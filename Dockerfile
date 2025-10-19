FROM python:3.12-slim

# Системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt /home/

# Обновляем pip, setuptools и wheel и устанавливаем зависимости
RUN python -m ensurepip && \
    python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /home/requirements.txt

WORKDIR /home
