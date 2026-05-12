import asyncio
import os
import uuid as _uuid
from typing import Dict, List, Tuple
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
from common.email.factory import get_provider
from common.exceptions import db_op
from common.factories.scheduler import scheduler_factory
from common.logger import log as L
from models.schedule import ExecutionStatus, Schedule, ScheduleCreate, ScheduleExecution, ScheduleUpdate
from repositories.email_send_lists import EmailSendListsRepository
from repositories.schedules import SchedulesRepository
from repositories.smtp_connections import SmtpConnectionsRepository
from services.report_renderer import (
    build_email_html_document,
    build_pdf_html_document,
    collect_images_for_email,
    html_to_pdf_bytes,
    inline_images,
    render_charts_as_svg,
    render_charts_for_pdf,
    render_report,
)

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


async def _send_to_one_list(
    schedule: Schedule,
    send_list,
    smtp_conn,
    html_body: str | None = None,
    cid_images: Dict[str, Tuple[str, bytes]] | None = None,
    pdf_bytes: bytes | None = None,
    filename: str | None = None,
) -> tuple[str, bool]:
    """Send to a single list. Returns (message, has_error).

    Exactly one of pdf_bytes or html_body must be provided.
    """
    assert (pdf_bytes is None) != (html_body is None), (
        "_send_to_one_list requires exactly one of pdf_bytes or html_body"
    )
    try:
        provider = get_provider(smtp_conn)
        subject = f"Scheduled Report: {schedule.name}"
        if pdf_bytes is not None:
            await provider.send_attachment(
                from_email=smtp_conn.from_email,
                recipients=send_list.emails,
                subject=subject,
                pdf_bytes=pdf_bytes,
                filename=filename or f"{schedule.name}.pdf",
            )
        else:
            await provider.send_html(
                from_email=smtp_conn.from_email,
                recipients=send_list.emails,
                subject=subject,
                html_body=html_body or "",
                cid_images=cid_images or None,
            )
        return f"Emails sent: {send_list.name} ({len(send_list.emails)} recipient(s))", False
    except Exception as e:
        L.error(f"[Scheduler] Email failed for send list {send_list.name}: {e}")
        return f"Email failed: {send_list.name} — {e}", True


async def _send_to_lists(
    schedule: Schedule,
    send_lists_repo: EmailSendListsRepository,
    smtp_repo: SmtpConnectionsRepository,
    html_body: str | None = None,
    cid_images: Dict[str, Tuple[str, bytes]] | None = None,
    pdf_bytes: bytes | None = None,
    filename: str | None = None,
) -> tuple[str, bool]:
    """Send the rendered report to all attached send lists.

    Pass html_body for inline HTML delivery or pdf_bytes+filename for PDF attachment.
    Returns a tuple of (summary_message, has_failures).
    """
    if not schedule.send_list_ids:
        return "", False

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
        message, error = await _send_to_one_list(
            schedule, sl, conn,
            html_body=html_body, cid_images=cid_images,
            pdf_bytes=pdf_bytes, filename=filename,
        )
        lines.append(message)
        if error:
            has_failures = True

    return "\n".join(lines), has_failures


async def _execute_report(
    execution_id: UUID,
    schedule: Schedule,
    repo: SchedulesRepository,
    send_lists_repo: EmailSendListsRepository,
    smtp_repo: SmtpConnectionsRepository,
) -> None:
    """Core report execution logic — called inside a timeout wrapper."""
    if not schedule.send_list_ids:
        # PDF rendering is expensive; skip the whole pipeline when there's nowhere to send.
        await repo.update_execution(
            execution_id, ExecutionStatus.success, error_message="No send lists configured",
        )
        L.info(f"[Scheduler] Execution {execution_id} skipped — no send lists configured")
        return

    html_body, template = await render_report(schedule.template_id)
    is_markdown = template.template_type == "markdown"

    if template.page_size == "A4":
        body = await asyncio.to_thread(render_charts_for_pdf, html_body or "")
        body = await inline_images(body, pdf_mode=True)
        full_html = build_pdf_html_document(body, template.name, is_markdown=is_markdown)
        pdf_bytes = await asyncio.to_thread(html_to_pdf_bytes, full_html)
        email_summary, email_failures = await _send_to_lists(
            schedule, send_lists_repo, smtp_repo,
            pdf_bytes=pdf_bytes, filename=f"{template.name}.pdf",
        )
    else:
        body = await asyncio.to_thread(render_charts_as_svg, html_body or "")
        body, cid_images = await collect_images_for_email(body)
        full_html = build_email_html_document(body, template.name, is_markdown=is_markdown)
        email_summary, email_failures = await _send_to_lists(
            schedule, send_lists_repo, smtp_repo,
            html_body=full_html, cid_images=cid_images,
        )

    status = ExecutionStatus.failed if email_failures else ExecutionStatus.success
    await repo.update_execution(execution_id, status, error_message=email_summary or None)
    L.info(f"[Scheduler] Execution {execution_id} {'succeeded' if not email_failures else 'completed with email failures'}")


async def _run_scheduled_report(schedule_id: UUID) -> None:
    """APScheduler job function. Repos are instantiated directly — Depends() is unavailable outside a request context."""
    repo = SchedulesRepository()
    schedule = await repo.get_by_id(schedule_id)
    if not schedule or not schedule.is_active:
        return

    execution = await repo.create_execution(schedule_id)
    L.info(f"[Scheduler] Running schedule {schedule_id} (execution {execution.id})")

    send_lists_repo = EmailSendListsRepository()
    smtp_repo = SmtpConnectionsRepository()

    timeout = int(os.getenv("SCHEDULE_JOB_TIMEOUT_SECONDS", "300"))
    try:
        await asyncio.wait_for(
            _execute_report(execution.id, schedule, repo, send_lists_repo, smtp_repo),
            timeout=timeout,
        )
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
    async with db_op("list schedules"):
        return await repo.get_all_for_project(project_id)


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
    async with db_op("list all executions"):
        return await repo.get_all_executions_for_project(project_id, limit=limit, offset=offset)


@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(
    schedule_id: UUID,
    email: CurrentUser,
    repo: SchedulesRepo,
    projects_repo: ProjectsRepo,
):
    await check_schedule_project_access(schedule_id, email, repo, projects_repo)
    async with db_op("get schedule"):
        schedule = await repo.get_by_id(schedule_id)
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
    async with db_op("create schedule"):
        schedule = await repo.create(body, email)

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
    async with db_op("update schedule"):
        schedule = await repo.update(schedule_id, body)

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
    async with db_op("delete schedule"):
        deleted = await repo.delete(schedule_id)
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
    async with db_op("list executions"):
        return await repo.get_executions(schedule_id, limit=limit, offset=offset)


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
