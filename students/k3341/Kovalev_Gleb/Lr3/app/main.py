from fastapi import FastAPI, HTTPException
from celery.result import AsyncResult
import requests

from app.schemas import DirectParseResponse, HealthResponse, ParseRequest, QueueParseResponse, TaskStatusResponse
from shared.db import init_database
from shared.settings import get_database_url, get_parser_service_url
from worker.celery_app import celery_app
from worker.tasks import parse_url_task

app = FastAPI(
    title="Lab 3 Main API",
    description="FastAPI application that calls parser service directly and through Celery queue.",
)


@app.on_event("startup")
def startup() -> None:
    init_database(get_database_url())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api")


@app.post("/parse/direct", response_model=DirectParseResponse)
def parse_direct(payload: ParseRequest) -> DirectParseResponse:
    parser_url = f"{get_parser_service_url().rstrip('/')}/parse"
    try:
        response = requests.post(
            parser_url,
            json={"url": str(payload.url)},
            timeout=30,
        )
        response.raise_for_status()
        return DirectParseResponse(message="Parsing completed", **response.json())
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.post("/parse/queue", response_model=QueueParseResponse)
def parse_queue(payload: ParseRequest) -> QueueParseResponse:
    task = parse_url_task.delay(str(payload.url))
    return QueueParseResponse(
        message="Parsing task accepted",
        task_id=task.id,
        status="queued",
    )


@app.get("/parse/tasks/{task_id}", response_model=TaskStatusResponse)
def task_status(task_id: str) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    task_result = None
    if result.ready():
        task_result = str(result.result) if isinstance(result.result, Exception) else result.result
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=task_result,
    )
