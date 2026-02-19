from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Project(BaseModel):
    """Domain model for a persisted project."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    id: UUID
    name: str
    user_email: str = Field(alias="user_email")
    is_locked: bool = Field(False, alias="is_locked")
    is_global: bool = Field(False, alias="is_global")
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    is_locked: Optional[bool] = None
    is_global: Optional[bool] = None


class ProjectShare(BaseModel):
    """Domain model for a project share record."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    id: UUID
    project_id: UUID = Field(alias="project_id")
    shared_with_email: str = Field(alias="shared_with_email")
    shared_by_email: str = Field(alias="shared_by_email")
    created_at: datetime = Field(alias="created_at")


class ProjectShareCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    shared_with_email: EmailStr
