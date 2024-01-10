FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONWARNINGS once

RUN python -m pip install --upgrade pip poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-root

WORKDIR /app
COPY . .
ENV PYTHONPATH .