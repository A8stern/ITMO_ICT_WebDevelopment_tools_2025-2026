# Lab 3

Лабораторная работа 3 посвящена упаковке FastAPI-приложения в Docker, работе с источниками данных и запуску парсера через HTTP и очередь задач.

В этой работе собрана мини-система из нескольких сервисов:

- основное FastAPI-приложение;
- отдельный FastAPI-сервис парсера;
- PostgreSQL;
- Redis;
- Celery worker;
- Celery beat для периодических задач.

Проект находится в отдельной папке `lab_3`.

## Цель работы

Цель лабораторной:

- упаковать FastAPI-приложение в Docker;
- упаковать приложение парсера в Docker;
- поднять PostgreSQL через Docker Compose;
- поднять Redis через Docker Compose;
- интегрировать парсер с базой данных;
- реализовать HTTP-вызов парсера;
- реализовать вызов парсера из основного FastAPI-приложения;
- реализовать вызов парсера через Celery-очередь;
- добавить Celery worker;
- добавить Celery beat;
- настроить периодическую задачу;
- описать архитектуру и запуск в README.

## Структура проекта

```text
lab_3/
├── .env.example
├── Dockerfile.api
├── Dockerfile.parser
├── Dockerfile.worker
├── README.md
├── docker-compose.yml
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
├── parser_service/
│   ├── __init__.py
│   └── main.py
├── shared/
│   ├── __init__.py
│   ├── db.py
│   ├── parser.py
│   └── settings.py
└── worker/
    ├── __init__.py
    ├── celery_app.py
    └── tasks.py
```

## Назначение папок

### `app`

Основное FastAPI-приложение.

Оно отвечает за:

- health-check;
- синхронный вызов парсера через HTTP;
- постановку задачи парсинга в Celery;
- получение статуса Celery-задачи.

### `parser_service`

Отдельное FastAPI-приложение парсера.

Оно отвечает за:

- прием URL через HTTP;
- загрузку страницы;
- извлечение `<title>`;
- сохранение результата в БД.

### `shared`

Общий код, который используется несколькими сервисами:

- настройки окружения;
- парсер HTML;
- работа с БД.

Такой слой нужен, чтобы parser service и Celery worker не дублировали одинаковую логику.

### `worker`

Celery-приложение и фоновые задачи.

Содержит:

- конфигурацию Celery;
- задачу парсинга URL;
- периодическую задачу очистки старых результатов.

## Используемые технологии

- FastAPI;
- Uvicorn;
- PostgreSQL;
- Redis;
- Celery;
- SQLAlchemy Core;
- Requests;
- Docker;
- Docker Compose.

## Подзадача 1: Docker для FastAPI, БД и парсера

По заданию нужно упаковать:

- FastAPI-приложение;
- базу данных;
- парсер данных.

В проекте для этого сделаны три Dockerfile и один `docker-compose.yml`.

### Dockerfile.api

Файл:

```text
Dockerfile.api
```

Он собирает контейнер основного API.

Что делает:

1. Берет базовый образ `python:3.11-slim`.
2. Создает рабочую директорию `/app`.
3. Копирует `requirements.txt`.
4. Устанавливает зависимости.
5. Копирует папки `app`, `shared`, `worker`.
6. Запускает:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Почему API-контейнеру копируется `worker`:

- основное приложение ставит задачи в Celery;
- для этого ему нужен импорт `parse_url_task`;
- фактически задача выполняется не в API-контейнере, а в Celery worker.

### Dockerfile.parser

Файл:

```text
Dockerfile.parser
```

Он собирает отдельный HTTP-сервис парсера.

Что делает:

1. Устанавливает зависимости.
2. Копирует `app`, `parser_service`, `shared`.
3. Запускает:

```bash
uvicorn parser_service.main:app --host 0.0.0.0 --port 8001
```

Папка `app` копируется в parser-контейнер из-за общих Pydantic-схем.

### Dockerfile.worker

Файл:

```text
Dockerfile.worker
```

Он собирает образ для Celery worker и Celery beat.

Что делает:

1. Устанавливает зависимости.
2. Копирует `shared` и `worker`.
3. По умолчанию запускает Celery worker:

```bash
celery -A worker.celery_app.celery_app worker --loglevel=info
```

В `docker-compose.yml` этот же образ используется дважды:

- как `worker`;
- как `beat`.

Для `beat` команда переопределяется.

## Docker Compose

Файл:

```text
docker-compose.yml
```

В нем описаны сервисы:

| Сервис | Назначение | Порт |
|---|---|---|
| `db` | PostgreSQL | `5433:5432` |
| `redis` | Redis broker/result backend | `6379:6379` |
| `api` | основное FastAPI-приложение | `8000:8000` |
| `parser` | отдельный FastAPI-сервис парсера | `8001:8001` |
| `worker` | Celery worker | внутренний |
| `beat` | Celery beat periodic scheduler | внутренний |

## Схема сервисов

```mermaid
flowchart LR
    Client["Client / Swagger"] --> API["api: FastAPI main service"]
    API --> Parser["parser: FastAPI parser service"]
    Parser --> DB["db: PostgreSQL"]
    API --> Redis["redis: broker/backend"]
    Redis --> Worker["worker: Celery worker"]
    Worker --> DB
    Worker --> Web["External web page"]
    Parser --> Web
    Beat["beat: Celery beat"] --> Redis
```

## Переменные окружения

Файл `.env.example`:

```text
DATABASE_URL=postgresql+psycopg2://postgres:123@localhost:5433/finance_lab_db
PARSER_SERVICE_URL=http://localhost:8001
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

В Docker Compose используются внутренние имена сервисов:

```text
DATABASE_URL=postgresql+psycopg2://postgres:123@db:5432/finance_lab_db
PARSER_SERVICE_URL=http://parser:8001
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

## База данных

Парсер сохраняет данные в таблицы:

- `app_user`;
- `notification`;
- `parsed_page`.

Таблица `notification` выбрана потому, что в лабораторной 1 уже была сущность уведомлений. Заголовок страницы можно представить как уведомление о результате парсинга.

Таблица `parsed_page` добавлена для технического хранения результата парсинга:

- URL;
- title;
- подход вызова;
- HTTP status code;
- время выполнения;
- дата создания.

## Схема БД

```mermaid
erDiagram
    APP_USER ||--o{ NOTIFICATION : owns
    APP_USER ||--o{ PARSED_PAGE : owns

    APP_USER {
        int id
        string username
        string email
        string hashed_password
        bool is_active
    }

    NOTIFICATION {
        int id
        string title
        string message
        bool is_read
        datetime created_at
        int user_id
    }

    PARSED_PAGE {
        int id
        string url
        string title
        string approach
        float elapsed_seconds
        int status_code
        datetime created_at
        int user_id
    }
```

## Инициализация БД

В `shared/db.py` есть функция:

```python
init_database(database_url)
```

Она:

1. создает таблицы, если их нет;
2. создает технического пользователя `lab3_parser`;
3. возвращает `user_id`.

Также в ней есть retry-механизм. Он нужен потому, что Docker Compose запускает контейнеры в нужном порядке, но PostgreSQL может быть еще не готов принимать подключения.

Переменные:

| Переменная | Значение | Назначение |
|---|---|---|
| `DB_INIT_RETRIES` | `30` | количество попыток подключения |
| `DB_INIT_DELAY` | `1` | пауза между попытками |

## Подзадача 2: HTTP-вызов парсера из FastAPI

По заданию нужно добавить эндпоинт в FastAPI, который принимает URL, отправляет запрос парсеру и возвращает результат клиенту.

В основном API это реализовано ручкой:

```http
POST /parse/direct
```

Тело запроса:

```json
{
  "url": "https://example.com"
}
```

Как это работает:

1. Клиент отправляет URL в `api`.
2. `api` делает HTTP-запрос в сервис `parser`.
3. `parser` загружает страницу.
4. `parser` извлекает `<title>`.
5. `parser` сохраняет результат в PostgreSQL.
6. `parser` возвращает результат в `api`.
7. `api` возвращает результат клиенту.

Пример ответа:

```json
{
  "message": "Parsing completed",
  "url": "https://example.com/",
  "title": "Example Domain",
  "status_code": 200,
  "elapsed_seconds": 0.221,
  "notification_id": 1,
  "parsed_page_id": 1
}
```

## Parser service

Parser service имеет собственный endpoint:

```http
POST /parse
```

Его можно вызвать напрямую:

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Также есть health-check:

```http
GET /health
```

Ответ:

```json
{
  "status": "ok",
  "service": "parser"
}
```

## Подзадача 3: Celery, Redis и очередь

По заданию нужно добавить:

- Celery;
- Redis;
- Celery worker;
- endpoint для постановки задачи в очередь;
- endpoint для проверки статуса;
- periodic task.

## Celery-конфигурация

Файл:

```text
worker/celery_app.py
```

Создается объект:

```python
celery_app = Celery(
    "lab3_parser_queue",
    broker=get_celery_broker_url(),
    backend=get_celery_result_backend(),
    include=["worker.tasks"],
)
```

Redis используется:

- как broker для очереди задач;
- как result backend для хранения результата.

## Celery-задача парсинга

Файл:

```text
worker/tasks.py
```

Задача:

```python
parse_url_task(url)
```

Она:

1. получает URL;
2. загружает страницу;
3. извлекает заголовок;
4. сохраняет результат в БД;
5. возвращает JSON-результат.

## Endpoint для постановки задачи в очередь

В основном API:

```http
POST /parse/queue
```

Тело запроса:

```json
{
  "url": "https://example.com"
}
```

Ответ:

```json
{
  "message": "Parsing task accepted",
  "task_id": "f8f10b2c-...",
  "status": "queued"
}
```

## Endpoint проверки статуса задачи

```http
GET /parse/tasks/{task_id}
```

Возможные статусы:

- `PENDING`;
- `STARTED`;
- `SUCCESS`;
- `FAILURE`;
- `RETRY`.

Пример успешного ответа:

```json
{
  "task_id": "f8f10b2c-...",
  "status": "SUCCESS",
  "result": {
    "url": "https://example.com/",
    "title": "Example Domain",
    "status_code": 200,
    "elapsed_seconds": 0.231,
    "notification_id": 2,
    "parsed_page_id": 2
  }
}
```

## Periodic task

По заданию нужно настроить периодические задачи Celery.

В `worker/celery_app.py` настроено расписание:

```python
celery_app.conf.beat_schedule = {
    "cleanup-old-parse-results": {
        "task": "worker.cleanup_old_parse_results",
        "schedule": 3600.0,
        "args": (7,),
    }
}
```

Каждый час Celery beat ставит задачу:

```text
worker.cleanup_old_parse_results
```

Она удаляет записи из `parsed_page`, которые старше 7 дней.

Зачем это нужно:

- таблица результатов парсинга не растет бесконечно;
- показано использование Celery beat;
- периодическая задача не блокирует API.

## API основного приложения

| Метод | URL | Назначение |
|---|---|---|
| GET | `/health` | проверка API |
| POST | `/parse/direct` | синхронный HTTP-вызов parser service |
| POST | `/parse/queue` | постановка задачи в Celery |
| GET | `/parse/tasks/{task_id}` | проверка статуса Celery-задачи |

## API parser service

| Метод | URL | Назначение |
|---|---|---|
| GET | `/health` | проверка parser service |
| POST | `/parse` | прямой запуск парсинга |

## Запуск через Docker Compose

Из папки `lab_3`:

```bash
docker compose up --build
```

После запуска будут доступны:

- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Parser service: http://localhost:8001
- Parser docs: http://localhost:8001/docs
- PostgreSQL: localhost:5433
- Redis: localhost:6379

Остановка:

```bash
docker compose down
```

Остановка с удалением volume PostgreSQL:

```bash
docker compose down -v
```

## Проверка health-check

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "api"
}
```

```bash
curl http://localhost:8001/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "parser"
}
```

## Проверка прямого вызова парсера

Через основное API:

```bash
curl -X POST http://localhost:8000/parse/direct \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Через parser service напрямую:

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Проверка очереди

Поставить задачу:

```bash
curl -X POST http://localhost:8000/parse/queue \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Пример ответа:

```json
{
  "message": "Parsing task accepted",
  "task_id": "task-id",
  "status": "queued"
}
```

Проверить статус:

```bash
curl http://localhost:8000/parse/tasks/task-id
```

## Проверка Docker Compose

Была выполнена команда:

```bash
docker compose -f lab_3/docker-compose.yml config
```

Она успешно разобрала compose-файл и показала все сервисы:

- `api`;
- `parser`;
- `db`;
- `redis`;
- `worker`;
- `beat`.

## Локальная проверка без Docker

Для проверки импорта можно использовать SQLite:

```bash
cd lab_3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=sqlite:////private/tmp/lab3_import.db python -c "from app.main import app; print(app.title)"
DATABASE_URL=sqlite:////private/tmp/lab3_import.db python -c "from parser_service.main import app; print(app.title)"
DATABASE_URL=sqlite:////private/tmp/lab3_import.db python -c "from worker.celery_app import celery_app; print(celery_app.main)"
```

Проверенный результат:

```text
Lab 3 Main API
Lab 3 Parser Service
lab3_parser_queue
```

## Что выполнено по требованиям

| Требование | Выполнение |
|---|---|
| FastAPI-приложение из лабораторной 1 | реализовано отдельное основное API |
| База данных | PostgreSQL в Docker Compose |
| Парсер данных | отдельный parser service |
| HTTP-вызов парсера | `POST /parse/direct` и `POST /parse` |
| Dockerfile для FastAPI | `Dockerfile.api` |
| Dockerfile для парсера | `Dockerfile.parser` |
| Docker Compose | `docker-compose.yml` |
| Endpoint в FastAPI для вызова парсера | `POST /parse/direct` |
| Redis | сервис `redis` |
| Celery | `worker/celery_app.py` |
| Celery worker | сервис `worker` |
| Endpoint для очереди | `POST /parse/queue` |
| Endpoint статуса задачи | `GET /parse/tasks/{task_id}` |
| Periodic tasks | сервис `beat` и задача cleanup |

## Итоговая архитектура

Лабораторная показывает разделение ответственности:

- API отвечает за взаимодействие с клиентом;
- parser service отвечает за синхронный HTTP-парсинг;
- Redis отвечает за очередь;
- Celery worker выполняет фоновые задачи;
- Celery beat создает периодические задачи;
- PostgreSQL хранит результат.

Такой подход ближе к реальной backend-архитектуре, где долгие операции не должны блокировать основной API-поток.
