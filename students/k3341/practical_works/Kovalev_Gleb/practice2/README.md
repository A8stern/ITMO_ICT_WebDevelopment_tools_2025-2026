# Practice 1.2

Практика 1.2 является развитием первой практики. В первой версии данные хранились в обычных Python-списках, а здесь проект переводится на настоящую базу данных PostgreSQL и ORM SQLModel.

Проект по-прежнему реализован по теме сервиса управления личными финансами и находится в отдельной папке. Он не зависит от `practice_1_1`.

## Цель практики

Цель этой практики — научиться:

- подключать FastAPI-приложение к PostgreSQL;
- описывать таблицы через SQLModel;
- создавать связи между таблицами;
- работать с сессиями БД через `Depends`;
- реализовывать CRUD уже не через списки, а через ORM;
- возвращать вложенные объекты через `response_model`.

## Структура проекта

```text
practice_1_2/
├── connection.py
├── main.py
├── models.py
├── requirements.txt
└── README.md
```

Назначение файлов:

- `connection.py` — строка подключения к PostgreSQL, движок SQLModel, создание таблиц и генератор сессий.
- `models.py` — SQLModel-модели таблиц, модели для запросов и модели для ответов.
- `main.py` — FastAPI-приложение и все API-эндпоинты.
- `requirements.txt` — зависимости проекта.
- `README.md` — описание архитектуры и примеры использования.

## Используемые технологии

- FastAPI — веб-фреймворк.
- SQLModel — ORM-библиотека от автора FastAPI.
- SQLAlchemy — используется внутри SQLModel.
- PostgreSQL — СУБД.
- psycopg2-binary — драйвер PostgreSQL для Python.
- Uvicorn — сервер для запуска FastAPI.

## Подключение к базе данных

В `connection.py` описано подключение:

```python
db_url = "postgresql://postgres:123@localhost/finance_db"
engine = create_engine(db_url, echo=True)
```

`engine` отвечает за подключение к базе. Параметр `echo=True` выводит SQL-запросы в консоль, что удобно для учебной работы.

Функция `init_db` создает таблицы:

```python
def init_db() -> None:
    SQLModel.metadata.create_all(engine)
```

Функция `get_session` используется как зависимость FastAPI:

```python
def get_session():
    with Session(engine) as session:
        yield session
```

Каждый эндпоинт, которому нужна база данных, получает `session` через `Depends(get_session)`.

## Модели данных

В практике реализованы четыре таблицы:

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

Связи:

- одна категория может иметь много операций.

### Transaction

Финансовая операция.

Поля:

- `id` — первичный ключ.
- `transaction_type` — тип операции: `income` или `expense`.
- `title` — название.
- `amount` — сумма.
- `category_id` — внешний ключ на категорию.

Связи:

- операция относится к одной категории;
- операция может иметь много тегов.

### Tag

Метка операции.

Поля:

- `id` — первичный ключ.
- `name` — название.
- `description` — описание.

Связи:

- тег может быть привязан ко многим операциям.

### TransactionTagLink

Ассоциативная таблица для связи many-to-many.

Поля:

- `transaction_id` — внешний ключ на операцию.
- `tag_id` — внешний ключ на тег.

В этой практике связь many-to-many уже вынесена в отдельную таблицу. Дополнительное поле для связи появляется в практике 1.3.

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
    }
```

## Архитектура работы

1. Клиент отправляет запрос в FastAPI.
2. FastAPI валидирует тело запроса через SQLModel/Pydantic-модель.
3. Через `Depends(get_session)` создается сессия БД.
4. Эндпоинт выполняет ORM-операцию: `select`, `session.add`, `session.commit`, `session.refresh` или `session.delete`.
5. FastAPI сериализует ответ.
6. Если указан `response_model`, вложенные объекты возвращаются в нужном формате.

## Особенности реализации

### Создание таблиц при старте

В `main.py` используется обработчик старта:

```python
@app.on_event("startup")
def on_startup() -> None:
    init_db()
```

Это значит, что при запуске приложения SQLModel проверит модели и создаст таблицы, если их еще нет.

### Модели для создания и чтения

В проекте разделены модели таблиц и модели запросов:

- `CategoryDefault` — данные для создания/обновления категории.
- `Category` — таблица в базе данных.
- `CategoryRead` — ответ API.

Такой же подход используется для тегов и операций.

### Вложенная выдача

Для операции используется `TransactionRead`:

```python
class TransactionRead(TransactionDefault):
    id: int
    category: Optional[CategoryRead] = None
    tags: List[TagRead] = Field(default_factory=list)
```

Поэтому при запросе операции можно увидеть не только `category_id`, но и вложенную категорию, а также список тегов.

## API-эндпоинты

### Операции

| Метод | URL | Назначение |
|---|---|---|
| GET | `/transactions_list` | Получить все операции |
| GET | `/transaction/{transaction_id}` | Получить операцию по id с вложенными объектами |
| POST | `/transaction` | Создать операцию |
| PATCH | `/transaction{transaction_id}` | Частично обновить операцию |
| DELETE | `/transaction/delete{transaction_id}` | Удалить операцию |

Пример создания операции:

```json
{
  "transaction_type": "expense",
  "title": "Groceries",
  "amount": 4500,
  "category_id": 1
}
```

Пример ответа при получении операции:

```json
{
  "transaction_type": "expense",
  "title": "Groceries",
  "amount": 4500,
  "category_id": 1,
  "id": 1,
  "category": {
    "title": "Food",
    "description": "Groceries, cafes and other food expenses",
    "monthly_limit": 30000,
    "id": 1
  },
  "tags": []
}
```

### Категории

| Метод | URL | Назначение |
|---|---|---|
| GET | `/categories_list` | Получить все категории |
| GET | `/category/{category_id}` | Получить категорию |
| POST | `/category` | Создать категорию |
| PATCH | `/category{category_id}` | Обновить категорию |
| DELETE | `/category/delete{category_id}` | Удалить категорию |

Пример создания категории:

```json
{
  "title": "Food",
  "description": "Groceries, cafes and other food expenses",
  "monthly_limit": 30000
}
```

### Теги

| Метод | URL | Назначение |
|---|---|---|
| GET | `/tags_list` | Получить все теги |
| GET | `/tag/{tag_id}` | Получить тег |
| POST | `/tag` | Создать тег |
| PATCH | `/tag{tag_id}` | Обновить тег |
| DELETE | `/tag/delete{tag_id}` | Удалить тег |

Пример создания тега:

```json
{
  "name": "card",
  "description": "Paid by bank card"
}
```

### Связь операции и тега

| Метод | URL | Назначение |
|---|---|---|
| POST | `/transaction/{transaction_id}/tag/{tag_id}` | Добавить тег к операции |
| DELETE | `/transaction/{transaction_id}/tag/{tag_id}` | Удалить тег у операции |

Пример:

```text
POST /transaction/1/tag/2
```

После этого при запросе `GET /transaction/1` тег будет отображаться внутри поля `tags`.

## Подготовка БД

Создайте PostgreSQL-базу данных:

```sql
CREATE DATABASE finance_db;
```

По умолчанию приложение использует строку подключения:

```text
postgresql://postgres:123@localhost/finance_db
```

Если у вас другой пользователь, пароль, порт или имя базы, измените `db_url` в `connection.py`.

## Запуск

```bash
cd practice_1_2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

После запуска:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Сценарий проверки

1. Создать базу `finance_db`.
2. Запустить приложение.
3. Создать категорию через `POST /category`.
4. Создать тег через `POST /tag`.
5. Создать операцию через `POST /transaction`, передав `category_id`.
6. Привязать тег к операции через `POST /transaction/{transaction_id}/tag/{tag_id}`.
7. Проверить вложенный ответ через `GET /transaction/{transaction_id}`.
8. Обновить операцию через `PATCH /transaction{transaction_id}`.
9. Удалить связь тега и операции.
10. Удалить тестовые данные.

## Что было изучено в практике

- подключение PostgreSQL к FastAPI;
- создание `engine`;
- работа с `Session`;
- внедрение зависимостей через `Depends`;
- описание таблиц через `SQLModel`;
- описание первичных и внешних ключей;
- связь one-to-many;
- связь many-to-many через ассоциативную таблицу;
- выполнение SELECT-запросов через `select`;
- создание, обновление и удаление записей через ORM;
- вложенная сериализация ответов через `response_model`.
