import yadisk
import os
import sys

YADISK_TOKEN = os.getenv("YADISK_TOKEN")

if not YADISK_TOKEN:
    print("Ошибка: не задана переменная окружения YADISK_TOKEN")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Ошибка: не указан файл для загрузки. Пример: python upload_to_yadisk.py /path/to/backup.sql.gz")
    sys.exit(1)

local_filepath = sys.argv[1]
filename = os.path.basename(local_filepath)

remote_filepath = f"/{filename}"

try:
    y = yadisk.YaDisk(token=YADISK_TOKEN)
    print(f"Загрузка файла '{local_filepath}' в Яндекс.Диск как '{remote_filepath}'...")
    y.upload(local_filepath, remote_filepath, overwrite=True)
    print("Загрузка успешно завершена.")

except Exception as e:
    print(f"Произошла ошибка при загрузке: {e}")
    sys.exit(1)
