"""
Service for discovering Unity Catalog assets (catalogs, schemas, tables, columns).

Uses the Databricks SDK via WorkspaceConnector to browse the UC metastore
and map table column types to structure field types. Complex types such as
ARRAY<STRUCT<...>> and STRUCT<...> are parsed recursively from the `type_text`
field returned by the SDK so that nested shapes are preserved.
"""

import asyncio
import re
from typing import Any, Dict, List, Optional

from common.connectors.workspace import WorkspaceConnector
from common.logger import log as L
from models.structure import StructureField

_UC_SCALAR_TYPE_MAP: Dict[str, str] = {
    "STRING": "string",
    "VARCHAR": "string",
    "CHAR": "string",
    "BINARY": "string",
    "INT": "number",
    "INTEGER": "number",
    "SMALLINT": "number",
    "TINYINT": "number",
    "BIGINT": "number",
    "LONG": "number",
    "FLOAT": "number",
    "DOUBLE": "number",
    "DECIMAL": "number",
    "BOOLEAN": "boolean",
    "DATE": "date",
    "TIMESTAMP": "date",
    "TIMESTAMP_NTZ": "date",
}


class DiscoveryService:
    """Browse Unity Catalog assets and convert table schemas to structure fields."""

    def __init__(self, workspace_connector: Optional[WorkspaceConnector] = None, token: Optional[str] = None):
        self.workspace = workspace_connector or (WorkspaceConnector(bearer=token) if token else WorkspaceConnector())
        self.client = self.workspace.client

    async def list_catalogs(self) -> List[Dict[str, Any]]:
        catalogs = await asyncio.to_thread(lambda: list(self.client.catalogs.list()))
        return [
            {
                "name": c.name,
                "comment": getattr(c, "comment", None),
                "owner": getattr(c, "owner", None),
            }
            for c in catalogs
        ]

    async def list_schemas(self, catalog_name: str) -> List[Dict[str, Any]]:
        schemas = await asyncio.to_thread(
            lambda: list(self.client.schemas.list(catalog_name=catalog_name))
        )
        return [
            {
                "name": s.name,
                "catalog_name": catalog_name,
                "comment": getattr(s, "comment", None),
            }
            for s in schemas
        ]

    async def list_tables(self, catalog_name: str, schema_name: str) -> List[Dict[str, Any]]:
        tables = await asyncio.to_thread(
            lambda: list(
                self.client.tables.list(
                    catalog_name=catalog_name, schema_name=schema_name
                )
            )
        )
        return [
            {
                "name": t.name,
                "full_name": t.full_name,
                "table_type": str(getattr(t, "table_type", "")),
                "comment": getattr(t, "comment", None),
            }
            for t in tables
        ]

    async def get_table_columns(
        self, catalog_name: str, schema_name: str, table_name: str
    ) -> List[Dict[str, Any]]:
        full_name = f"{catalog_name}.{schema_name}.{table_name}"
        table_info = await asyncio.to_thread(self.client.tables.get, full_name)
        columns = getattr(table_info, "columns", None) or []
        return [
            {
                "name": col.name,
                "type_name": str(getattr(col, "type_name", "STRING")),
                "type_text": getattr(col, "type_text", None) or str(getattr(col, "type_name", "STRING")),
                "comment": getattr(col, "comment", None),
                "position": getattr(col, "position", idx),
                "nullable": getattr(col, "nullable", True),
            }
            for idx, col in enumerate(columns)
        ]

    def columns_to_structure_fields(
        self, columns: List[Dict[str, Any]]
    ) -> List[StructureField]:
        """Map UC column definitions to StructureField objects.

        Uses type_text (e.g. "array<struct<name:string,amount:double>>") when
        available so that ARRAY and STRUCT columns produce nested children.
        Falls back to type_name for simple scalars.
        """
        return [
            _parse_type_to_field(col["name"], col.get("type_text") or col.get("type_name", "string"))
            for col in columns
        ]


def _parse_type_to_field(name: str, type_text: str) -> StructureField:
    """Recursively parse a Databricks type_text string into a StructureField."""
    normalized = type_text.strip().lower()

    if normalized.startswith("array<") and normalized.endswith(">"):
        inner = normalized[6:-1]
        if inner.startswith("struct<") and inner.endswith(">"):
            children = _parse_struct_fields(inner[7:-1])
            return StructureField(name=name, type="array", children=children)
        return StructureField(name=name, type="array")

    if normalized.startswith("struct<") and normalized.endswith(">"):
        children = _parse_struct_fields(normalized[7:-1])
        return StructureField(name=name, type="object", children=children)

    if normalized.startswith("map<"):
        return StructureField(name=name, type="object")

    scalar = _UC_SCALAR_TYPE_MAP.get(normalized.upper().split("(")[0], "string")
    return StructureField(name=name, type=scalar)


def _parse_struct_fields(fields_str: str) -> List[StructureField]:
    """
    Parse the interior of a struct definition into StructureField children.

    Example input: "name:string,amount:double,tags:array<string>"
    Handles nested angle brackets correctly by tracking depth.
    """
    parts = _split_top_level(fields_str)
    children: List[StructureField] = []
    for part in parts:
        part = part.strip()
        colon = part.find(":")
        if colon == -1:
            continue
        field_name = part[:colon].strip()
        field_type = part[colon + 1:].strip()
        children.append(_parse_type_to_field(field_name, field_type))
    return children


def _split_top_level(s: str) -> List[str]:
    """Split a comma-separated string while ignoring commas inside angle brackets."""
    parts: List[str] = []
    depth = 0
    current: List[str] = []
    for ch in s:
        if ch == "<":
            depth += 1
            current.append(ch)
        elif ch == ">":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts
