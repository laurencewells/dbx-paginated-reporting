"""
Unit tests for ImagesRepository.

The LakebaseConnector is fully mocked; no DB connection is made.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.image import Image, ImageCreate, ImageUpdate
from repositories.images import ImagesRepository

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
IID = uuid.uuid4()
PID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row(
    *,
    id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    filename: str = "photo.png",
    mime_type: str = "image/png",
    size_bytes: int = 1024,
):
    """Return a tuple that mimics a DB row for the images table."""
    return (
        str(id or IID),
        str(project_id or PID),
        filename,
        mime_type,
        size_bytes,
        NOW,
        NOW,
    )


def _make_result(rows: list | None = None, *, rowcount: int = 1, scalar: int | None = None):
    result = MagicMock()
    _rows = rows if rows is not None else []
    result.fetchall.return_value = _rows
    result.fetchone.return_value = _rows[0] if _rows else None
    result.rowcount = rowcount
    result.scalar.return_value = scalar
    return result


def _make_repo(query_result=None) -> tuple[ImagesRepository, MagicMock]:
    connector = MagicMock()
    connector.execute_query = AsyncMock(return_value=query_result or _make_result())
    repo = ImagesRepository(connector=connector)
    return repo, connector


# ---------------------------------------------------------------------------
# _require_connector
# ---------------------------------------------------------------------------


class TestRequireConnector:
    def test_raises_runtime_error_when_no_connector(self):
        repo = ImagesRepository(connector=None)
        with pytest.raises(RuntimeError, match="Lakebase is not available"):
            repo._require_connector()


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


class TestGetAll:
    @pytest.mark.asyncio
    async def test_get_all_returns_list_of_images(self):
        rows = [_row(), _row(filename="second.jpg", mime_type="image/jpeg")]
        repo, connector = _make_repo(_make_result(rows))
        result = await repo.get_all(PID)
        assert len(result) == 2
        assert all(isinstance(img, Image) for img in result)

    @pytest.mark.asyncio
    async def test_get_all_empty_returns_empty_list(self):
        repo, connector = _make_repo(_make_result([]))
        result = await repo.get_all(PID)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_passes_project_id_as_string_param(self):
        repo, connector = _make_repo(_make_result([_row()]))
        await repo.get_all(PID)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)

    @pytest.mark.asyncio
    async def test_get_all_selects_by_project_id(self):
        repo, connector = _make_repo(_make_result([]))
        await repo.get_all(PID)
        sql = connector.execute_query.call_args[0][0]
        assert "project_id" in sql
        assert ":pid" in sql


# ---------------------------------------------------------------------------
# count
# ---------------------------------------------------------------------------


class TestCount:
    @pytest.mark.asyncio
    async def test_count_returns_integer_from_scalar(self):
        repo, connector = _make_repo(_make_result(scalar=5))
        result = await repo.count(PID)
        assert result == 5

    @pytest.mark.asyncio
    async def test_count_returns_zero_when_scalar_is_none(self):
        repo, connector = _make_repo(_make_result(scalar=None))
        result = await repo.count(PID)
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_passes_project_id_as_string_param(self):
        repo, connector = _make_repo(_make_result(scalar=0))
        await repo.count(PID)
        params = connector.execute_query.call_args[0][1]
        assert params["pid"] == str(PID)


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


class TestGetById:
    @pytest.mark.asyncio
    async def test_get_by_id_returns_image_when_found(self):
        row = _row(id=IID)
        repo, connector = _make_repo(_make_result([row]))
        result = await repo.get_by_id(IID)
        assert isinstance(result, Image)
        assert str(result.id) == str(IID)

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        result = await repo.get_by_id(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_passes_id_as_string_param(self):
        repo, connector = _make_repo(_make_result([_row()]))
        image_id = uuid.uuid4()
        await repo.get_by_id(image_id)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(image_id)


# ---------------------------------------------------------------------------
# get_data
# ---------------------------------------------------------------------------


class TestGetData:
    @pytest.mark.asyncio
    async def test_get_data_returns_tuple_when_found(self):
        data_row = ("image/png", "base64encodeddata==")
        result_mock = MagicMock()
        result_mock.fetchone.return_value = data_row
        connector = MagicMock()
        connector.execute_query = AsyncMock(return_value=result_mock)
        repo = ImagesRepository(connector=connector)

        result = await repo.get_data(IID)
        assert result == ("image/png", "base64encodeddata==")

    @pytest.mark.asyncio
    async def test_get_data_returns_none_when_not_found(self):
        result_mock = MagicMock()
        result_mock.fetchone.return_value = None
        connector = MagicMock()
        connector.execute_query = AsyncMock(return_value=result_mock)
        repo = ImagesRepository(connector=connector)

        result = await repo.get_data(uuid.uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_data_selects_mime_type_and_data_base64(self):
        data_row = ("image/jpeg", "data")
        result_mock = MagicMock()
        result_mock.fetchone.return_value = data_row
        connector = MagicMock()
        connector.execute_query = AsyncMock(return_value=result_mock)
        repo = ImagesRepository(connector=connector)

        await repo.get_data(IID)
        sql = connector.execute_query.call_args[0][0]
        assert "mime_type" in sql
        assert "data_base64" in sql


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_image(self):
        repo, connector = _make_repo(_make_result([_row()]))
        data = ImageCreate(
            project_id=PID,
            filename="test.png",
            mime_type="image/png",
            size_bytes=512,
            data_base64="aGVsbG8=",
        )
        result = await repo.create(data)
        assert isinstance(result, Image)

    @pytest.mark.asyncio
    async def test_create_passes_correct_params(self):
        repo, connector = _make_repo(_make_result([_row()]))
        data = ImageCreate(
            project_id=PID,
            filename="test.png",
            mime_type="image/png",
            size_bytes=512,
            data_base64="aGVsbG8=",
        )
        await repo.create(data)
        params = connector.execute_query.call_args[0][1]
        assert params["project_id"] == str(PID)
        assert params["filename"] == "test.png"
        assert params["mime_type"] == "image/png"
        assert params["size_bytes"] == 512
        assert params["data_base64"] == "aGVsbG8="

    @pytest.mark.asyncio
    async def test_create_uses_insert_returning(self):
        repo, connector = _make_repo(_make_result([_row()]))
        data = ImageCreate(
            project_id=PID,
            filename="x.png",
            mime_type="image/png",
            size_bytes=1,
            data_base64="a",
        )
        await repo.create(data)
        sql = connector.execute_query.call_args[0][0]
        assert "INSERT" in sql
        assert "RETURNING" in sql


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_updated_image(self):
        row = _row(filename="renamed.png")
        repo, connector = _make_repo(_make_result([row]))
        data = ImageUpdate(filename="renamed.png")
        result = await repo.update(IID, data)
        assert isinstance(result, Image)
        assert result.filename == "renamed.png"

    @pytest.mark.asyncio
    async def test_update_returns_none_when_not_found(self):
        repo, connector = _make_repo(_make_result([]))
        data = ImageUpdate(filename="ghost.png")
        result = await repo.update(uuid.uuid4(), data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_no_fields_falls_back_to_get_by_id(self):
        """When ImageUpdate has all None fields, repository falls back to get_by_id."""
        repo, connector = _make_repo(_make_result([_row()]))
        data = ImageUpdate()  # all None
        await repo.update(IID, data)
        connector.execute_query.assert_awaited_once()
        sql = connector.execute_query.call_args[0][0]
        assert "SELECT" in sql

    @pytest.mark.asyncio
    async def test_update_filename_builds_set_clause(self):
        row = _row(filename="new.png")
        repo, connector = _make_repo(_make_result([row]))
        data = ImageUpdate(filename="new.png")
        await repo.update(IID, data)
        sql = connector.execute_query.call_args[0][0]
        assert "filename = :filename" in sql

    @pytest.mark.asyncio
    async def test_update_always_sets_updated_at(self):
        row = _row(filename="new.png")
        repo, connector = _make_repo(_make_result([row]))
        data = ImageUpdate(filename="new.png")
        await repo.update(IID, data)
        sql = connector.execute_query.call_args[0][0]
        assert "updated_at = NOW()" in sql


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_returns_true_when_row_deleted(self):
        repo, connector = _make_repo(_make_result(rowcount=1))
        deleted = await repo.delete(IID)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_no_row_deleted(self):
        repo, connector = _make_repo(_make_result(rowcount=0))
        deleted = await repo.delete(uuid.uuid4())
        assert deleted is False

    @pytest.mark.asyncio
    async def test_delete_passes_id_as_string_param(self):
        repo, connector = _make_repo(_make_result(rowcount=1))
        image_id = uuid.uuid4()
        await repo.delete(image_id)
        params = connector.execute_query.call_args[0][1]
        assert params["id"] == str(image_id)


# ---------------------------------------------------------------------------
# _row_to_model
# ---------------------------------------------------------------------------


class TestRowToModel:
    def test_row_to_model_returns_image(self):
        row = _row()
        model = ImagesRepository._row_to_model(row)
        assert isinstance(model, Image)
        assert str(model.id) == str(IID)
        assert model.filename == "photo.png"
        assert model.mime_type == "image/png"
        assert model.size_bytes == 1024

    def test_row_to_model_maps_project_id(self):
        row = _row(project_id=PID)
        model = ImagesRepository._row_to_model(row)
        assert str(model.project_id) == str(PID)

    def test_row_to_model_maps_timestamps(self):
        row = _row()
        model = ImagesRepository._row_to_model(row)
        assert model.created_at == NOW
        assert model.updated_at == NOW
