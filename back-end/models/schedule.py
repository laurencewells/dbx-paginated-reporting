from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExecutionStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    interrupted = "interrupted"


class Schedule(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    project_id: UUID
    structure_id: UUID
    template_id: UUID
    cron_expression: str
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    send_list_ids: List[UUID] = []


class ScheduleCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    project_id: UUID
    structure_id: UUID
    template_id: UUID
    cron_expression: str
    is_active: bool = True
    send_list_ids: List[UUID] = []

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str) -> str:
        parts = v.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 fields: minute hour day month day_of_week")
        return v


class ScheduleUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, max_length=200)
    cron_expression: Optional[str] = None
    is_active: Optional[bool] = None
    expected_updated_at: Optional[datetime] = None
    send_list_ids: Optional[List[UUID]] = None

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            parts = v.strip().split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have exactly 5 fields: minute hour day month day_of_week")
        return v


class ScheduleExecution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    schedule_id: UUID
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
