FROM python:3.10.5

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    UWSGI_PROCESSES 1 \
    UWSGI_THREADS 16 \
    UWSGI_HARAKIRI 240

COPY requirements.txt .

RUN apt-get update \
    && apt install -y curl netcat \
    && pip install -r requirements.txt

COPY . .

EXPOSE $FASTAPI_PORT

WORKDIR /app/src/
