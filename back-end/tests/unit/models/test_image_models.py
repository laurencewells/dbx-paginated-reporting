"""
Unit tests for Image, ImageCreate, and ImageUpdate Pydantic models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.image import Image, ImageCreate, ImageUpdate

NOW = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
IID = uuid.uuid4()
PID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Image
# ---------------------------------------------------------------------------


class TestImageModel:
    def test_image_valid_construction(self):
        img = Image(
            id=IID,
            project_id=PID,
            filename="photo.png",
            mime_type="image/png",
            size_bytes=2048,
            created_at=NOW,
            updated_at=NOW,
        )
        assert img.filename == "photo.png"
        assert img.size_bytes == 2048

    def test_image_strips_whitespace_from_filename(self):
        img = Image(
            id=IID,
            project_id=PID,
            filename="  photo.png  ",
            mime_type="image/png",
            size_bytes=1,
            created_at=NOW,
            updated_at=NOW,
        )
        assert img.filename == "photo.png"

    def test_image_accepts_alias_field_names(self):
        """populate_by_name=True means aliases and field names both work."""
        img = Image.model_validate(
            {
                "id": str(IID),
                "project_id": str(PID),
                "filename": "x.gif",
                "mime_type": "image/gif",
                "size_bytes": 100,
                "created_at": NOW.isoformat(),
                "updated_at": NOW.isoformat(),
            }
        )
        assert str(img.id) == str(IID)

    def test_image_raises_on_missing_required_field(self):
        with pytest.raises(ValidationError):
            Image(
                id=IID,
                project_id=PID,
                # filename missing
                mime_type="image/png",
                size_bytes=1,
                created_at=NOW,
                updated_at=NOW,
            )


# ---------------------------------------------------------------------------
# ImageCreate
# ---------------------------------------------------------------------------


class TestImageCreateModel:
    def test_image_create_valid_construction(self):
        data = ImageCreate(
            project_id=PID,
            filename="upload.jpg",
            mime_type="image/jpeg",
            size_bytes=500,
            data_base64="aGVsbG8=",
        )
        assert data.filename == "upload.jpg"
        assert data.data_base64 == "aGVsbG8="

    def test_image_create_strips_whitespace(self):
        data = ImageCreate(
            project_id=PID,
            filename="  file.png  ",
            mime_type="  image/png  ",
            size_bytes=1,
            data_base64="x",
        )
        assert data.filename == "file.png"
        assert data.mime_type == "image/png"

    def test_image_create_raises_on_missing_project_id(self):
        with pytest.raises(ValidationError):
            ImageCreate(
                filename="x.png",
                mime_type="image/png",
                size_bytes=1,
                data_base64="x",
            )

    def test_image_create_raises_on_missing_data_base64(self):
        with pytest.raises(ValidationError):
            ImageCreate(
                project_id=PID,
                filename="x.png",
                mime_type="image/png",
                size_bytes=1,
            )


# ---------------------------------------------------------------------------
# ImageUpdate
# ---------------------------------------------------------------------------


class TestImageUpdateModel:
    def test_image_update_all_none_is_valid(self):
        data = ImageUpdate()
        assert data.filename is None

    def test_image_update_with_filename(self):
        data = ImageUpdate(filename="renamed.png")
        assert data.filename == "renamed.png"

    def test_image_update_strips_whitespace_from_filename(self):
        data = ImageUpdate(filename="  renamed.png  ")
        assert data.filename == "renamed.png"
