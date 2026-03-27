from typing import List, Optional
from uuid import UUID, uuid4

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from models.smtp_connection import SmtpConnection, SmtpConnectionCreate, SmtpConnectionUpdate

_COLUMNS = (
    "id, name, provider, from_email, smtp_host, smtp_port, username, "
    "secret_scope, secret_key, created_by, created_at, updated_at"
)


class SmtpConnectionsRepository:
    """Data-access layer for the smtp_connections table."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    async def get_all(self) -> List[SmtpConnection]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM smtp_connections ORDER BY name",
            {},
        )
        return [self._row_to_model(r) for r in result.fetchall()]

    async def get_by_id(self, connection_id: UUID) -> Optional[SmtpConnection]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM smtp_connections WHERE id = :id",
            {"id": str(connection_id)},
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def create(
        self,
        data: SmtpConnectionCreate,
        user_email: str,
        secret_scope: str,
        secret_key: str,
        connection_id: Optional[UUID] = None,
    ) -> SmtpConnection:
        result = await self._require_connector().execute_query(
            "INSERT INTO smtp_connections "
            "(id, name, provider, from_email, smtp_host, smtp_port, username, "
            "secret_scope, secret_key, created_by) "
            "VALUES (:id, :name, :provider, :from_email, :smtp_host, :smtp_port, :username, "
            ":secret_scope, :secret_key, :created_by) "
            f"RETURNING {_COLUMNS}",
            {
                "id": str(connection_id or uuid4()),
                "name": data.name,
                "provider": data.provider,
                "from_email": str(data.from_email),
                "smtp_host": data.smtp_host,
                "smtp_port": data.smtp_port,
                "username": data.username,
                "secret_scope": secret_scope,
                "secret_key": secret_key,
                "created_by": user_email,
            },
        )
        return self._row_to_model(result.fetchone())

    async def update(self, connection_id: UUID, data: SmtpConnectionUpdate) -> Optional[SmtpConnection]:
        sets: list[str] = []
        params: dict = {"id": str(connection_id)}

        if data.name is not None:
            sets.append("name = :name")
            params["name"] = data.name
        if data.from_email is not None:
            sets.append("from_email = :from_email")
            params["from_email"] = str(data.from_email)
        if data.smtp_host is not None:
            sets.append("smtp_host = :smtp_host")
            params["smtp_host"] = data.smtp_host
        if data.smtp_port is not None:
            sets.append("smtp_port = :smtp_port")
            params["smtp_port"] = data.smtp_port
        if data.username is not None:
            sets.append("username = :username")
            params["username"] = data.username

        if not sets:
            return await self.get_by_id(connection_id)

        sets.append("updated_at = NOW()")
        result = await self._require_connector().execute_query(
            f"UPDATE smtp_connections SET {', '.join(sets)} WHERE id = :id RETURNING {_COLUMNS}",
            params,
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def delete(self, connection_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "DELETE FROM smtp_connections WHERE id = :id",
            {"id": str(connection_id)},
        )
        return result.rowcount > 0

    async def has_active_send_lists(self, connection_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "SELECT COUNT(*) FROM email_send_lists WHERE smtp_connection_id = :id",
            {"id": str(connection_id)},
        )
        count = result.scalar()
        return (count or 0) > 0

    @staticmethod
    def _row_to_model(row) -> SmtpConnection:
        return SmtpConnection(
            id=row[0],
            name=row[1],
            provider=row[2],
            from_email=row[3],
            smtp_host=row[4],
            smtp_port=row[5],
            username=row[6],
            secret_scope=row[7],
            secret_key=row[8],
            created_by=row[9],
            created_at=row[10],
            updated_at=row[11],
        )
