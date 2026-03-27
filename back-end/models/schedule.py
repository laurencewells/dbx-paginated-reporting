from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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

    name: str
    project_id: UUID
    structure_id: UUID
    template_id: UUID
    cron_expression: str
    is_active: bool = True
    send_list_ids: List[UUID] = []


class ScheduleUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = None
    cron_expression: Optional[str] = None
    is_active: Optional[bool] = None
    expected_updated_at: Optional[datetime] = None
    send_list_ids: Optional[List[UUID]] = None


class ScheduleExecution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    schedule_id: UUID
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
