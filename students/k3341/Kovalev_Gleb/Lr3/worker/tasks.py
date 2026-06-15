from shared.db import cleanup_old_results, save_parsed_title
from shared.parser import parse_url
from shared.settings import get_database_url
from worker.celery_app import celery_app


@celery_app.task(name="worker.parse_url_task")
def parse_url_task(url: str) -> dict:
    parsed = parse_url(url)
    saved = save_parsed_title(
        get_database_url(),
        parsed.url,
        parsed.title,
        "celery-worker",
        parsed.elapsed_seconds,
        parsed.status_code,
    )
    return {
        "url": parsed.url,
        "title": parsed.title,
        "status_code": parsed.status_code,
        "elapsed_seconds": parsed.elapsed_seconds,
        "notification_id": saved["notification_id"],
        "parsed_page_id": saved["parsed_page_id"],
    }


@celery_app.task(name="worker.cleanup_old_parse_results")
def cleanup_old_parse_results(days: int = 7) -> dict:
    deleted = cleanup_old_results(get_database_url(), days)
    return {
        "deleted": deleted,
        "days": days,
    }
