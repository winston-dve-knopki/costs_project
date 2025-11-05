FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    postgresql-client \
    gzip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install yadisk[requests]

WORKDIR /app/backup

COPY ./upload_to_yadisk.py .
COPY ./backup_db.sh .
COPY ./crontab .

RUN chmod +x backup_db.sh

RUN crontab crontab

CMD touch /var/log/cron.log && cron && tail -f /var/log/cron.log
