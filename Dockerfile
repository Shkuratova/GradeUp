FROM python:3.14-slim

RUN pip install poetry==2.3.2

WORKDIR /backend

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction  --no-root

COPY app .