import asyncio
import os
import uuid as _uuid
from typing import List, Optional
from uuid import UUID

from apscheduler.jobstores.base import JobLookupError
from fastapi import APIRouter, HTTPException, Query

from common.authorization import (
    CurrentUser,
    ProjectsRepo,
    SchedulesRepo,
    check_project_access,
    check_project_access_and_not_locked,
    check_schedule_project_access,
)
from common.factories.scheduler import scheduler_factory
from common.logger import log as L
from models.schedule import ExecutionStatus, Schedule, ScheduleCreate, ScheduleExecution, ScheduleUpdate
from repositories.schedules import SchedulesRepository
from services.report_renderer import build_html_document, render_charts_as_svg, render_report, render_report_pdf

router = APIRouter(prefix="/schedules", tags=["schedules"])

_scheduler = scheduler_factory.scheduler


def _parse_cron(expression: str) -> dict:
    """Convert a 5-field cron string to APScheduler cron kwargs."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have exactly 5 fields: minute hour day month day_of_week")
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }


def _register_job(schedule: Schedule) -> None:
    """Register or replace an APScheduler cron job for the given schedule."""
    job_id = str(schedule.id)
    # Remove existing job if present (handles update case)
    try:
        _scheduler.remove_job(job_id)
    except JobLookupError:
        pass

    if not schedule.is_active:
        return

    try:
        cron_kwargs = _parse_cron(schedule.cron_expression)
    except ValueError as e:
        L.error(f"[Scheduler] Invalid cron for schedule {job_id}: {e}")
        return

    _scheduler.add_job(
        _run_scheduled_report,
        "cron",
        id=job_id,
        replace_existing=True,
        args=[schedule.id],
        **cron_kwargs,
    )
    L.info(f"[Scheduler] Registered job {job_id} ({schedule.cron_expression})")


def _remove_job(schedule_id: UUID) -> None:
    try:
        _scheduler.remove_job(str(schedule_id))
        L.info(f"[Scheduler] Removed job {schedule_id}")
    except JobLookupError:
        pass


async def _send_to_lists(
    schedule: Schedule, html_body: str, pdf_bytes: Optional[bytes] = None
) -> tuple[str, bool]:
    """Send the rendered report to all attached send lists.

    If pdf_bytes is provided the report is delivered as a PDF attachment;
    otherwise the rendered HTML is sent inline.

    Returns a tuple of (summary_message, has_failures).
    """
    if not schedule.send_list_ids:
        return "", False

    from repositories.email_send_lists import EmailSendListsRepository
    from repositories.smtp_connections import SmtpConnectionsRepository
    from common.email.sender import send_report_email, send_report_email_with_attachment

    send_lists_repo = EmailSendListsRepository()
    smtp_repo = SmtpConnectionsRepository()
    send_lists = await send_lists_repo.get_by_ids(schedule.send_list_ids)

    lines: list[str] = []
    has_failures = False
    for sl in send_lists:
        if not sl.emails:
            continue
        conn = await smtp_repo.get_by_id(sl.smtp_connection_id)
        if not conn:
            has_failures = True
            lines.append(f"Email failed: {sl.name} — connection not found")
            continue
        try:
            if pdf_bytes is not None:
                await send_report_email_with_attachment(
                    provider=conn.provider,
                    smtp_host=conn.smtp_host,
                    smtp_port=conn.smtp_port,
                    username=conn.username,
                    secret_scope=conn.secret_scope,
                    secret_key=conn.secret_key,
                    from_email=conn.from_email,
                    recipients=sl.emails,
                    subject=f"Scheduled Report: {schedule.name}",
                    pdf_bytes=pdf_bytes,
                    filename=f"{schedule.name}.pdf",
                )
            else:
                await send_report_email(
                    provider=conn.provider,
                    smtp_host=conn.smtp_host,
                    smtp_port=conn.smtp_port,
                    username=conn.username,
                    secret_scope=conn.secret_scope,
                    secret_key=conn.secret_key,
                    from_email=conn.from_email,
                    recipients=sl.emails,
                    subject=f"Scheduled Report: {schedule.name}",
                    html_body=html_body,
                )
            lines.append(f"Emails sent: {sl.name} ({len(sl.emails)} recipient(s))")
        except Exception as e:
            has_failures = True
            L.error(f"[Scheduler] Email failed for send list {sl.name}: {e}")
            lines.append(f"Email failed: {sl.name} — {e}")

    return "\n".join(lines), has_failures


async def _execute_report(execution_id: UUID, schedule: Schedule, repo: SchedulesRepository) -> None:
    """Core report execution logic — called inside a timeout wrapper."""
    html_body, template = await render_report(schedule.template_id)
    if template.page_size == "email":
        is_markdown = template.template_type == "markdown"
        body = html_body or ""
        if not is_markdown:
            body = render_charts_as_svg(body)
        full_html = build_html_document(body, template.name, include_charts=False, is_markdown=is_markdown)
        email_summary, email_failures = await _send_to_lists(schedule, full_html)
    else:
        pdf_bytes, _ = await render_report_pdf(schedule.template_id)
        email_summary, email_failures = await _send_to_lists(schedule, html_body or "", pdf_bytes=pdf_bytes)

    status = ExecutionStatus.failed if email_failures else ExecutionStatus.success
    await repo.update_execution(execution_id, status, error_message=email_summary or None)
    L.info(f"[Scheduler] Execution {execution_id} {'succeeded' if not email_failures else 'completed with email failures'}")


async def _run_scheduled_report(schedule_id: UUID) -> None:
    """APScheduler job function."""
    repo = SchedulesRepository()
    schedule = await repo.get_by_id(schedule_id)
    if not schedule or not schedule.is_active:
        return

    execution = await repo.create_execution(schedule_id)
    L.info(f"[Scheduler] Running schedule {schedule_id} (execution {execution.id})")

    timeout = int(os.getenv("SCHEDULE_JOB_TIMEOUT_SECONDS", "300"))
    try:
        await asyncio.wait_for(_execute_report(execution.id, schedule, repo), timeout=timeout)
    except asyncio.TimeoutError:
        L.error(f"[Scheduler] Execution {execution.id} timed out after {timeout}s")
        await repo.update_execution(
            execution.id, ExecutionStatus.failed,
            error_message=f"Execution timed out after {timeout}s",
        )
    except Exception as e:
        err = str(e)
        L.error(f"[Scheduler] Execution {execution.id} failed: {err}")
        await repo.update_execution(execution.id, ExecutionStatus.failed, error_message=err)


# -- Routes -------------------------------------------------------------------

@router.get("/", response_model=List[Schedule])
async def list_schedules(
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
    project_id: UUID = Query(...),
):
    await check_project_access(project_id, email, projects_repo)
    try:
        return await repo.get_all_for_project(project_id)
    except RuntimeError:
        L.exception("Failed to list schedules")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/executions", response_model=List[ScheduleExecution])
async def list_all_executions(
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
    project_id: UUID = Query(...),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """All executions across every schedule in a project, newest first."""
    await check_project_access(project_id, email, projects_repo)
    try:
        return await repo.get_all_executions_for_project(project_id, limit=limit, offset=offset)
    except RuntimeError:
        L.exception("Failed to list all executions")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(
    schedule_id: UUID,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
):
    await check_schedule_project_access(schedule_id, email, repo, projects_repo)
    try:
        schedule = await repo.get_by_id(schedule_id)
    except RuntimeError:
        L.exception("Failed to get schedule")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/", response_model=Schedule, status_code=201)
async def create_schedule(
    body: ScheduleCreate,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
):
    # Validate cron before writing to DB
    try:
        _parse_cron(body.cron_expression)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    await check_project_access_and_not_locked(body.project_id, email, projects_repo)
    try:
        schedule = await repo.create(body, email)
    except RuntimeError:
        L.exception("Failed to create schedule")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    _register_job(schedule)
    return schedule


@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(
    schedule_id: UUID,
    body: ScheduleUpdate,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
):
    if body.cron_expression is not None:
        try:
            _parse_cron(body.cron_expression)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    await check_schedule_project_access(schedule_id, email, repo, projects_repo)
    try:
        schedule = await repo.update(schedule_id, body)
    except RuntimeError:
        L.exception("Failed to update schedule")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    if not schedule:
        if body.expected_updated_at is not None:
            exists = await repo.get_by_id(schedule_id)
            if exists:
                raise HTTPException(
                    status_code=409,
                    detail="Schedule was modified by another user. Reload to see the latest version.",
                )
        raise HTTPException(status_code=404, detail="Schedule not found")

    _register_job(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
):
    await check_schedule_project_access(schedule_id, email, repo, projects_repo)
    try:
        deleted = await repo.delete(schedule_id)
    except RuntimeError:
        L.exception("Failed to delete schedule")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")
    _remove_job(schedule_id)


@router.get("/{schedule_id}/executions", response_model=List[ScheduleExecution])
async def list_executions(
    schedule_id: UUID,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    await check_schedule_project_access(schedule_id, email, repo, projects_repo)
    try:
        return await repo.get_executions(schedule_id, limit=limit, offset=offset)
    except RuntimeError:
        L.exception("Failed to list executions")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@router.post("/{schedule_id}/trigger", status_code=202)
async def trigger_schedule(
    schedule_id: UUID,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
):
    """Manually trigger a schedule execution immediately (write-guarded)."""
    await check_schedule_project_access(schedule_id, email, repo, projects_repo)
    schedule = await repo.get_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    _scheduler.add_job(
        _run_scheduled_report,
        "date",
        args=[schedule_id],
        id=f"manual_{_uuid.uuid4().hex}",
    )
    return {"detail": "Execution triggered"}
