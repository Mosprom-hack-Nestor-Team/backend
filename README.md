# Backend API

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)

Современный FastAPI backend с чистой архитектурой и компонентным подходом

</div>

---

## 📋 Содержание

- [О проекте](#о-проекте)
- [Структура проекта](#структура-проекта)
- [Технологии](#технологии)
- [Установка](#установка)
- [Запуск проекта](#запуск-проекта)
- [API Документация](#api-документация)
- [Разработка](#разработка)

---

## 🎯 О проекте

Это современный backend сервис, построенный на **FastAPI** с соблюдением принципов чистой архитектуры и компонентного подхода. Проект включает:

- ✅ Модульная архитектура с разделением на слои
- ✅ Автоматическая документация API (Swagger/ReDoc)
- ✅ Типизация с использованием Pydantic
- ✅ Настраиваемая конфигурация через переменные окружения
- ✅ CORS middleware для работы с фронтендом
- ✅ Health check endpoint

---

## 📁 Структура проекта

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Точка входа приложения
│   ├── core/                   # Ядро приложения
│   │   ├── __init__.py
│   │   └── config.py          # Конфигурация и настройки
│   └── api/                   # API слой
│       ├── __init__.py
│       └── v1/                # Версия API v1
│           ├── __init__.py
│           ├── router.py      # Главный роутер API
│           └── endpoints/     # Эндпоинты
│               ├── __init__.py
│               └── health.py  # Health check endpoint
├── .env.example               # Пример переменных окружения
├── .gitignore                 # Git ignore файл
├── requirements.txt           # Зависимости Python
└── README.md                  # Документация
```

### Принципы архитектуры:

- **`app/core/`** - базовые компоненты (конфигурация, утилиты)
- **`app/api/`** - API endpoints, роутеры
- **`app/api/v1/endpoints/`** - версионированные эндпоинты

---

## 🛠 Технологии

- **[FastAPI](https://fastapi.tiangolo.com/)** - современный веб-фреймворк
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI сервер
- **[Pydantic](https://docs.pydantic.dev/)** - валидация данных и настройки
- **[Python 3.9+](https://www.python.org/)** - язык программирования

---

## 📦 Установка

### Требования

- Python 3.9 или выше
- pip (менеджер пакетов Python)
- Docker и Docker Compose (для запуска PostgreSQL)

### Шаги установки

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   ```

3. **Активируйте виртуальное окружение:**
   
   На macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   На Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Создайте файл `.env`:**
   ```bash
   cp .env.example .env
   ```
   
   Отредактируйте `.env` под ваши нужды. **ВАЖНО:** Измените `JWT_SECRET_KEY` на случайную строку минимум 32 символа!

6. **Запустите PostgreSQL в Docker:**
   ```bash
   docker-compose up -d
   ```
   
   Эта команда поднимет PostgreSQL базу данных в фоновом режиме.

---

## 🚀 Запуск проекта

### Запуск базы данных и pgAdmin

Перед запуском приложения убедитесь, что PostgreSQL и pgAdmin запущены:

```bash
docker-compose up -d
```

Это запустит два контейнера:
- **PostgreSQL** на порту `5432`
- **pgAdmin4** на порту `5050`

Проверка статуса:
```bash
docker-compose ps
```

Просмотр логов:
```bash
docker-compose logs -f postgres
docker-compose logs -f pgadmin
```

### Запуск backend приложения

#### Простой запуск (рекомендуется)

```bash
python3 run.py
```

#### Альтернативный запуск через uvicorn

Режим разработки:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 7878
```

Режим продакшн:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 7878 --workers 4
```

После запуска:
- Сервер будет доступен по адресу: **http://localhost:7878**
- При первом запуске автоматически создадутся таблицы в БД

### Остановка проекта

Остановка backend:
```bash
# Нажмите Ctrl+C в терминале с запущенным приложением
```

Остановка базы данных:
```bash
docker-compose down
```

Полная очистка (включая данные):
```bash
docker-compose down -v
```

---

## �️ Работа с pgAdmin4

### Доступ к pgAdmin

После запуска `docker-compose up -d`, pgAdmin будет доступен по адресу:

**http://localhost:5050**

### Данные для входа в pgAdmin:

- **Email:** `admin@admin.com`
- **Password:** `admin`

### Подключение к базе данных через pgAdmin:

1. **Откройте pgAdmin** в браузере (http://localhost:5050)

2. **Войдите** используя данные выше

3. **Добавьте новый сервер:**
   - Кликните правой кнопкой на "Servers" → "Register" → "Server"

4. **Вкладка "General":**
   - **Name:** `Hackk Database` (или любое имя)

5. **Вкладка "Connection":**
   - **Host name/address:** `postgres` (имя сервиса из docker-compose)
   - **Port:** `5432`
   - **Maintenance database:** `appdb`
   - **Username:** `appuser`
   - **Password:** `apppassword`
   - ✅ Отметьте "Save password"

6. **Нажмите "Save"**

7. **Просмотр таблиц:**
   - Разверните: `Servers` → `Hackk Database` → `Databases` → `appdb` → `Schemas` → `public` → `Tables`
   - Здесь вы увидите таблицы: `users` и `tokens`

### Полезные запросы в pgAdmin:

Просмотр всех пользователей:
```sql
SELECT id, name, email, role, created_at FROM users;
```

Просмотр активных токенов:
```sql
SELECT t.id, t.user_id, u.email, t.expires_at, t.created_at 
FROM tokens t 
JOIN users u ON t.user_id = u.id 
WHERE t.expires_at > NOW();
```

Очистка истекших токенов:
```sql
DELETE FROM tokens WHERE expires_at < NOW();
```

---

## �📚 API Документация

После запуска проекта документация доступна по следующим адресам:

- **Swagger UI:** [http://localhost:7878/api/v1/docs](http://localhost:7878/api/v1/docs)
- **ReDoc:** [http://localhost:7878/api/v1/redoc](http://localhost:7878/api/v1/redoc)
- **OpenAPI Schema:** [http://localhost:7878/api/v1/openapi.json](http://localhost:7878/api/v1/openapi.json)

### Доступные эндпоинты

#### Health Check

Проверка работоспособности API:

```http
GET /api/v1/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "message": "API is running successfully",
  "timestamp": "2025-10-17T10:30:00.000000",
  "version": "1.0.0"
}
```

#### Аутентификация

**Регистрация:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Вход:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Получение информации о текущем пользователе:**
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Обновление токена:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

**Выход:**
```http
POST /api/v1/auth/logout
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

---

## 👨‍💻 Разработка

### Добавление нового эндпоинта

1. Создайте новый файл в `app/api/v1/endpoints/`:
   ```python
   # app/api/v1/endpoints/example.py
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.get("/example")
   async def example_endpoint():
       return {"message": "Example endpoint"}
   ```

2. Зарегистрируйте роутер в `app/api/v1/router.py`:
   ```python
   from app.api.v1.endpoints import example
   
   api_router.include_router(
       example.router,
       tags=["Example"],
   )
   ```

### Конфигурация

Все настройки находятся в `app/core/config.py`. Вы можете переопределить их через переменные окружения в файле `.env`.

### Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```env
PROJECT_NAME=Backend API
VERSION=1.0.0
API_V1_STR=/api/v1
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

---

## 📝 Лицензия

MIT License

---

## 🤝 Контрибуция

Приветствуются любые предложения по улучшению проекта!

---

<div align="center">
Сделано с ❤️ используя FastAPI
</div>
