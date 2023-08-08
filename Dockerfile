FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Для poetry
# COPY poetry.lock pyproject.toml /app/
# RUN pip install --upgrade pip --no-cache-dir && \
#    pip install --no-cache-dir poetry && \
#    poetry install --no-interaction --no-ansi

# Для requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir && pip install --no-cache-dir -r requirements.txt

COPY . .
