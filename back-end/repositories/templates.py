from typing import List, Optional
from uuid import UUID

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from common.logger import log as L
from models.template import Template, TemplateCreate, TemplateUpdate


_COLUMNS = "id, name, structure_id, html_content, created_at, updated_at"


class TemplatesRepository:
    """Data-access layer for the templates table in Lakebase."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    async def get_all(self, structure_id: Optional[UUID] = None) -> List[Template]:
        connector = self._require_connector()
        if structure_id:
            result = await connector.execute_query(
                f"SELECT {_COLUMNS} FROM templates WHERE structure_id = :sid ORDER BY created_at",
                {"sid": str(structure_id)},
            )
        else:
            result = await connector.execute_query(
                f"SELECT {_COLUMNS} FROM templates ORDER BY created_at"
            )
        rows = result.fetchall()
        return [self._row_to_model(r) for r in rows]

    async def get_by_id(self, template_id: UUID) -> Optional[Template]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM templates WHERE id = :id",
            {"id": str(template_id)},
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def create(self, data: TemplateCreate) -> Template:
        result = await self._require_connector().execute_query(
            "INSERT INTO templates (name, structure_id, html_content) "
            "VALUES (:name, :structure_id, :html_content) "
            f"RETURNING {_COLUMNS}",
            {
                "name": data.name,
                "structure_id": str(data.structure_id),
                "html_content": data.html_content,
            },
        )
        row = result.fetchone()
        return self._row_to_model(row)

    async def update(self, template_id: UUID, data: TemplateUpdate) -> Optional[Template]:
        sets: list[str] = []
        params: dict = {"id": str(template_id)}

        if data.name is not None:
            sets.append("name = :name")
            params["name"] = data.name
        if data.structure_id is not None:
            sets.append("structure_id = :structure_id")
            params["structure_id"] = str(data.structure_id)
        if data.html_content is not None:
            sets.append("html_content = :html_content")
            params["html_content"] = data.html_content

        if not sets:
            return await self.get_by_id(template_id)

        sets.append("updated_at = NOW()")
        set_clause = ", ".join(sets)

        result = await self._require_connector().execute_query(
            f"UPDATE templates SET {set_clause} WHERE id = :id "
            f"RETURNING {_COLUMNS}",
            params,
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def delete(self, template_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "DELETE FROM templates WHERE id = :id",
            {"id": str(template_id)},
        )
        return result.rowcount > 0

    @staticmethod
    def _row_to_model(row) -> Template:
        return Template(
            id=row[0],
            name=row[1],
            structure_id=row[2],
            html_content=row[3],
            created_at=row[4],
            updated_at=row[5],
        )
