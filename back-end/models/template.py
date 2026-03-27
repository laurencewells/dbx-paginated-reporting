from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

PageSize = Literal["A4", "email"]
TemplateType = Literal["html", "markdown"]


class Template(BaseModel):
    """Domain model for a persisted report template."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    id: UUID
    name: str
    structure_id: UUID = Field(alias="structure_id")
    html_content: str = Field("", alias="html_content")
    page_size: PageSize = Field("A4", alias="page_size")
    template_type: TemplateType = Field("html", alias="template_type")
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")


class TemplateCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    structure_id: UUID
    html_content: str = ""
    page_size: PageSize = "A4"
    template_type: TemplateType = "html"


class TemplateUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    structure_id: Optional[UUID] = None
    html_content: Optional[str] = None
    page_size: Optional[PageSize] = None
    expected_updated_at: Optional[datetime] = None
    # template_type is intentionally excluded — it is immutable after creation
