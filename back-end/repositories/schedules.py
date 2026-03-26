from typing import List, Optional
from uuid import UUID

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from common.logger import log as L
from models.schedule import ExecutionStatus, Schedule, ScheduleCreate, ScheduleExecution, ScheduleUpdate

_SCHEDULE_COLUMNS = (
    "id, name, project_id, structure_id, template_id, "
    "cron_expression, is_active, created_by, created_at, updated_at"
)

_EXECUTION_COLUMNS = (
    "id, schedule_id, status, started_at, completed_at, error_message, created_at"
)


class SchedulesRepository:
    """Data-access layer for the schedules and schedule_executions tables."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    # -- Schedules ----------------------------------------------------------------

    async def get_all_for_project(self, project_id: UUID) -> List[Schedule]:
        result = await self._require_connector().execute_query(
            f"SELECT {_SCHEDULE_COLUMNS} FROM schedules "
            "WHERE project_id = :pid ORDER BY created_at",
            {"pid": str(project_id)},
        )
        return [self._row_to_schedule(r) for r in result.fetchall()]

    async def get_all_active(self) -> List[Schedule]:
        result = await self._require_connector().execute_query(
            f"SELECT {_SCHEDULE_COLUMNS} FROM schedules WHERE is_active = TRUE ORDER BY created_at",
            {},
        )
        return [self._row_to_schedule(r) for r in result.fetchall()]

    async def get_by_id(self, schedule_id: UUID) -> Optional[Schedule]:
        result = await self._require_connector().execute_query(
            f"SELECT {_SCHEDULE_COLUMNS} FROM schedules WHERE id = :id",
            {"id": str(schedule_id)},
        )
        row = result.fetchone()
        return self._row_to_schedule(row) if row else None

    async def create(self, data: ScheduleCreate, user_email: str) -> Schedule:
        result = await self._require_connector().execute_query(
            "INSERT INTO schedules "
            "(name, project_id, structure_id, template_id, cron_expression, is_active, created_by) "
            "VALUES (:name, :project_id, :structure_id, :template_id, :cron_expression, :is_active, :created_by) "
            f"RETURNING {_SCHEDULE_COLUMNS}",
            {
                "name": data.name,
                "project_id": str(data.project_id),
                "structure_id": str(data.structure_id),
                "template_id": str(data.template_id),
                "cron_expression": data.cron_expression,
                "is_active": data.is_active,
                "created_by": user_email,
            },
        )
        return self._row_to_schedule(result.fetchone())

    async def update(self, schedule_id: UUID, data: ScheduleUpdate) -> Optional[Schedule]:
        sets: list[str] = []
        params: dict = {"id": str(schedule_id)}

        if data.name is not None:
            sets.append("name = :name")
            params["name"] = data.name
        if data.cron_expression is not None:
            sets.append("cron_expression = :cron_expression")
            params["cron_expression"] = data.cron_expression
        if data.is_active is not None:
            sets.append("is_active = :is_active")
            params["is_active"] = data.is_active

        if not sets:
            return await self.get_by_id(schedule_id)

        sets.append("updated_at = NOW()")
        set_clause = ", ".join(sets)

        where = "id = :id"
        if data.expected_updated_at is not None:
            where += " AND updated_at = :expected_updated_at"
            params["expected_updated_at"] = data.expected_updated_at

        result = await self._require_connector().execute_query(
            f"UPDATE schedules SET {set_clause} WHERE {where} RETURNING {_SCHEDULE_COLUMNS}",
            params,
        )
        row = result.fetchone()
        return self._row_to_schedule(row) if row else None

    async def delete(self, schedule_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "DELETE FROM schedules WHERE id = :id",
            {"id": str(schedule_id)},
        )
        return result.rowcount > 0

    # -- Executions ---------------------------------------------------------------

    async def get_executions(
        self, schedule_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[ScheduleExecution]:
        result = await self._require_connector().execute_query(
            f"SELECT {_EXECUTION_COLUMNS} FROM schedule_executions "
            "WHERE schedule_id = :sid ORDER BY created_at DESC LIMIT :lim OFFSET :off",
            {"sid": str(schedule_id), "lim": limit, "off": offset},
        )
        return [self._row_to_execution(r) for r in result.fetchall()]

    async def get_all_executions_for_project(
        self, project_id: UUID, limit: int = 200, offset: int = 0
    ) -> List[ScheduleExecution]:
        result = await self._require_connector().execute_query(
            "SELECT se.id, se.schedule_id, se.status, se.started_at, se.completed_at, "
            "se.error_message, se.created_at "
            "FROM schedule_executions se "
            "JOIN schedules s ON se.schedule_id = s.id "
            "WHERE s.project_id = :pid ORDER BY se.created_at DESC LIMIT :lim OFFSET :off",
            {"pid": str(project_id), "lim": limit, "off": offset},
        )
        return [self._row_to_execution(r) for r in result.fetchall()]

    async def create_execution(self, schedule_id: UUID) -> ScheduleExecution:
        result = await self._require_connector().execute_query(
            "INSERT INTO schedule_executions (schedule_id, status, started_at) "
            "VALUES (:sid, 'running', NOW()) "
            f"RETURNING {_EXECUTION_COLUMNS}",
            {"sid": str(schedule_id)},
        )
        return self._row_to_execution(result.fetchone())

    async def update_execution(
        self,
        execution_id: UUID,
        status: ExecutionStatus,
        error_message: Optional[str] = None,
    ) -> None:
        await self._require_connector().execute_query(
            "UPDATE schedule_executions "
            "SET status = :status, completed_at = NOW(), error_message = :error_message "
            "WHERE id = :id",
            {
                "id": str(execution_id),
                "status": status.value,
                "error_message": error_message,
            },
        )

    # -- Row mappers --------------------------------------------------------------

    @staticmethod
    def _row_to_schedule(row) -> Schedule:
        return Schedule(
            id=row[0],
            name=row[1],
            project_id=row[2],
            structure_id=row[3],
            template_id=row[4],
            cron_expression=row[5],
            is_active=row[6],
            created_by=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    @staticmethod
    def _row_to_execution(row) -> ScheduleExecution:
        return ScheduleExecution(
            id=row[0],
            schedule_id=row[1],
            status=row[2],
            started_at=row[3],
            completed_at=row[4],
            error_message=row[5],
            created_at=row[6],
        )
