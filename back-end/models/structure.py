from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StructureField(BaseModel):
    """A single field in a data structure, optionally with nested children."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    name: str
    type: str
    children: Optional[List[StructureField]] = None


class StructureTable(BaseModel):
    """A Unity Catalog table selected for a data structure."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    full_name: str
    alias: str


class Structure(BaseModel):
    """Domain model for a persisted data structure."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    id: UUID
    name: str
    project_id: UUID = Field(alias="project_id")
    fields: List[StructureField] = Field(default_factory=list)
    tables: List[StructureTable] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    selected_columns: List[str] = Field(default_factory=list)
    sql_query: Optional[str] = Field(None, alias="sql_query")
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")


class StructureCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    project_id: UUID
    fields: List[StructureField] = Field(default_factory=list)
    tables: List[StructureTable] = Field(default_factory=list)
    selected_columns: List[str] = Field(default_factory=list)


class StructureUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    fields: Optional[List[StructureField]] = None
    tables: Optional[List[StructureTable]] = None
    selected_columns: Optional[List[str]] = None
