from typing import Any, Optional

from pydantic import BaseModel, HttpUrl


class ParseRequest(BaseModel):
    url: HttpUrl


class DirectParseResponse(BaseModel):
    message: str
    url: str
    title: str
    status_code: int
    elapsed_seconds: float
    notification_id: int
    parsed_page_id: int


class QueueParseResponse(BaseModel):
    message: str
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None


class HealthResponse(BaseModel):
    status: str
    service: str
