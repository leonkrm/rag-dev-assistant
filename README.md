# 🤖 RAG Dev Assistant

Умный помощник для разработчиков на основе Retrieval-Augmented Generation (RAG).
Бот «знает» кодовую базу и документацию проекта и отвечает на вопросы с указанием источников.

## Возможности

- 🔍 Векторный поиск по индексированным источникам (PostgreSQL + pgvector)
- 💬 Чат с LLM, который отвечает на основе найденного контекста и указывает источники
- 📥 Индексация локальных папок с кодом и документацией
- 🐳 Полностью контейнеризовано (Docker Compose) для локального запуска
- ✅ CI/CD через GitHub Actions (линтер, тесты, сборка при каждом push)

## Стек технологий

| Слой         | Технология                                             |
|--------------|----------------------------------------------------------|
| Бэкенд       | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic     |
| Фронтенд     | Angular 18 (standalone components)                        |
| БД           | PostgreSQL 16 + pgvector                                   |
| Эмбеддинги   | sentence-transformers (`all-MiniLM-L6-v2`)                 |
| LLM          | Anthropic Claude API (переключаемо на OpenAI-совместимые/локальные через Ollama) |
| Инфра        | Docker, Docker Compose, GitHub Actions                     |

## Архитектура

Вопрос пользователя → эмбеддинг (sentence-transformers) → векторный поиск в pgvector →
сборка контекста из найденных чанков → вызов LLM → ответ с указанием источников.

## Быстрый старт

### 1. Переменные окружения

```bash
cp backend/.env.example backend/.env
# впишите LLM_API_KEY в backend/.env
```

### 2. Запуск через Docker Compose

```bash
docker compose up --build
```

Поднимает:
- `db` — PostgreSQL + pgvector, порт `5432`
- `backend` — FastAPI, порт `8000` (Swagger UI: http://localhost:8000/docs)
- `frontend` — Angular, порт `4200`

### 3. Применить миграции

```bash
docker exec -it rag-dev-assistant-backend-1 alembic upgrade head
```

### 4. Проиндексировать источник

```bash
curl -X POST http://localhost:8000/api/sources \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project", "type": "local_folder", "uri": "/app/my-project"}'

curl -X POST http://localhost:8000/api/sources/<SOURCE_ID>/sync
```

### 5. Открыть чат

http://localhost:4200

## Статус проекта

Backend, frontend, база данных, контейнеризация и CI/CD полностью реализованы и протестированы
end-to-end. Вызов LLM работает через Anthropic API (требует оплаченного доступа) или может быть
переключён на локальную модель через Ollama, поменяв `LLM_PROVIDER` в `.env`.

## Roadmap

- [ ] Индексация git-репозиториев (сейчас — только локальные папки)
- [ ] Аутентификация и роли доступа
- [ ] Гибридный поиск (BM25 + векторный)
- [ ] Деплой в облако

## Лицензия

MIT
