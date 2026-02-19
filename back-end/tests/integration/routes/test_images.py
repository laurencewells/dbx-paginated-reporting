"""
Integration tests for the /api/v1/images routes.

ImagesRepository is injected via dependency_overrides; auth helpers are patched.
No real DB or network calls are made.
"""
from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.authorization import get_images_repo
from models.image import Image

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
IID = uuid.uuid4()
PID = uuid.uuid4()

SMALL_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # minimal fake PNG bytes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _image(
    *,
    id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    filename: str = "photo.png",
    mime_type: str = "image/png",
    size_bytes: int = 108,
) -> Image:
    return Image(
        id=id or IID,
        project_id=project_id or PID,
        filename=filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
        created_at=NOW,
        updated_at=NOW,
    )


def _mock_images_repo(
    *,
    get_all=None,
    get_by_id=None,
    get_data=None,
    count: int = 0,
    create=None,
    update=None,
    delete: bool = True,
) -> MagicMock:
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=get_all or [])
    repo.get_by_id = AsyncMock(return_value=get_by_id)
    repo.get_data = AsyncMock(return_value=get_data)
    repo.count = AsyncMock(return_value=count)
    repo.create = AsyncMock(return_value=create)
    repo.update = AsyncMock(return_value=update)
    repo.delete = AsyncMock(return_value=delete)
    return repo


def _no_lock_patches():
    """Patches that simulate an unlocked project with access granted."""
    return (
        patch("routes.v1.images.check_project_access", return_value=None, new_callable=AsyncMock),
        patch("routes.v1.images.check_project_not_locked", return_value=None, new_callable=AsyncMock),
    )


def _locked_patches():
    """Patches that simulate a locked project with access granted."""
    from fastapi import HTTPException
    return (
        patch("routes.v1.images.check_project_access", return_value=None, new_callable=AsyncMock),
        patch("routes.v1.images.check_project_not_locked", side_effect=HTTPException(status_code=423, detail="Project is locked"), new_callable=AsyncMock),
    )


def _no_access_patches():
    """Patches that simulate a project the caller has no access to."""
    from fastapi import HTTPException
    return (
        patch("routes.v1.images.check_project_access", side_effect=HTTPException(status_code=403, detail="Access denied"), new_callable=AsyncMock),
        patch("routes.v1.images.check_project_not_locked", return_value=None, new_callable=AsyncMock),
    )


def _upload_files(
    content: bytes = SMALL_PNG,
    content_type: str = "image/png",
    filename: str = "test.png",
):
    return [("file", (filename, content, content_type))]


# ---------------------------------------------------------------------------
# GET /images/
# ---------------------------------------------------------------------------


class TestListImages:
    @pytest.mark.asyncio
    async def test_list_images_returns_200(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_all=[_image()])
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/?project_id={PID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_images_returns_list_of_images(self, async_client, dependency_overrides):
        images = [_image(), _image(filename="second.jpg", mime_type="image/jpeg")]
        repo = _mock_images_repo(get_all=images)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/?project_id={PID}")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_images_empty_returns_empty_list(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_all=[])
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/?project_id={PID}")
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_images_passes_project_id_to_repo(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_all=[])
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            await async_client.get(f"/api/v1/images/?project_id={PID}")
        repo.get_all.assert_awaited_once_with(PID)

    @pytest.mark.asyncio
    async def test_list_images_returns_422_when_project_id_missing(self, async_client):
        response = await async_client.get("/api/v1/images/")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_images_returns_422_for_invalid_project_id(self, async_client):
        response = await async_client.get("/api/v1/images/?project_id=not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_images_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_images_repo()
        repo.get_all = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/?project_id={PID}")
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_list_images_response_contains_expected_fields(self, async_client, dependency_overrides):
        img = _image(id=IID, filename="photo.png", mime_type="image/png", size_bytes=512)
        repo = _mock_images_repo(get_all=[img])
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/?project_id={PID}")
        item = response.json()[0]
        assert item["filename"] == "photo.png"
        assert item["mime_type"] == "image/png"
        assert item["size_bytes"] == 512

    @pytest.mark.asyncio
    async def test_list_images_returns_403_when_no_access(self, async_client):
        (p1, p2) = _no_access_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/?project_id={PID}")
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /images/{image_id}
# ---------------------------------------------------------------------------


class TestGetImage:
    @pytest.mark.asyncio
    async def test_get_image_returns_200_when_found(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=_image(id=IID))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_image_returns_correct_filename(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=_image(id=IID, filename="banner.webp"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}")
        assert response.json()["filename"] == "banner.webp"

    @pytest.mark.asyncio
    async def test_get_image_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=None)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_image_returns_422_for_invalid_uuid(self, async_client):
        response = await async_client.get("/api/v1/images/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_image_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_images_repo()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}")
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_get_image_returns_403_when_no_access(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=_image(id=IID))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_access_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}")
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /images/{image_id}/data
# ---------------------------------------------------------------------------


class TestGetImageData:
    @pytest.mark.asyncio
    async def test_get_image_data_returns_200_with_binary_content(self, async_client, dependency_overrides):
        raw = b"\x89PNG\r\n"
        encoded = base64.b64encode(raw).decode("ascii")
        repo = _mock_images_repo(get_by_id=_image(id=IID), get_data=("image/png", encoded))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}/data")
        assert response.status_code == 200
        assert response.content == raw

    @pytest.mark.asyncio
    async def test_get_image_data_sets_correct_content_type(self, async_client, dependency_overrides):
        raw = b"fake-jpeg-data"
        encoded = base64.b64encode(raw).decode("ascii")
        repo = _mock_images_repo(get_by_id=_image(id=IID), get_data=("image/jpeg", encoded))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}/data")
        assert "image/jpeg" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_get_image_data_sets_cache_control_header(self, async_client, dependency_overrides):
        raw = b"data"
        encoded = base64.b64encode(raw).decode("ascii")
        repo = _mock_images_repo(get_by_id=_image(id=IID), get_data=("image/png", encoded))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}/data")
        assert "cache-control" in response.headers
        assert "86400" in response.headers["cache-control"]

    @pytest.mark.asyncio
    async def test_get_image_data_sets_content_security_policy_header(self, async_client, dependency_overrides):
        raw = b"<svg><script>alert(1)</script></svg>"
        encoded = base64.b64encode(raw).decode("ascii")
        repo = _mock_images_repo(get_by_id=_image(id=IID, mime_type="image/svg+xml"), get_data=("image/svg+xml", encoded))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}/data")
        assert "content-security-policy" in response.headers
        assert response.headers["content-security-policy"] == "default-src 'none'"

    @pytest.mark.asyncio
    async def test_get_image_data_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=None, get_data=None)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{uuid.uuid4()}/data")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_image_data_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=_image(id=IID))
        repo.get_data = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}/data")
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_get_image_data_returns_403_when_no_access(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=_image(id=IID))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_access_patches()
        with p1, p2:
            response = await async_client.get(f"/api/v1/images/{IID}/data")
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /images/
# ---------------------------------------------------------------------------


class TestUploadImage:
    @pytest.mark.asyncio
    async def test_upload_image_returns_201_on_success(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image())
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_returns_image_schema(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image(id=IID, filename="test.png"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        data = response.json()
        assert "id" in data
        assert "filename" in data
        assert "mime_type" in data

    @pytest.mark.asyncio
    async def test_upload_image_returns_400_for_disallowed_mime_type(self, async_client):
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content=b"<html>", content_type="text/html", filename="evil.html"),
            )
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_image_returns_400_for_pdf_mime_type(self, async_client):
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content=b"%PDF", content_type="application/pdf", filename="doc.pdf"),
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_image_accepts_jpeg(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image(mime_type="image/jpeg"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content_type="image/jpeg", filename="img.jpg"),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_accepts_gif(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image(mime_type="image/gif"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content_type="image/gif", filename="anim.gif"),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_accepts_webp(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image(mime_type="image/webp"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content_type="image/webp", filename="img.webp"),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_accepts_svg(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image(mime_type="image/svg+xml"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content_type="image/svg+xml", filename="chart.svg"),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_returns_400_when_file_exceeds_2mb(self, async_client):
        big_content = b"x" * (2 * 1024 * 1024 + 1)  # 2MB + 1 byte
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content=big_content),
            )
        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_image_allows_exactly_2mb(self, async_client, dependency_overrides):
        exact_content = b"x" * (2 * 1024 * 1024)  # exactly 2MB
        repo = _mock_images_repo(count=0, create=_image(size_bytes=len(exact_content)))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content=exact_content),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_returns_400_when_at_image_limit(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=20)  # already at limit
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        assert response.status_code == 400
        assert "Maximum" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_image_allows_19th_image(self, async_client, dependency_overrides):
        """19 existing images — one below the limit — should succeed."""
        repo = _mock_images_repo(count=19, create=_image())
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_upload_image_returns_422_when_project_id_missing(self, async_client):
        response = await async_client.post(
            "/api/v1/images/",
            files=_upload_files(),
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_upload_image_returns_423_when_project_is_locked(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image())
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _locked_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        assert response.status_code == 423
        assert "locked" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_image_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0)
        repo.create = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_upload_image_returns_403_when_no_access(self, async_client):
        (p1, p2) = _no_access_patches()
        with p1, p2:
            response = await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(),
            )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_upload_image_preserves_filename_in_create_payload(self, async_client, dependency_overrides):
        """The original filename from the upload is forwarded to the repository create call."""
        repo = _mock_images_repo(count=0, create=_image(filename="logo.png"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(filename="logo.png"),
            )
        call_args = repo.create.call_args[0][0]
        assert call_args.filename == "logo.png"

    @pytest.mark.asyncio
    async def test_upload_image_encodes_content_as_base64(self, async_client, dependency_overrides):
        repo = _mock_images_repo(count=0, create=_image())
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            await async_client.post(
                f"/api/v1/images/?project_id={PID}",
                files=_upload_files(content=SMALL_PNG),
            )
        call_args = repo.create.call_args[0][0]
        decoded = base64.b64decode(call_args.data_base64)
        assert decoded == SMALL_PNG


# ---------------------------------------------------------------------------
# PUT /images/{image_id}
# ---------------------------------------------------------------------------


class TestUpdateImage:
    @pytest.mark.asyncio
    async def test_update_image_returns_200_on_success(self, async_client, dependency_overrides):
        img = _image(id=IID)
        repo = _mock_images_repo(get_by_id=img, update=img)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.put(
                f"/api/v1/images/{IID}",
                json={"filename": "renamed.png"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_image_returns_updated_filename(self, async_client, dependency_overrides):
        img = _image(id=IID, filename="renamed.png")
        repo = _mock_images_repo(get_by_id=img, update=img)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.put(
                f"/api/v1/images/{IID}",
                json={"filename": "renamed.png"},
            )
        assert response.json()["filename"] == "renamed.png"

    @pytest.mark.asyncio
    async def test_update_image_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=None)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.put(
                f"/api/v1/images/{uuid.uuid4()}",
                json={"filename": "ghost.png"},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_image_returns_422_for_invalid_uuid(self, async_client):
        response = await async_client.put(
            "/api/v1/images/not-a-uuid",
            json={"filename": "x.png"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_image_returns_423_when_project_is_locked(self, async_client, dependency_overrides):
        img = _image(id=IID, project_id=PID)
        repo = _mock_images_repo(get_by_id=img, update=img)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _locked_patches()
        with p1, p2:
            response = await async_client.put(
                f"/api/v1/images/{IID}",
                json={"filename": "new.png"},
            )
        assert response.status_code == 423

    @pytest.mark.asyncio
    async def test_update_image_returns_404_when_update_returns_none(self, async_client, dependency_overrides):
        """If the repo update returns None after passing existence check, respond 404."""
        img = _image(id=IID)
        repo = _mock_images_repo(get_by_id=img, update=None)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.put(
                f"/api/v1/images/{IID}",
                json={"filename": "new.png"},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_image_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        img = _image(id=IID)
        repo = _mock_images_repo(get_by_id=img)
        repo.update = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.put(
                f"/api/v1/images/{IID}",
                json={"filename": "broken.png"},
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_update_image_returns_403_when_no_access(self, async_client, dependency_overrides):
        img = _image(id=IID, project_id=PID)
        repo = _mock_images_repo(get_by_id=img)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_access_patches()
        with p1, p2:
            response = await async_client.put(f"/api/v1/images/{IID}", json={"filename": "x.png"})
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# DELETE /images/{image_id}
# ---------------------------------------------------------------------------


class TestDeleteImage:
    @pytest.mark.asyncio
    async def test_delete_image_returns_204_on_success(self, async_client, dependency_overrides):
        img = _image(id=IID)
        repo = _mock_images_repo(get_by_id=img, delete=True)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.delete(f"/api/v1/images/{IID}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_image_returns_404_when_not_found(self, async_client, dependency_overrides):
        repo = _mock_images_repo(get_by_id=None, delete=False)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.delete(f"/api/v1/images/{uuid.uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_image_returns_422_for_invalid_uuid(self, async_client):
        response = await async_client.delete("/api/v1/images/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_image_returns_423_when_project_is_locked(self, async_client, dependency_overrides):
        img = _image(id=IID, project_id=PID)
        repo = _mock_images_repo(get_by_id=img, delete=True)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _locked_patches()
        with p1, p2:
            response = await async_client.delete(f"/api/v1/images/{IID}")
        assert response.status_code == 423

    @pytest.mark.asyncio
    async def test_delete_image_returns_404_when_delete_returns_false(self, async_client, dependency_overrides):
        """If repo.delete returns False after passing existence check, respond 404."""
        img = _image(id=IID)
        repo = _mock_images_repo(get_by_id=img, delete=False)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.delete(f"/api/v1/images/{IID}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_image_returns_503_on_runtime_error(self, async_client, dependency_overrides):
        img = _image(id=IID)
        repo = _mock_images_repo(get_by_id=img)
        repo.delete = AsyncMock(side_effect=RuntimeError("DB down"))
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_lock_patches()
        with p1, p2:
            response = await async_client.delete(f"/api/v1/images/{IID}")
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_delete_image_returns_403_when_no_access(self, async_client, dependency_overrides):
        img = _image(id=IID, project_id=PID)
        repo = _mock_images_repo(get_by_id=img)
        dependency_overrides[get_images_repo] = lambda: repo
        (p1, p2) = _no_access_patches()
        with p1, p2:
            response = await async_client.delete(f"/api/v1/images/{IID}")
        assert response.status_code == 403
