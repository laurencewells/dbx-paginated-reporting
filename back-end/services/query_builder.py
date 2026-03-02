"""
Build SQL queries and infer structure fields from a single Unity Catalog table.

One table (or view) is selected per structure along with a list of chosen
columns. The SQL is a plain SELECT of those columns from the table — no JOINs,
no relationships. ARRAY<STRUCT<...>> columns are parsed via DiscoveryService
so that the StructureField tree reflects the native nested shape returned by
the Databricks Arrow-serialised result set.
"""

from typing import List, Optional

from common.connectors.workspace import WorkspaceConnector
from common.logger import log as L
from models.structure import StructureField, StructureTable
from services.discovery import DiscoveryService


class QueryBuilderService:
    """Generate SQL and infer nested fields from a single UC table + column list."""

    def __init__(self, workspace_connector: Optional[WorkspaceConnector] = None, token: Optional[str] = None):
        self.discovery = DiscoveryService(workspace_connector, token=token)

    def build_query(self, table: StructureTable, selected_columns: List[str]) -> str:
        """Return a SELECT of the chosen columns from the table."""
        if not selected_columns:
            raise ValueError("At least one column must be selected")
        cols = ", ".join(selected_columns)
        return f"SELECT {cols} FROM {table.full_name}"

    async def infer_fields(
        self, table: StructureTable, selected_columns: List[str]
    ) -> List[StructureField]:
        """
        Fetch column metadata from UC, filter to selected_columns, and build
        a nested StructureField tree using type_text parsing.
        """
        parts = table.full_name.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid table name '{table.full_name}', expected catalog.schema.table"
            )

        all_columns = await self.discovery.get_table_columns(parts[0], parts[1], parts[2])
        selected_set = set(selected_columns)
        chosen = [c for c in all_columns if c["name"] in selected_set]

        # Preserve the order the user selected columns in
        order = {name: idx for idx, name in enumerate(selected_columns)}
        chosen.sort(key=lambda c: order.get(c["name"], 9999))

        return self.discovery.columns_to_structure_fields(chosen)
