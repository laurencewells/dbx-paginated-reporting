"""
Service for querying real data from Unity Catalog tables linked to structures.

Uses the SQL query stored on the Structure (auto-generated from a single table
and selected columns) and executes it via SQLConnector against a Databricks
SQL warehouse. ARRAY<STRUCT<...>> columns are returned as native Python lists
by the Arrow deserialiser, so no flat-to-nested mapping is needed.
"""

from typing import Any, Dict, List, Optional

import numpy as np

from common.connectors.sql import SQLConnector
from common.factories.cache import app_cache
from common.logger import log as L
from models.structure import Structure
from repositories.structures import StructuresRepository
from repositories.templates import TemplatesRepository

PREVIEW_CACHE_TTL = 600  # 10 minutes
MAX_QUERY_LIMIT = 10_000  # hard cap — prevents runaway result sets


class DataQueryService:
    """Execute data queries for template preview and final report rendering."""

    def __init__(self, sql_connector: Optional[SQLConnector] = None, token: Optional[str] = None):
        self.sql_connector = sql_connector or SQLConnector(bearer=token)
        self.structures_repo = StructuresRepository()
        self.templates_repo = TemplatesRepository()

    @app_cache.cached("preview:{template_id}:{limit}", ttl=PREVIEW_CACHE_TTL)
    async def execute_for_preview(
        self, template_id, limit: int = 50
    ) -> Dict[str, Any]:
        limit = min(limit, MAX_QUERY_LIMIT)
        template = await self.templates_repo.get_by_id(template_id)
        if not template:
            raise ValueError("Template not found")

        structure = await self.structures_repo.get_by_id(template.structure_id)
        if not structure:
            raise ValueError("Linked structure not found")

        if not structure.sql_query:
            return {"data": {}, "query": None, "row_count": 0}

        limited_query = f"SELECT * FROM ({structure.sql_query}) _q LIMIT {limit}"
        rows, columns = await self._run_query(limited_query)
        data = self._map_results_to_data(columns, rows, structure)

        return {"data": data, "query": structure.sql_query, "row_count": len(rows)}

    async def _run_query(self, query: str):
        """Execute SQL via the Databricks SQL warehouse connector.

        Returns a list of row-dicts and a list of column names.
        The SQLConnector returns a pandas DataFrame, so we convert here.
        """
        L.info(f"[DataQueryService] Executing: {query[:120]}...")
        df = await self.sql_connector.run_sql_statement_async(query)

        if df is None:
            L.warning("[DataQueryService] SQL connector returned None — possible silent failure for query: %s", query[:120])
            raise RuntimeError("Query returned no result from the SQL connector")

        if df.empty:
            return [], []

        columns = list(df.columns)
        def _convert(val):
            if isinstance(val, np.ndarray):
                return [_convert(v) for v in val.tolist()]
            if isinstance(val, np.integer):
                return int(val)
            if isinstance(val, np.floating):
                return float(val)
            if isinstance(val, np.bool_):
                return bool(val)
            if isinstance(val, list):
                return [_convert(v) for v in val]
            if isinstance(val, dict):
                return {k: _convert(v) for k, v in val.items()}
            if hasattr(val, 'isoformat'):
                return val.isoformat()
            return val

        rows = [
            {k: _convert(v) for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]
        return rows, columns

    def _map_results_to_data(
        self, columns: List[str], rows: List[Dict[str, Any]], structure: Structure
    ) -> Dict[str, Any]:
        """
        Build the template data context from query rows.

        Each row is enriched with `_index` (1-based) and `_total` so templates
        can reference record position. ARRAY columns are already native Python
        lists courtesy of Databricks Arrow serialisation — no further mapping
        is required.
        """
        # _first exposes the first row's scalar values at the top level so templates
        # can reference scalar aggregates (e.g. {{#_first}}{{report_date}}{{/_first}})
        # without iterating all rows. Nested arrays/structs are excluded to keep
        # the payload small and the contract obvious. Built before enrichment so
        # the loop order below can change without affecting _first's contents.
        _first: Dict[str, Any] = {}
        if rows:
            _first = {
                k: v for k, v in rows[0].items()
                if not isinstance(v, (list, dict))
            }

        total = len(rows)
        enriched = []
        for idx, row in enumerate(rows):
            row["_index"] = idx + 1
            row["_total"] = total
            # True when _index is even (2nd, 4th, ... rows) — useful for zebra striping.
            row["_even"] = row["_index"] % 2 == 0
            enriched.append(row)

        return {"rows": enriched, "_first": _first}
