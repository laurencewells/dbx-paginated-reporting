import json
from typing import List, Optional
from uuid import UUID

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from models.email_send_list import EmailSendList, EmailSendListCreate, EmailSendListUpdate

_COLUMNS = (
    "id, name, project_id, smtp_connection_id, emails, created_by, created_at, updated_at"
)


class EmailSendListsRepository:
    """Data-access layer for the email_send_lists table."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    async def get_all_for_project(self, project_id: UUID) -> List[EmailSendList]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM email_send_lists WHERE project_id = :pid ORDER BY name",
            {"pid": str(project_id)},
        )
        return [self._row_to_model(r) for r in result.fetchall()]

    async def get_by_id(self, send_list_id: UUID) -> Optional[EmailSendList]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM email_send_lists WHERE id = :id",
            {"id": str(send_list_id)},
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def get_by_ids(self, send_list_ids: List[UUID]) -> List[EmailSendList]:
        if not send_list_ids:
            return []
        placeholders = ", ".join(f":id_{i}" for i in range(len(send_list_ids)))
        params = {f"id_{i}": str(sid) for i, sid in enumerate(send_list_ids)}
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM email_send_lists WHERE id IN ({placeholders})",
            params,
        )
        return [self._row_to_model(r) for r in result.fetchall()]

    async def create(self, data: EmailSendListCreate, user_email: str) -> EmailSendList:
        emails_json = json.dumps([str(e) for e in data.emails])
        result = await self._require_connector().execute_query(
            "INSERT INTO email_send_lists "
            "(name, project_id, smtp_connection_id, emails, created_by) "
            "VALUES (:name, :project_id, :smtp_connection_id, CAST(:emails AS jsonb), :created_by) "
            f"RETURNING {_COLUMNS}",
            {
                "name": data.name,
                "project_id": str(data.project_id),
                "smtp_connection_id": str(data.smtp_connection_id),
                "emails": emails_json,
                "created_by": user_email,
            },
        )
        return self._row_to_model(result.fetchone())

    async def update(self, send_list_id: UUID, data: EmailSendListUpdate) -> Optional[EmailSendList]:
        sets: list[str] = []
        params: dict = {"id": str(send_list_id)}

        if data.name is not None:
            sets.append("name = :name")
            params["name"] = data.name
        if data.smtp_connection_id is not None:
            sets.append("smtp_connection_id = :smtp_connection_id")
            params["smtp_connection_id"] = str(data.smtp_connection_id)
        if data.emails is not None:
            sets.append("emails = CAST(:emails AS jsonb)")
            params["emails"] = json.dumps([str(e) for e in data.emails])

        if not sets:
            return await self.get_by_id(send_list_id)

        sets.append("updated_at = NOW()")
        result = await self._require_connector().execute_query(
            f"UPDATE email_send_lists SET {', '.join(sets)} WHERE id = :id RETURNING {_COLUMNS}",
            params,
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def delete(self, send_list_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "DELETE FROM email_send_lists WHERE id = :id",
            {"id": str(send_list_id)},
        )
        return result.rowcount > 0

    @staticmethod
    def _row_to_model(row) -> EmailSendList:
        emails = row[4]
        if isinstance(emails, str):
            emails = json.loads(emails)
        return EmailSendList(
            id=row[0],
            name=row[1],
            project_id=row[2],
            smtp_connection_id=row[3],
            emails=emails or [],
            created_by=row[5],
            created_at=row[6],
            updated_at=row[7],
        )
