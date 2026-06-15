from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, create_engine, insert, select

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
    Column("created_at", DateTime, nullable=False),
    Column("user_id", Integer, ForeignKey("app_user.id"), nullable=False),
)


def get_engine(db_url: str):
    connect_args = {"check_same_thread": False, "timeout": 30} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, connect_args=connect_args)


def init_database(db_url: str) -> int:
    engine = get_engine(db_url)
    metadata.create_all(engine)
    with engine.begin() as connection:
        user_id = connection.execute(
            select(app_user.c.id).where(app_user.c.username == "lab2_parser")
        ).scalar_one_or_none()
        if user_id is None:
            result = connection.execute(
                insert(app_user).values(
                    username="lab2_parser",
                    email="lab2_parser@example.com",
                    hashed_password="lab2_demo_password_hash",
                    is_active=True,
                )
            )
            user_id = result.inserted_primary_key[0]
        return int(user_id)


def save_title(db_url: str, url: str, title: str, approach: str, elapsed_seconds: float) -> int:
    user_id = init_database(db_url)
    engine = get_engine(db_url)
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
        connection.execute(
            insert(parsed_page).values(
                url=url,
                title=clean_title,
                approach=approach,
                elapsed_seconds=elapsed_seconds,
                created_at=now,
                user_id=user_id,
            )
        )
        return int(notification_result.inserted_primary_key[0])
