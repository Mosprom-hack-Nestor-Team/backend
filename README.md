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

5. **Создайте файл `.env` (опционально):**
   ```bash
   cp .env.example .env
   ```
   
   Отредактируйте `.env` под ваши нужды.

---

## 🚀 Запуск проекта

### Простой запуск (рекомендуется)

```bash
python3 run.py
```

### Альтернативный запуск через uvicorn

Режим разработки:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 7878
```

Режим продакшн:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 7878 --workers 4
```

После запуска сервер будет доступен по адресу: **http://localhost:7878**

---

## 📚 API Документация

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
