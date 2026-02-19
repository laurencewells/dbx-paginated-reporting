"""
Unit tests for StructuresRepository.

The LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.structure import Structure, StructureCreate, StructureField, StructureTable, StructureUpdate
from repositories.structures import StructuresRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
SID = uuid.uuid4()
PID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row(
    *,
    id: str | None = None,
    name: str = "My Structure",
    project_id: str | None = str(PID),
    fields=None,
    tables=None,
    relationships=None,
    selected_columns=None,
    sql_query: str | None = "SELECT col FROM cat.sch.tbl",
):
    """Return a tuple row matching the _COLUMNS select order."""
    return (
        str(id or SID),
        name,
        project_id,
        json.dumps(fields or [{"name": "col", "type": "string", "children": None}]),
        json.dumps(tables or [{"full_name": "cat.sch.tbl", "alias": "tbl"}]),
        json.dumps(relationships or []),
        json.dumps(selected_columns or ["col"]),
        sql_query,
        NOW,
        NOW,
    )


def _make_result(rows: list | None = None, *, rowcount: int = 1):
    result = MagicMock()
    _rows = rows if rows is not None else []
    result.fetchall.return_value = _rows
    result.fetchone.return_value = _rows[0] if _rows else None
    result.rowcount = rowcount
    return result


def _make_repo(query_result=None) -> tuple[StructuresRepository, MagicMock]:
    connector = MagicMock()
    connector.execute_query = AsyncMock(return_value=query_result or _make_result())
    repo = StructuresRepository(connector=connector)
    return repo, connector


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    def test_raises_runtime_error_when_no_connector(self):
        repo = StructuresRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            repo._require_connector()


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_get_by_id_returns_structure_when_found(self):
        row = _row(id=SID)
        repo, connector = _make_repo(_make_result([row]))
        result = await repo.get_by_id(SID)
        assert isinstance(result, Structure)
        assert str(result.id) == str(SID)

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_passes_id_as_string_param(self):
        repo, connector = _make_repo(_make_result([_row()]))
        sid = uuid.uuid4()
        await repo.get_by_id(sid)
        _, kwargs = connector.execute_query.call_args
        # params is second positional arg
        call_args = connector.execute_query.call_args[0]
        assert str(sid) in call_args[1]["id"]


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_structure(self):
        row = _row()
        repo, connector = _make_repo(_make_result([row]))
        data = StructureCreate(
            name="New",
            project_id=PID,
            fields=[],
            tables=[StructureTable(full_name="cat.sch.tbl", alias="t")],
            selected_columns=["col"],
        )
        result = await repo.create(data)
        assert isinstance(result, Structure)
        assert result.name == "My Structure"  # comes from mock row

    @pytest.mark.asyncio
    async def test_create_serialises_fields_as_json(self):
        row = _row()
        repo, connector = _make_repo(_make_result([row]))
        data = StructureCreate(
            name="New",
            project_id=PID,
            fields=[StructureField(name="f", type="string")],
            tables=[],
            selected_columns=[],
        )
        await repo.create(data)
        params = connector.execute_query.call_args[0][1]
        parsed = json.loads(params["fields"])
        assert parsed[0]["name"] == "f"


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_updated_structure(self):
        row = _row(name="Updated")
        repo, connector = _make_repo(_make_result([row]))
        data = StructureUpdate(name="Updated")
        result = await repo.update(SID, data)
        assert isinstance(result, Structure)

    @pytest.mark.asyncio
    async def test_update_returns_none_when_row_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        data = StructureUpdate(name="New name")
        result = await repo.update(uuid.uuid4(), data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_no_fields_calls_get_by_id(self):
        """When StructureUpdate has all None fields, repository falls back to get_by_id."""
        existing_row = _row()
        repo, connector = _make_repo(_make_result([existing_row]))
        data = StructureUpdate()  # all None
        await repo.update(SID, data)
        # Should have called execute_query once (the get_by_id SELECT)
        connector.execute_query.assert_awaited_once()
        sql = connector.execute_query.call_args[0][0]
        assert "SELECT" in sql


# ---------------------------------------------------------------------------
# update_built
# ---------------------------------------------------------------------------


class TestUpdateBuilt:
    @pytest.mark.asyncio
    async def test_update_built_returns_structure(self):
        row = _row(sql_query="SELECT col FROM t")
        repo, connector = _make_repo(_make_result([row]))
        fields = [StructureField(name="col", type="string")]
        result = await repo.update_built(SID, "SELECT col FROM t", fields)
        assert isinstance(result, Structure)
        assert result.sql_query == "SELECT col FROM t"

    @pytest.mark.asyncio
    async def test_update_built_returns_none_when_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        result = await repo.update_built(uuid.uuid4(), "SELECT 1", [])
        assert result is None


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_returns_true_when_row_deleted(self):
        result_mock = _make_result(rowcount=1)
        repo, connector = _make_repo(result_mock)
        deleted = await repo.delete(SID)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_no_row_deleted(self):
        result_mock = _make_result(rowcount=0)
        repo, connector = _make_repo(result_mock)
        deleted = await repo.delete(uuid.uuid4())
        assert deleted is False


# ---------------------------------------------------------------------------
# _row_to_model
# ---------------------------------------------------------------------------


class TestRowToModel:
    def test_parses_json_string_fields(self):
        row = _row()
        model = StructuresRepository._row_to_model(row)
        assert isinstance(model.fields, list)
        assert isinstance(model.tables, list)

    def test_parses_already_parsed_list_fields(self):
        """If the DB driver already deserialised JSON, accept it as-is."""
        row = list(_row())
        row[3] = [{"name": "col", "type": "string", "children": None}]
        row[4] = [{"full_name": "cat.sch.tbl", "alias": "tbl"}]
        row[5] = []
        row[6] = ["col"]
        model = StructuresRepository._row_to_model(tuple(row))
        assert len(model.fields) == 1
        assert model.fields[0].name == "col"
