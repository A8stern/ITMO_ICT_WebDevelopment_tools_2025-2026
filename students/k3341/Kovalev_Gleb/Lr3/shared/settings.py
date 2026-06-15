import os

DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:123@localhost:5432/finance_lab_db"
DEFAULT_PARSER_SERVICE_URL = "http://localhost:8001"
DEFAULT_BROKER_URL = "redis://localhost:6379/0"
DEFAULT_RESULT_BACKEND = "redis://localhost:6379/1"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_parser_service_url() -> str:
    return os.getenv("PARSER_SERVICE_URL", DEFAULT_PARSER_SERVICE_URL)


def get_celery_broker_url() -> str:
    return os.getenv("CELERY_BROKER_URL", DEFAULT_BROKER_URL)


def get_celery_result_backend() -> str:
    return os.getenv("CELERY_RESULT_BACKEND", DEFAULT_RESULT_BACKEND)
