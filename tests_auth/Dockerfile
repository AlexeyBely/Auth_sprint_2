FROM python:3.10

RUN apt-get update

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 \
    UWSGI_PROCESSES 1 \
    UWSGI_THREADS 16 \
    UWSGI_HARAKIRI 240

WORKDIR /tests

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
