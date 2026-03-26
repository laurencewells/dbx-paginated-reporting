from datetime import datetime
from typing import Annotated, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

_MAX_EMAILS = 500
_EmailList = Annotated[List[EmailStr], Field(max_length=_MAX_EMAILS)]


class EmailSendList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    project_id: UUID
    smtp_connection_id: UUID
    emails: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime


class EmailSendListCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    project_id: UUID
    smtp_connection_id: UUID
    emails: _EmailList = []


class EmailSendListUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    smtp_connection_id: Optional[UUID] = None
    emails: Optional[_EmailList] = None
