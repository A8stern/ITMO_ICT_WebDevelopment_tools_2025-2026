from datetime import datetime, timedelta
import os
from time import sleep

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, create_engine, delete, insert, select
from sqlalchemy.exc import OperationalError

metadata = MetaData()

app_user = Table(
    "app_user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, unique=True),
    Column("email", String, nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
)

notification = Table(
    "notification",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("message", String, nullable=False),
    Column("is_read", Boolean, nullable=False, default=False),
    Column("created_at", DateTime, nullable=False),
    Column("user_id", Integer, ForeignKey("app_user.id"), nullable=False),
)

parsed_page = Table(
    "parsed_page",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String, nullable=False),
    Column("title", String, nullable=False),
    Column("approach", String, nullable=False),
    Column("elapsed_seconds", Float, nullable=False, default=0),
    Column("status_code", Integer, nullable=False, default=200),
    Column("created_at", DateTime, nullable=False),
    Column("user_id", Integer, ForeignKey("app_user.id"), nullable=False),
)


def get_engine(database_url: str):
    connect_args = {"check_same_thread": False, "timeout": 30} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def init_database(database_url: str) -> int:
    engine = get_engine(database_url)
    retries = int(os.getenv("DB_INIT_RETRIES", "30"))
    delay = float(os.getenv("DB_INIT_DELAY", "1"))
    for attempt in range(retries):
        try:
            metadata.create_all(engine)
            with engine.begin() as connection:
                user_id = connection.execute(
                    select(app_user.c.id).where(app_user.c.username == "lab3_parser")
                ).scalar_one_or_none()
                if user_id is None:
                    result = connection.execute(
                        insert(app_user).values(
                            username="lab3_parser",
                            email="lab3_parser@example.com",
                            hashed_password="lab3_service_user",
                            is_active=True,
                        )
                    )
                    user_id = result.inserted_primary_key[0]
                return int(user_id)
        except OperationalError:
            if attempt == retries - 1:
                raise
            sleep(delay)
    raise RuntimeError("Database initialization failed")


def save_parsed_title(database_url: str, url: str, title: str, approach: str, elapsed_seconds: float, status_code: int) -> dict:
    user_id = init_database(database_url)
    engine = get_engine(database_url)
    now = datetime.utcnow()
    clean_title = title[:180] if title else "Untitled page"
    with engine.begin() as connection:
        notification_result = connection.execute(
            insert(notification).values(
                title=f"Parsed: {clean_title[:120]}",
                message=f"{approach}: {url}",
                is_read=False,
                created_at=now,
                user_id=user_id,
            )
        )
        parsed_page_result = connection.execute(
            insert(parsed_page).values(
                url=url,
                title=clean_title,
                approach=approach,
                elapsed_seconds=elapsed_seconds,
                status_code=status_code,
                created_at=now,
                user_id=user_id,
            )
        )
        return {
            "notification_id": int(notification_result.inserted_primary_key[0]),
            "parsed_page_id": int(parsed_page_result.inserted_primary_key[0]),
            "user_id": user_id,
        }


def cleanup_old_results(database_url: str, days: int = 7) -> int:
    init_database(database_url)
    engine = get_engine(database_url)
    threshold = datetime.utcnow() - timedelta(days=days)
    with engine.begin() as connection:
        result = connection.execute(delete(parsed_page).where(parsed_page.c.created_at < threshold))
        return int(result.rowcount or 0)
