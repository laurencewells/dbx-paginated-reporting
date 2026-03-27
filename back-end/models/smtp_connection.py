from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SmtpConnection(BaseModel):
    """Internal model — includes secret store references used by the email service."""
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    provider: str
    from_email: str
    smtp_host: str
    smtp_port: int
    username: str
    secret_scope: str
    secret_key: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class SmtpConnectionPublic(BaseModel):
    """API response model — secret store metadata is excluded."""
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    provider: str
    from_email: str
    smtp_host: str
    smtp_port: int
    username: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class SmtpConnectionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    provider: str
    from_email: EmailStr
    smtp_host: str = ""
    smtp_port: int = Field(587, ge=1, le=65535)
    username: str = ""
    password: str


class SmtpConnectionUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    from_email: Optional[EmailStr] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = None
    password: Optional[str] = None  # None means keep existing
