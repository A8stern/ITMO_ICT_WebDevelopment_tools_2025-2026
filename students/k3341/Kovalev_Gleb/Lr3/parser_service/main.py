from fastapi import FastAPI, HTTPException

from app.schemas import DirectParseResponse, HealthResponse, ParseRequest
from shared.db import init_database, save_parsed_title
from shared.parser import parse_url
from shared.settings import get_database_url

app = FastAPI(
    title="Lab 3 Parser Service",
    description="Separate FastAPI service for parsing pages and saving titles to database.",
)


@app.on_event("startup")
def startup() -> None:
    init_database(get_database_url())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="parser")


@app.post("/parse", response_model=DirectParseResponse)
def parse(payload: ParseRequest) -> DirectParseResponse:
    try:
        parsed = parse_url(str(payload.url))
        saved = save_parsed_title(
            get_database_url(),
            parsed.url,
            parsed.title,
            "http-parser-service",
            parsed.elapsed_seconds,
            parsed.status_code,
        )
        return DirectParseResponse(
            message="Parsing completed",
            url=parsed.url,
            title=parsed.title,
            status_code=parsed.status_code,
            elapsed_seconds=parsed.elapsed_seconds,
            notification_id=saved["notification_id"],
            parsed_page_id=saved["parsed_page_id"],
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
