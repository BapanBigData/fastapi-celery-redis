# Advanced FastAPI Backend

A robust, production-ready FastAPI backend following best practices, featuring:

- **Async SQLModel/SQLAlchemy** for database access
- **Alembic** for migrations
- **PostgreSQL** (production) and **MySQL** (development) support
- **Celery** for background tasks
- **Redis** for task queue and caching
- **JWT-based authentication**
- **Pydantic** for settings and validation
- **Modular app structure** for scalability and maintainability

---

## Features

- **Async Endpoints**: Fully async API for maximum performance.
- **Background Tasks**: Heavy or slow tasks are offloaded to Celery workers.
- **Task Queue & Caching**: Redis is used both as a Celery broker and for caching.
- **Secure Auth**: JWT authentication, password hashing, and role-based access.
- **Environment-based Config**: Uses `.env` and Pydantic for robust configuration.
- **Database Migrations**: Alembic for safe, versioned schema changes.
- **Testing**: Pytest for automated testing.
- **Email Support**: FastAPI-Mail for sending emails.
- **Production Ready**: Uvicorn for ASGI serving, and best practices for deployment.

---

## Project Structure

```
src/app/
    auth/         # Authentication logic (routes, schemas, services)
    books/        # Book-related endpoints and logic
    reviews/      # Review endpoints and logic
    db/           # Database and Redis connection setup
    models/       # SQLModel/SQLAlchemy models
    utils/        # Utilities: Celery tasks, config, mail, security, etc.
    main.py       # FastAPI app entrypoint
migrations/       # Alembic migrations
```

---

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/BapanBigData/fastapi-celery-redis.git
cd fastapi-celery-redis
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values for your environment (DB URLs, secrets, etc).

### 3. Database Migrations

```bash
alembic upgrade head
```

### 4. Start Services

- **Redis**:  
  Start a Redis server (locally or via Docker).

- **Celery Worker**:

  ```bash
  celery -A src.app.utils.celery_tasks.celery worker --loglevel=info
  ```

- **FastAPI App**:
  ```bash
  uvicorn src.app.main:app --reload
  ```

---

## Best Practices Emphasized

- **Async everywhere**: All I/O is async for scalability.
- **Separation of concerns**: Clear separation between routes, services, schemas, and models.
- **Background processing**: Use Celery for long-running/background tasks (e.g., sending emails, heavy computations).
- **Caching**: Use Redis for caching expensive queries or results.
- **Environment configs**: All secrets and configs are managed via environment variables and Pydantic settings.
- **Database migrations**: Never change schema manually; always use Alembic.
- **Testing**: Write tests for all endpoints and business logic.
- **Security**: Use JWT for authentication, hash passwords, validate all inputs.
- **Production readiness**: Use Uvicorn with workers, proper logging, and environment separation.

---

## Advanced Features

- **Celery + Redis**:  
  Offload background tasks (e.g., email sending, report generation) to Celery workers, using Redis as the broker.

- **Redis Caching**:  
  Cache frequently accessed data to reduce DB load and improve response times.

- **Async Database**:  
  Use SQLModel/SQLAlchemy with async drivers (`asyncpg` for PostgreSQL, `asyncmy` for MySQL).

- **Modular Design**:  
  Each domain (auth, books, reviews) is a separate module for maintainability.

---

## Testing

```bash
pytest
```

---

## Deployment

- Use environment variables for all secrets and configs.
- Run Uvicorn with multiple workers for production.
- Use a managed PostgreSQL and Redis service for reliability.

---

## Contributing

Pull requests are welcome! Please open issues for bugs or feature requests.

---

## License

MIT
