from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import auth, finance

base_dir = Path(__file__).resolve().parent
frontend_dir = base_dir / "app" / "frontend"

app = FastAPI(
    title="Personal Finance API. Lab 1",
    description="FastAPI server application with SQLModel, Alembic and JWT authentication.",
)

app.include_router(auth.router)
app.include_router(finance.router)
app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")


@app.get("/")
def hello() -> str:
    return "Hello, personal finance lab user!"


@app.get("/app", response_class=FileResponse)
def frontend() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")
