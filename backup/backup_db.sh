#!/bin/bash

DB_HOST=${POSTGRES_HOST}
DB_USER=${POSTGRES_USER}
DB_NAME=${POSTGRES_DB}
export PGPASSWORD=${POSTGRES_PASSWORD}

BACKUP_DIR="/backups"

echo "--- $(date) ---"
echo "Запущен процесс создания бэкапа..."

mkdir -p $BACKUP_DIR

DATE=$(date +"%Y-%m-%d_%H-%M")
BACKUP_FILENAME="backup_${DATE}.sql.gz"
BACKUP_FILEPATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

echo "1. Создание дампа базы данных '$DB_NAME' с хоста '$DB_HOST'..."
# Используем переменные окружения для подключения
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILEPATH

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Ошибка: не удалось создать дамп базы данных."
    exit 1
fi

echo "2. Загрузка бэкапа на Яндекс.Диск..."
# Запускаем Python-скрипт (он тоже будет использовать переменную YADISK_TOKEN)
python /app/backup/upload_to_yadisk.py $BACKUP_FILEPATH

if [ $? -ne 0 ]; then
    echo "Ошибка: не удалось загрузить бэкап."
    # Можно добавить логику отправки уведомления ботом отсюда
    exit 1
fi

echo "3. Очистка локального файла бэкапа..."
rm $BACKUP_FILEPATH

echo "Бэкап успешно создан и загружен!"
echo "--------------------------"
