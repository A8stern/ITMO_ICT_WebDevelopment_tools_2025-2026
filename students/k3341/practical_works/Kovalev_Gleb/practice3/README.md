# Practice 1.3

Практика 1.3 продолжает развитие сервиса управления личными финансами. В предыдущей практике приложение уже работало с PostgreSQL через SQLModel, а в этой версии добавлены миграции Alembic, переменные окружения и `.gitignore`.

Проект находится в отдельной папке и не зависит от практик 1.1 и 1.2.

## Цель практики

Цель практики — привести FastAPI-проект к более правильной структуре для реальной разработки:

- вынести строку подключения к БД в `.env`;
- исключить чувствительные и служебные файлы через `.gitignore`;
- подключить Alembic;
- настроить Alembic на чтение URL базы данных из `.env`;
- создать миграцию для таблиц;
- добавить дополнительное поле в ассоциативную таблицу many-to-many;
- сохранить CRUD API и вложенную выдачу связанных объектов.

## Структура проекта

```text
practice_1_3/
├── .env
├── .gitignore
├── alembic.ini
├── connection.py
├── main.py
├── models.py
├── requirements.txt
├── README.md
└── migrations/
    ├── README
    ├── env.py
    ├── script.py.mako
    └── versions/
        └── 20260614_0001_initial_finance_schema.py
```

Назначение файлов:

- `.env` — переменные окружения, в этой практике строка подключения `DB_ADMIN`.
- `.gitignore` — исключения для env-файлов, виртуального окружения, кэша и IDE-файлов.
- `alembic.ini` — основной конфигурационный файл Alembic.
- `connection.py` — подключение к PostgreSQL через переменную окружения.
- `models.py` — SQLModel-модели.
- `main.py` — FastAPI-приложение и API.
- `migrations/env.py` — настройка Alembic-окружения.
- `migrations/script.py.mako` — шаблон генерации миграций.
- `migrations/versions/...` — файл миграции.

## Используемые технологии

- FastAPI — API-фреймворк.
- SQLModel — ORM и Pydantic-модели.
- PostgreSQL — база данных.
- Alembic — миграции базы данных.
- python-dotenv — загрузка переменных из `.env`.
- psycopg2-binary — драйвер PostgreSQL.
- Uvicorn — сервер приложения.

## Переменные окружения

В `.env` находится строка подключения:

```text
DB_ADMIN=postgresql://postgres:123@localhost/finance_db
```

В `connection.py` она читается так:

```python
load_dotenv()
db_url = os.getenv("DB_ADMIN", "postgresql://postgres:123@localhost/finance_db")
```

Такой подход нужен, чтобы не хранить пароли и адреса БД прямо в коде. В учебном проекте `.env` лежит рядом для удобства проверки, но `.gitignore` исключает env-файлы из индексации.

## Настройка Alembic

Alembic отвечает за создание и изменение таблиц через миграции.

В `alembic.ini` указан путь к папке миграций:

```ini
script_location = migrations
```

Также там оставлено значение:

```ini
sqlalchemy.url = ${DB_ADMIN}
```

Фактическое значение URL передается в `migrations/env.py`:

```python
db_url = os.getenv("DB_ADMIN", "postgresql://postgres:123@localhost/finance_db")
config.set_main_option("sqlalchemy.url", db_url)
```

То есть Alembic берет подключение из `.env`, а не из жестко прописанной строки в `alembic.ini`.

## Модели данных

В проекте используются четыре таблицы:

- `Category`
- `Transaction`
- `Tag`
- `TransactionTagLink`

### Category

Категория дохода или расхода.

Поля:

- `id` — первичный ключ.
- `title` — название категории.
- `description` — описание.
- `monthly_limit` — месячный лимит.

### Transaction

Финансовая операция.

Поля:

- `id` — первичный ключ.
- `transaction_type` — `income` или `expense`.
- `title` — название операции.
- `amount` — сумма.
- `category_id` — внешний ключ на категорию.

### Tag

Метка операции.

Поля:

- `id` — первичный ключ.
- `name` — название.
- `description` — описание.

### TransactionTagLink

Ассоциативная таблица для связи many-to-many между операциями и тегами.

Поля:

- `transaction_id` — внешний ключ на операцию.
- `tag_id` — внешний ключ на тег.
- `importance_level` — дополнительное поле, характеризующее связь.

Поле `importance_level` показывает важность конкретного тега для конкретной операции. Например, один и тот же тег может быть обычным для одной операции и важным для другой.

## Схема базы данных

```mermaid
erDiagram
    CATEGORY ||--o{ TRANSACTION : has
    TRANSACTION ||--o{ TRANSACTION_TAG_LINK : has
    TAG ||--o{ TRANSACTION_TAG_LINK : has

    CATEGORY {
        int id
        string title
        string description
        float monthly_limit
    }

    TRANSACTION {
        int id
        string transaction_type
        string title
        float amount
        int category_id
    }

    TAG {
        int id
        string name
        string description
    }

    TRANSACTION_TAG_LINK {
        int transaction_id
        int tag_id
        int importance_level
    }
```

## Архитектура работы

1. `.env` загружается через `python-dotenv`.
2. `connection.py` создает `engine`.
3. Alembic через `migrations/env.py` получает тот же URL базы данных.
4. Команда `alembic upgrade head` применяет миграции.
5. FastAPI запускается через `uvicorn`.
6. Эндпоинты получают `session` через `Depends(get_session)`.
7. Все операции с БД выполняются через SQLModel.

## Миграция

Файл миграции:

```text
migrations/versions/20260614_0001_initial_finance_schema.py
```

Он создает таблицы:

- `category`
- `tag`
- `transaction`
- `transactiontaglink`

И добавляет поле:

- `importance_level`

Команда применения миграции:

```bash
alembic upgrade head
```

Команда отката миграции:

```bash
alembic downgrade base
```

Команда просмотра истории:

```bash
alembic history
```

## API-эндпоинты

### Операции

| Метод | URL | Назначение |
|---|---|---|
| GET | `/transactions_list` | Получить все операции |
| GET | `/transaction/{transaction_id}` | Получить операцию с категорией и тегами |
| POST | `/transaction` | Создать операцию |
| PATCH | `/transaction{transaction_id}` | Обновить операцию |
| DELETE | `/transaction/delete{transaction_id}` | Удалить операцию |

Пример создания операции:

```json
{
  "transaction_type": "expense",
  "title": "Taxi",
  "amount": 900,
  "category_id": 1
}
```

### Категории

| Метод | URL | Назначение |
|---|---|---|
| GET | `/categories_list` | Получить категории |
| GET | `/category/{category_id}` | Получить категорию |
| POST | `/category` | Создать категорию |
| PATCH | `/category{category_id}` | Обновить категорию |
| DELETE | `/category/delete{category_id}` | Удалить категорию |

Пример:

```json
{
  "title": "Transport",
  "description": "Taxi, metro, fuel and other transport expenses",
  "monthly_limit": 12000
}
```

### Теги

| Метод | URL | Назначение |
|---|---|---|
| GET | `/tags_list` | Получить теги |
| GET | `/tag/{tag_id}` | Получить тег |
| POST | `/tag` | Создать тег |
| PATCH | `/tag{tag_id}` | Обновить тег |
| DELETE | `/tag/delete{tag_id}` | Удалить тег |

Пример:

```json
{
  "name": "cash",
  "description": "Paid by cash"
}
```

### Связь операции и тега

| Метод | URL | Назначение |
|---|---|---|
| POST | `/transaction_tag` | Создать связь операции и тега |
| GET | `/transaction_tags_list` | Получить список связей |
| PATCH | `/transaction/{transaction_id}/tag/{tag_id}` | Обновить поле связи |
| DELETE | `/transaction/{transaction_id}/tag/{tag_id}` | Удалить связь |

Пример создания связи:

```json
{
  "transaction_id": 1,
  "tag_id": 1,
  "importance_level": 5
}
```

Пример обновления важности связи:

```json
{
  "transaction_id": 1,
  "tag_id": 1,
  "importance_level": 10
}
```

## Подготовка БД

Создайте PostgreSQL-базу данных:

```sql
CREATE DATABASE finance_db;
```

Проверьте `.env`:

```text
DB_ADMIN=postgresql://postgres:123@localhost/finance_db
```

Если у вас другой пароль, пользователь, порт или название базы, измените строку подключения.

## Запуск миграций

```bash
cd practice_1_3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

## Запуск приложения

```bash
uvicorn main:app --reload
```

После запуска:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Сценарий проверки

1. Создать базу `finance_db`.
2. Установить зависимости.
3. Выполнить `alembic upgrade head`.
4. Запустить приложение.
5. Создать категорию через `POST /category`.
6. Создать тег через `POST /tag`.
7. Создать операцию через `POST /transaction`.
8. Создать связь операции и тега через `POST /transaction_tag`.
9. Проверить `GET /transaction/{transaction_id}`.
10. Проверить список связей через `GET /transaction_tags_list`.
11. Изменить `importance_level` через `PATCH /transaction/{transaction_id}/tag/{tag_id}`.
12. Удалить связь через `DELETE /transaction/{transaction_id}/tag/{tag_id}`.

## Что было изучено в практике

- использование `.env`;
- исключение чувствительных файлов через `.gitignore`;
- подключение `python-dotenv`;
- настройка Alembic;
- структура папки `migrations`;
- создание файла миграции;
- применение миграций;
- откат миграций;
- передача URL БД в Alembic из `.env`;
- расширение ассоциативной таблицы дополнительным полем;
- поддержка CRUD после перехода на миграции.
