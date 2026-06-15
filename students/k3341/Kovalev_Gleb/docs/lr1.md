# Lab 1

Лабораторная работа 1 — финальная версия серверного приложения на FastAPI по теме управления личными финансами.

Проект находится в отдельной папке `lab_1` и не зависит от практик. Практики показывали постепенное развитие: сначала временная база данных, затем SQLModel и PostgreSQL, затем Alembic, `.env` и `.gitignore`. В лабораторной все эти части собраны в один полноценный backend-проект.

## Цель лабораторной

Цель работы — реализовать серверное приложение, которое:

- использует FastAPI;
- работает с PostgreSQL;
- описывает таблицы через SQLModel;
- использует миграции Alembic;
- имеет 5 или больше таблиц;
- содержит связи one-to-many;
- содержит связь many-to-many;
- имеет ассоциативную таблицу с дополнительным полем;
- реализует CRUD API;
- возвращает вложенные связанные объекты;
- имеет аннотацию типов;
- разделено на файлы по архитектурной логике;
- реализует регистрацию и авторизацию пользователя;
- генерирует JWT-токены;
- проверяет JWT-токены вручную;
- хэширует пароли;
- содержит методы получения пользователя, списка пользователей и смены пароля.

## Предметная область

Тема проекта — сервис управления личными финансами.

Пользователь может:

- зарегистрироваться;
- войти в систему;
- создавать категории доходов и расходов;
- создавать теги для операций;
- добавлять доходы и расходы;
- связывать операции с тегами;
- задавать бюджеты по категориям;
- создавать финансовые цели;
- получать уведомления;
- смотреть финансовый отчет.

## Структура проекта

```text
lab_1/
├── .env
├── .gitignore
├── alembic.ini
├── main.py
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── db.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── finance.py
└── migrations/
    ├── README
    ├── env.py
    ├── script.py.mako
    └── versions/
        └── 20260614_0001_initial_lab_schema.py
```

## Назначение файлов

### `main.py`

Главная точка входа приложения. Здесь создается объект `FastAPI` и подключаются роутеры:

- `auth.router`
- `finance.router`

### `app/db.py`

Файл подключения к базе данных.

Содержит:

- загрузку `.env`;
- чтение переменной `DB_ADMIN`;
- создание `engine`;
- функцию `init_db`;
- зависимость `get_session`.

### `app/models.py`

SQLModel-модели таблиц. Именно эти классы описывают структуру базы данных.

### `app/schemas.py`

Модели запросов и ответов. Они отделены от таблиц, чтобы API не отдавал лишние поля, например `hashed_password`.

### `app/auth.py`

Логика безопасности:

- хэширование пароля;
- проверка пароля;
- ручная генерация JWT;
- ручная проверка JWT.

JWT реализован вручную через:

- `base64`;
- `json`;
- `hmac`;
- `hashlib.sha256`;
- поле `exp` для срока жизни токена.

### `app/dependencies.py`

Зависимости FastAPI:

- `oauth2_scheme`;
- `get_current_user`.

`get_current_user` достает Bearer-токен, проверяет JWT, получает пользователя из базы и запрещает доступ, если токен неверный.

### `app/routers/auth.py`

Эндпоинты регистрации, входа и работы с пользователем.

### `app/routers/finance.py`

Все финансовые эндпоинты:

- категории;
- теги;
- операции;
- связи операций и тегов;
- бюджеты;
- цели;
- уведомления;
- отчет.

### `migrations`

Папка Alembic. В ней находится миграция, создающая все таблицы лабораторной.

## Используемые технологии

- Python 3.10+
- FastAPI
- SQLModel
- SQLAlchemy
- PostgreSQL
- Alembic
- python-dotenv
- psycopg2-binary
- Uvicorn

## Таблицы базы данных

В лабораторной реализовано 8 таблиц:

- `app_user`
- `category`
- `tag`
- `transaction`
- `transaction_tag_link`
- `budget`
- `goal`
- `notification`

Это больше минимального требования в 5 таблиц.

## Модели и поля

### app_user

Пользователь системы.

Поля:

- `id` — первичный ключ.
- `username` — логин пользователя.
- `email` — email.
- `hashed_password` — хэш пароля.
- `is_active` — активен ли пользователь.

Связи:

- пользователь имеет много категорий;
- пользователь имеет много тегов;
- пользователь имеет много операций;
- пользователь имеет много бюджетов;
- пользователь имеет много целей;
- пользователь имеет много уведомлений.

### category

Категория финансовых операций.

Поля:

- `id` — первичный ключ.
- `title` — название.
- `description` — описание.
- `monthly_limit` — месячный лимит.
- `user_id` — владелец категории.

Связи:

- категория принадлежит пользователю;
- категория может иметь много операций;
- категория может иметь много бюджетов.

### tag

Тег операции.

Поля:

- `id` — первичный ключ.
- `name` — название.
- `description` — описание.
- `user_id` — владелец тега.

Связи:

- тег принадлежит пользователю;
- тег может быть связан со многими операциями.

### transaction

Финансовая операция.

Поля:

- `id` — первичный ключ.
- `transaction_type` — `income` или `expense`.
- `title` — название.
- `amount` — сумма.
- `operation_date` — дата операции.
- `description` — необязательное описание.
- `user_id` — владелец операции.
- `category_id` — категория операции.

Связи:

- операция принадлежит пользователю;
- операция может относиться к категории;
- операция может иметь много тегов.

### transaction_tag_link

Ассоциативная таблица many-to-many между операциями и тегами.

Поля:

- `transaction_id` — внешний ключ на операцию.
- `tag_id` — внешний ключ на тег.
- `importance_level` — дополнительное поле, характеризующее связь.

Это поле нужно по требованиям лабораторной: ассоциативная сущность должна иметь поле помимо ссылок на связанные таблицы.

### budget

Бюджет пользователя.

Поля:

- `id` — первичный ключ.
- `title` — название бюджета.
- `amount` — сумма бюджета.
- `period_start` — начало периода.
- `period_end` — конец периода.
- `user_id` — владелец бюджета.
- `category_id` — категория бюджета.

Связи:

- бюджет принадлежит пользователю;
- бюджет может быть связан с категорией.

### goal

Финансовая цель.

Поля:

- `id` — первичный ключ.
- `title` — название цели.
- `target_amount` — целевая сумма.
- `current_amount` — текущий прогресс.
- `deadline` — дедлайн.
- `is_completed` — выполнена ли цель.
- `user_id` — владелец цели.

### notification

Уведомление пользователя.

Поля:

- `id` — первичный ключ.
- `title` — заголовок.
- `message` — текст уведомления.
- `is_read` — прочитано ли уведомление.
- `created_at` — дата создания.
- `user_id` — владелец уведомления.

## Схема базы данных

```mermaid
erDiagram
    APP_USER ||--o{ CATEGORY : owns
    APP_USER ||--o{ TAG : owns
    APP_USER ||--o{ TRANSACTION : owns
    APP_USER ||--o{ BUDGET : owns
    APP_USER ||--o{ GOAL : owns
    APP_USER ||--o{ NOTIFICATION : owns
    CATEGORY ||--o{ TRANSACTION : groups
    CATEGORY ||--o{ BUDGET : limits
    TRANSACTION ||--o{ TRANSACTION_TAG_LINK : has
    TAG ||--o{ TRANSACTION_TAG_LINK : marks

    APP_USER {
        int id
        string username
        string email
        string hashed_password
        bool is_active
    }

    CATEGORY {
        int id
        string title
        string description
        float monthly_limit
        int user_id
    }

    TAG {
        int id
        string name
        string description
        int user_id
    }

    TRANSACTION {
        int id
        string transaction_type
        string title
        float amount
        date operation_date
        string description
        int user_id
        int category_id
    }

    TRANSACTION_TAG_LINK {
        int transaction_id
        int tag_id
        int importance_level
    }

    BUDGET {
        int id
        string title
        float amount
        date period_start
        date period_end
        int user_id
        int category_id
    }

    GOAL {
        int id
        string title
        float target_amount
        float current_amount
        date deadline
        bool is_completed
        int user_id
    }

    NOTIFICATION {
        int id
        string title
        string message
        bool is_read
        datetime created_at
        int user_id
    }
```

## Архитектура приложения

Приложение разделено на несколько слоев.

### Слой моделей

Файл `app/models.py` содержит таблицы базы данных. Эти модели используются SQLModel и Alembic.

### Слой схем API

Файл `app/schemas.py` содержит модели запросов и ответов. Это нужно, чтобы:

- не принимать лишние поля от клиента;
- не возвращать служебные поля;
- отделить API-контракт от таблиц базы данных;
- описать вложенные ответы.

### Слой авторизации

Файл `app/auth.py` отвечает за пароли и токены.

Алгоритм регистрации:

1. Пользователь отправляет username, email и password.
2. Приложение проверяет, что username или email не заняты.
3. Пароль хэшируется.
4. Пользователь сохраняется в БД.

Алгоритм входа:

1. Пользователь отправляет username и password.
2. Приложение ищет пользователя.
3. Пароль сравнивается с хэшем.
4. Если данные верные, создается JWT.

Алгоритм проверки защищенного запроса:

1. Клиент отправляет заголовок `Authorization: Bearer <token>`.
2. FastAPI достает токен через `OAuth2PasswordBearer`.
3. `decode_access_token` проверяет подпись и срок жизни.
4. `get_current_user` получает пользователя из БД.
5. Эндпоинт выполняется только для авторизованного пользователя.

### Слой роутеров

Роутеры разделены на две части:

- `app/routers/auth.py` — пользователь и безопасность.
- `app/routers/finance.py` — предметная область личных финансов.

### Слой миграций

Alembic использует:

- `alembic.ini`;
- `migrations/env.py`;
- `migrations/versions/20260614_0001_initial_lab_schema.py`.

Миграция создает все таблицы и индексы.

## Переменные окружения

Файл `.env`:

```text
DB_ADMIN=postgresql://postgres:123@localhost/finance_lab_db
JWT_SECRET=finance-lab-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Назначение:

- `DB_ADMIN` — строка подключения к PostgreSQL.
- `JWT_SECRET` — секрет для подписи JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES` — срок жизни токена.

## API авторизации

### Регистрация

```http
POST /auth/register
```

Тело запроса:

```json
{
  "username": "ivan",
  "email": "ivan@example.com",
  "password": "qwerty123"
}
```

Пример ответа:

```json
{
  "status": 200,
  "data": {
    "id": 1,
    "username": "ivan",
    "email": "ivan@example.com",
    "is_active": true
  }
}
```

### Вход

```http
POST /auth/login
```

Тело запроса:

```json
{
  "username": "ivan",
  "password": "qwerty123"
}
```

Пример ответа:

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

После входа в Swagger нужно нажать `Authorize` и вставить токен. Если Swagger сам не добавляет префикс, вставьте:

```text
Bearer jwt_token_here
```

### Текущий пользователь

```http
GET /auth/me
```

Возвращает данные пользователя по JWT.

### Список пользователей

```http
GET /auth/users
```

Возвращает список пользователей. Эндпоинт защищен JWT.

### Смена пароля

```http
PATCH /auth/change_password
```

Тело запроса:

```json
{
  "old_password": "qwerty123",
  "new_password": "new_password_123"
}
```

## API финансовой части

Все финансовые эндпоинты защищены JWT. Сущности принадлежат текущему пользователю, поэтому пользователь не может получить или изменить чужие категории, операции, бюджеты, цели, теги и уведомления.

### Категории

| Метод | URL | Назначение |
|---|---|---|
| GET | `/categories_list` | Список категорий пользователя |
| GET | `/category/{category_id}` | Получить категорию |
| POST | `/category` | Создать категорию |
| PATCH | `/category{category_id}` | Обновить категорию |
| DELETE | `/category/delete{category_id}` | Удалить категорию |

Пример создания:

```json
{
  "title": "Food",
  "description": "Groceries and cafes",
  "monthly_limit": 30000
}
```

### Теги

| Метод | URL | Назначение |
|---|---|---|
| GET | `/tags_list` | Список тегов |
| GET | `/tag/{tag_id}` | Получить тег |
| POST | `/tag` | Создать тег |
| PATCH | `/tag{tag_id}` | Обновить тег |
| DELETE | `/tag/delete{tag_id}` | Удалить тег |

Пример создания:

```json
{
  "name": "card",
  "description": "Paid by bank card"
}
```

### Операции

| Метод | URL | Назначение |
|---|---|---|
| GET | `/transactions_list` | Список операций |
| GET | `/transaction/{transaction_id}` | Получить операцию с категорией и тегами |
| POST | `/transaction` | Создать операцию |
| PATCH | `/transaction{transaction_id}` | Обновить операцию |
| DELETE | `/transaction/delete{transaction_id}` | Удалить операцию |

Пример создания расхода:

```json
{
  "transaction_type": "expense",
  "title": "Groceries",
  "amount": 4500,
  "operation_date": "2026-06-14",
  "description": "Weekly groceries",
  "category_id": 1
}
```

Пример создания дохода:

```json
{
  "transaction_type": "income",
  "title": "Salary",
  "amount": 150000,
  "operation_date": "2026-06-14",
  "description": "June salary",
  "category_id": 2
}
```

Пример вложенного ответа:

```json
{
  "transaction_type": "expense",
  "title": "Groceries",
  "amount": 4500,
  "operation_date": "2026-06-14",
  "description": "Weekly groceries",
  "category_id": 1,
  "id": 1,
  "user_id": 1,
  "category": {
    "title": "Food",
    "description": "Groceries and cafes",
    "monthly_limit": 30000,
    "id": 1,
    "user_id": 1
  },
  "tags": [
    {
      "name": "card",
      "description": "Paid by bank card",
      "id": 1,
      "user_id": 1
    }
  ]
}
```

### Связь операции и тега

| Метод | URL | Назначение |
|---|---|---|
| POST | `/transaction_tag` | Создать связь операции и тега |
| GET | `/transaction_tags_list` | Получить связи пользователя |
| PATCH | `/transaction/{transaction_id}/tag/{tag_id}` | Обновить важность связи |
| DELETE | `/transaction/{transaction_id}/tag/{tag_id}` | Удалить связь |

Пример создания связи:

```json
{
  "transaction_id": 1,
  "tag_id": 1,
  "importance_level": 5
}
```

Пример обновления:

```json
{
  "transaction_id": 1,
  "tag_id": 1,
  "importance_level": 9
}
```

### Бюджеты

| Метод | URL | Назначение |
|---|---|---|
| GET | `/budgets_list` | Список бюджетов |
| GET | `/budget/{budget_id}` | Получить бюджет |
| POST | `/budget` | Создать бюджет |
| PATCH | `/budget{budget_id}` | Обновить бюджет |
| DELETE | `/budget/delete{budget_id}` | Удалить бюджет |

Пример создания:

```json
{
  "title": "Food budget for June",
  "amount": 30000,
  "period_start": "2026-06-01",
  "period_end": "2026-06-30",
  "category_id": 1
}
```

### Цели

| Метод | URL | Назначение |
|---|---|---|
| GET | `/goals_list` | Список целей |
| GET | `/goal/{goal_id}` | Получить цель |
| POST | `/goal` | Создать цель |
| PATCH | `/goal{goal_id}` | Обновить цель |
| DELETE | `/goal/delete{goal_id}` | Удалить цель |

Пример создания:

```json
{
  "title": "Emergency fund",
  "target_amount": 200000,
  "current_amount": 25000,
  "deadline": "2026-12-31",
  "is_completed": false
}
```

### Уведомления

| Метод | URL | Назначение |
|---|---|---|
| GET | `/notifications_list` | Список уведомлений |
| GET | `/notification/{notification_id}` | Получить уведомление |
| POST | `/notification` | Создать уведомление |
| PATCH | `/notification{notification_id}` | Обновить уведомление |
| DELETE | `/notification/delete{notification_id}` | Удалить уведомление |

Пример создания:

```json
{
  "title": "Budget warning",
  "message": "Food budget is almost exceeded",
  "is_read": false
}
```

### Отчет

```http
GET /report
```

Отчет считает:

- сумму доходов;
- сумму расходов;
- баланс;
- количество бюджетов;
- количество целей;
- количество непрочитанных уведомлений.

Пример ответа:

```json
{
  "total_income": 150000,
  "total_expense": 4500,
  "balance": 145500,
  "budgets_count": 1,
  "goals_count": 1,
  "unread_notifications_count": 1
}
```

## Подготовка базы данных

Создайте базу:

```sql
CREATE DATABASE finance_lab_db;
```

Проверьте `.env`:

```text
DB_ADMIN=postgresql://postgres:123@localhost/finance_lab_db
JWT_SECRET=finance-lab-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Если PostgreSQL использует другой пароль или пользователя, измените `DB_ADMIN`.

## Запуск проекта

```bash
cd lab_1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

После запуска:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Сценарий полной проверки

1. Создать PostgreSQL-базу `finance_lab_db`.
2. Установить зависимости.
3. Выполнить `alembic upgrade head`.
4. Запустить `uvicorn main:app --reload`.
5. Открыть `http://127.0.0.1:8000/docs`.
6. Зарегистрировать пользователя через `POST /auth/register`.
7. Войти через `POST /auth/login`.
8. Нажать `Authorize` в Swagger и вставить токен.
9. Создать категорию `Food`.
10. Создать тег `card`.
11. Создать операцию `Groceries`.
12. Создать связь операции и тега через `POST /transaction_tag`.
13. Проверить вложенный ответ через `GET /transaction/{transaction_id}`.
14. Создать бюджет через `POST /budget`.
15. Создать цель через `POST /goal`.
16. Создать уведомление через `POST /notification`.
17. Проверить отчет через `GET /report`.
18. Проверить текущего пользователя через `GET /auth/me`.
19. Проверить список пользователей через `GET /auth/users`.
20. Сменить пароль через `PATCH /auth/change_password`.

## Проверка миграций

Применить миграции:

```bash
alembic upgrade head
```

Посмотреть историю:

```bash
alembic history
```

Откатить миграции:

```bash
alembic downgrade base
```

## Почему архитектура сделана так

Проект разделен не случайно:

- модели таблиц лежат отдельно, чтобы Alembic и SQLModel могли работать с ними напрямую;
- схемы API отделены от таблиц, чтобы не отдавать пароль и служебные поля;
- авторизация вынесена отдельно, потому что это самостоятельная логика;
- зависимости FastAPI вынесены отдельно, чтобы защищенные эндпоинты не дублировали проверку токена;
- финансовые маршруты отделены от маршрутов авторизации;
- миграции лежат отдельно, чтобы изменения БД были контролируемыми.

Такая структура проще поддерживается и лучше соответствует требованиям лабораторной к оформленной файловой структуре проекта.

## Что было выполнено по требованиям

| Требование | Выполнение |
|---|---|
| FastAPI-приложение | Да |
| PostgreSQL | Да |
| SQLModel ORM | Да |
| 5 или больше таблиц | Да, 8 таблиц |
| one-to-many | Да |
| many-to-many | Да |
| Ассоциативная сущность с дополнительным полем | Да, `importance_level` |
| CRUD API | Да |
| Вложенные объекты в GET | Да |
| Alembic | Да |
| Аннотация типов | Да |
| Разделение по файлам | Да |
| Регистрация | Да |
| Авторизация | Да |
| JWT | Да |
| Ручная проверка JWT | Да |
| Хэширование паролей | Да |
| Получение текущего пользователя | Да |
| Список пользователей | Да |
| Смена пароля | Да |

## Дополнительная работа: фронтенд, тесты и тестовая среда

После выполнения основной лабораторной работы был добавлен дополнительный слой: пользовательский фронтенд, автоматические тесты и отдельная тестовая среда. Это не заменяет основную серверную часть, а расширяет ее.

Основная PostgreSQL-среда остается рабочей средой лабораторной. Для тестов и демонстрации фронтенда можно использовать отдельную SQLite-базу в `/private/tmp`, чтобы не портить реальные данные.

## Фронтенд

Фронтенд встроен прямо в FastAPI-приложение и доступен по адресу:

```text
http://127.0.0.1:8000/app
```

Файлы фронтенда:

```text
app/frontend/
├── index.html
└── static/
    ├── app.js
    └── styles.css
```

Подключение фронтенда выполнено в `main.py`:

```python
app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")
```

Страница `/app` возвращает HTML-файл:

```python
@app.get("/app", response_class=FileResponse)
def frontend() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")
```

### Что есть во фронтенде

Фронтенд представляет собой рабочую панель управления личными финансами:

- блок регистрации;
- блок входа;
- сохранение JWT в `localStorage`;
- кнопка выхода;
- обновление данных из API;
- карточки статистики по доходам, расходам, балансу и уведомлениям;
- форма создания категории;
- форма создания тега;
- форма создания операции;
- форма связи операции и тега;
- форма создания бюджета;
- форма создания цели;
- форма создания уведомления;
- таблица операций;
- списки категорий, тегов, бюджетов, целей и уведомлений;
- ссылка на Swagger.

Фронтенд не использует отдельный фреймворк. Он написан на HTML, CSS и JavaScript, чтобы проект было проще открыть в PyCharm и запустить вместе с FastAPI.

### Архитектура фронтенда

Фронтенд работает так:

1. Пользователь открывает `/app`.
2. JavaScript проверяет JWT в `localStorage`.
3. Если токен есть, фронтенд делает запросы к защищенным API-ручкам.
4. Если токена нет, пользователь регистрируется или входит.
5. После входа JWT сохраняется в `localStorage`.
6. Все последующие запросы отправляются с заголовком:

```text
Authorization: Bearer <token>
```

7. Данные отрисовываются в карточках, таблицах и списках.

### Использованные API во фронтенде

Фронтенд обращается к следующим ручкам:

| Ручка | Назначение |
|---|---|
| `POST /auth/register` | регистрация |
| `POST /auth/login` | вход и получение JWT |
| `GET /categories_list` | список категорий |
| `POST /category` | создание категории |
| `GET /tags_list` | список тегов |
| `POST /tag` | создание тега |
| `GET /transactions_list` | список операций |
| `POST /transaction` | создание операции |
| `POST /transaction_tag` | связь операции и тега |
| `GET /budgets_list` | список бюджетов |
| `POST /budget` | создание бюджета |
| `GET /goals_list` | список целей |
| `POST /goal` | создание цели |
| `GET /notifications_list` | список уведомлений |
| `POST /notification` | создание уведомления |
| `GET /report` | финансовая сводка |

### Дизайн фронтенда

Дизайн сделан по файлу `DESIGN (3).md`.

Использованные принципы:

- теплый фон `#e2e2df`;
- cream-панели `#f7f6f2`;
- почти черный текст `#070607`;
- оранжевый `#fc5000` только для основных действий и stat-карточек;
- большие condensed-заголовки;
- крупный радиус `40px`;
- pill-навигация;
- отсутствие теней;
- halftone-панель в hero-блоке;
- плоская editorial/zine-эстетика.

Главный экран не является лендингом. Это рабочая панель приложения: сразу доступны авторизация, отчеты, формы и списки данных.

## Тестовая среда

Для дополнительной работы добавлена отдельная тестовая среда на SQLite. Она не использует основную PostgreSQL-базу `finance_lab_db`.

Тестовая база для pytest:

```text
sqlite:////private/tmp/finance_lab_test.db
```

Демо-база для ручной проверки фронтенда:

```text
sqlite:////private/tmp/finance_lab_frontend.db
```

Файл наполнения демо-среды:

```text
scripts/seed_test_data.py
```

Он создает:

- пользователя `demo`;
- пароль `demo12345`;
- категории `Food` и `Salary`;
- теги `card` и `regular`;
- доход `June salary`;
- расход `Groceries`;
- связи операций и тегов;
- бюджет;
- цель;
- уведомление.

### Запуск фронтенда на тестовой SQLite-среде

```bash
cd lab_1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DB_ADMIN=sqlite:////private/tmp/finance_lab_frontend.db python scripts/seed_test_data.py
DB_ADMIN=sqlite:////private/tmp/finance_lab_frontend.db JWT_SECRET=frontend-test-secret uvicorn main:app --reload
```

После запуска:

```text
http://127.0.0.1:8000/app
```

Данные для входа:

```text
demo / demo12345
```

## Тесты

Тесты находятся в папке:

```text
tests/
├── conftest.py
├── test_auth.py
├── test_finance.py
└── test_frontend.py
```

Тесты запускаются на отдельной SQLite-базе. Перед каждым тестом таблицы удаляются и создаются заново, поэтому тесты не зависят от основной PostgreSQL-среды и не портят реальные данные.

### Что проверяют тесты

Файл `test_auth.py` проверяет:

- регистрацию;
- вход;
- получение текущего пользователя;
- смену пароля;
- повторную авторизацию с новым паролем;
- список пользователей;
- ошибку при повторной регистрации.

Файл `test_finance.py` проверяет все финансовые ручки:

- CRUD категорий;
- CRUD тегов;
- CRUD операций;
- CRUD связи операции и тега;
- CRUD бюджетов;
- CRUD целей;
- CRUD уведомлений;
- отчет `/report`;
- запрет доступа без JWT.

Файл `test_frontend.py` проверяет:

- выдачу страницы `/app`;
- подключение CSS;
- подключение JS;
- выдачу static-файлов;
- базовую ручку `/`.

### Покрытие ручек тестами

Тесты вызывают все ручки проекта:

| Группа | Ручки |
|---|---|
| Базовые | `/`, `/app`, `/static/styles.css`, `/static/app.js` |
| Auth | `/auth/register`, `/auth/login`, `/auth/me`, `/auth/users`, `/auth/change_password` |
| Category | `/categories_list`, `/category/{id}`, `/category`, `/category{id}`, `/category/delete{id}` |
| Tag | `/tags_list`, `/tag/{id}`, `/tag`, `/tag{id}`, `/tag/delete{id}` |
| Transaction | `/transactions_list`, `/transaction/{id}`, `/transaction`, `/transaction{id}`, `/transaction/delete{id}` |
| TransactionTagLink | `/transaction_tag`, `/transaction_tags_list`, `/transaction/{transaction_id}/tag/{tag_id}` |
| Budget | `/budgets_list`, `/budget/{id}`, `/budget`, `/budget{id}`, `/budget/delete{id}` |
| Goal | `/goals_list`, `/goal/{id}`, `/goal`, `/goal{id}`, `/goal/delete{id}` |
| Notification | `/notifications_list`, `/notification/{id}`, `/notification`, `/notification{id}`, `/notification/delete{id}` |
| Report | `/report` |

### Запуск тестов

```bash
cd lab_1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Проверенный результат:

```text
14 passed
```
