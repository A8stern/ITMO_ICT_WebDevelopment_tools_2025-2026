import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

project_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_dir))

os.environ["DB_ADMIN"] = "sqlite:////private/tmp/finance_lab_test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from app.db import engine
from main import app


@pytest.fixture()
def client():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/auth/register",
        json={
            "username": "tester",
            "email": "tester@example.com",
            "password": "test12345",
        },
    )
    response = client.post(
        "/auth/login",
        json={
            "username": "tester",
            "password": "test12345",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
