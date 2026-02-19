import json
from typing import List, Optional
from uuid import UUID

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from models.structure import Structure, StructureCreate, StructureUpdate


_COLUMNS = (
    "id, name, project_id, fields, tables, relationships, selected_columns, sql_query, "
    "created_at, updated_at"
)


class StructuresRepository:
    """Data-access layer for the structures table in Lakebase."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    async def get_by_project_id(self, project_id: UUID) -> List[Structure]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM structures WHERE project_id = :pid ORDER BY created_at",
            {"pid": str(project_id)},
        )
        rows = result.fetchall()
        return [self._row_to_model(r) for r in rows]

    async def get_by_id(self, structure_id: UUID) -> Optional[Structure]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM structures WHERE id = :id",
            {"id": str(structure_id)},
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def create(self, data: StructureCreate) -> Structure:
        fields_json = json.dumps([f.model_dump() for f in data.fields])
        tables_json = json.dumps([t.model_dump() for t in data.tables])
        selected_columns_json = json.dumps(data.selected_columns)
        result = await self._require_connector().execute_query(
            "INSERT INTO structures (name, project_id, fields, tables, selected_columns) "
            "VALUES (:name, :project_id, CAST(:fields AS jsonb), CAST(:tables AS jsonb), "
            "CAST(:selected_columns AS jsonb)) "
            f"RETURNING {_COLUMNS}",
            {
                "name": data.name,
                "project_id": str(data.project_id),
                "fields": fields_json,
                "tables": tables_json,
                "selected_columns": selected_columns_json,
            },
        )
        row = result.fetchone()
        return self._row_to_model(row)

    async def update(self, structure_id: UUID, data: StructureUpdate) -> Optional[Structure]:
        sets: list[str] = []
        params: dict = {"id": str(structure_id)}

        if data.name is not None:
            sets.append("name = :name")
            params["name"] = data.name
        if data.fields is not None:
            sets.append("fields = CAST(:fields AS jsonb)")
            params["fields"] = json.dumps([f.model_dump() for f in data.fields])
        if data.tables is not None:
            sets.append("tables = CAST(:tables AS jsonb)")
            params["tables"] = json.dumps([t.model_dump() for t in data.tables])
        if data.selected_columns is not None:
            sets.append("selected_columns = CAST(:selected_columns AS jsonb)")
            params["selected_columns"] = json.dumps(data.selected_columns)

        if not sets:
            return await self.get_by_id(structure_id)

        sets.append("updated_at = NOW()")
        set_clause = ", ".join(sets)

        result = await self._require_connector().execute_query(
            f"UPDATE structures SET {set_clause} WHERE id = :id "
            f"RETURNING {_COLUMNS}",
            params,
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def update_built(
        self,
        structure_id: UUID,
        sql_query: str,
        fields: list,
    ) -> Optional[Structure]:
        """Persist the auto-generated query and inferred fields after a build."""
        fields_json = json.dumps([f.model_dump() for f in fields])
        result = await self._require_connector().execute_query(
            "UPDATE structures SET sql_query = :sql_query, "
            "fields = CAST(:fields AS jsonb), updated_at = NOW() "
            f"WHERE id = :id RETURNING {_COLUMNS}",
            {
                "id": str(structure_id),
                "sql_query": sql_query,
                "fields": fields_json,
            },
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def delete(self, structure_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "DELETE FROM structures WHERE id = :id",
            {"id": str(structure_id)},
        )
        return result.rowcount > 0

    @staticmethod
    def _row_to_model(row) -> Structure:
        def _parse_json(raw):
            if isinstance(raw, str):
                return json.loads(raw)
            return raw if raw is not None else []

        # Column order: id, name, project_id, fields, tables, relationships,
        #               selected_columns, sql_query, created_at, updated_at
        return Structure(
            id=row[0],
            name=row[1],
            project_id=row[2],
            fields=_parse_json(row[3]),
            tables=_parse_json(row[4]),
            relationships=_parse_json(row[5]),
            selected_columns=_parse_json(row[6]),
            sql_query=row[7],
            created_at=row[8],
            updated_at=row[9],
        )
