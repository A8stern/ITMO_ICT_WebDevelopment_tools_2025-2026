from celery import Celery

from shared.settings import get_celery_broker_url, get_celery_result_backend

celery_app = Celery(
    "lab3_parser_queue",
    broker=get_celery_broker_url(),
    backend=get_celery_result_backend(),
    include=["worker.tasks"],
)

celery_app.conf.timezone = "UTC"
celery_app.conf.task_track_started = True
celery_app.conf.result_expires = 3600
celery_app.conf.beat_schedule = {
    "cleanup-old-parse-results": {
        "task": "worker.cleanup_old_parse_results",
        "schedule": 3600.0,
        "args": (7,),
    }
}
