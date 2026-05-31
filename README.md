# GradeUp 


### 1. Сборка и запуск контейнеров

```bash
# Собрать образы
docker-compose build

# Запустить контейнеры в фоновом режиме
docker-compose up -d
```

### 2. Применение миграций базы данных

```bash
# Зайти в контейнер backend
docker exec -it gradeup_backend bash

# Применить все миграции Alembic
alembic upgrade head

# Создать суперпользователя
cd actions/
python create_superuser.py

# Выйти из контейнера
exit
```

### 3. Проверка работоспособности

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050



### 4. Работа с миграциями Alembic

```bash
# Войти в контейнер backend
docker exec -it gradeup_backend bash

# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Просмотреть текущую версию
alembic current
```


## Переменные окружения

```bash
# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=db_gradeup
DB_PORT=5432

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
PGADMIN_PORT=5050

# backend
BACKEND_PORT=8000

# App
DB__URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"
DB__ECHO=False
JWT__ALGORITHM=HS256
JWT__SECRET_KEY=secret
JWT__EXPIRE_ACCESS_TOKEN_MINUTES=240
JWT__EXPIRE_REFRESH_TOKEN_DAYS=30
ROOT_PATH=/api/v1
```
