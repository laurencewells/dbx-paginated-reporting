from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Image(BaseModel):
    """Domain model for a persisted gallery image."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    id: UUID
    project_id: UUID = Field(alias="project_id")
    filename: str
    mime_type: str = Field(alias="mime_type")
    size_bytes: int = Field(alias="size_bytes")
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")


class ImageCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    project_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    data_base64: str


class ImageUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filename: Optional[str] = None
