# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Системные пакеты для сборки mysqlclient (+ немного для Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libjpeg62-turbo-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Базовые инструменты Python
RUN pip install --upgrade pip setuptools wheel

# Ставим зависимости проекта (кэш на слое requirements)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

EXPOSE 8000

# Gunicorn: просто и надёжно для контейнера
CMD ["gunicorn","rental_project.wsgi:application","--bind","0.0.0.0:8000","--workers","2"]
