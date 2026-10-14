SOURCE_DIR="/home/ubuntu/network-audit/reports"
BACKUP_DIR="/home/ubuntu/network-audit/backups"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "[INFO] Папка для бэкапов не найдена. Создаю: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

SEARCH_FOR_FILES=$(find "$SOURCE_DIR" -type f -mtime -1)

if [ -z "$SEARCH_FOR_FILES" ]; then
    echo "[WARNING] Свежих отчетов за последние 24 часа не обнаружено."
    exit 0
fi

CURRENT_DATE=$(date +%F_%H-%M-%S)
ARCHIVE_NAME="$BACKUP_DIR/ports_backup_$CURRENT_DATE.tar.gz"

tar -czf "$ARCHIVE_NAME" $SEARCH_FOR_FILES

if [ $? -eq 0 ]; then
    echo "[OK] Свежие отчеты успешно упакованы в архив: $ARCHIVE_NAME"
    exit 0
else
    echo "[ERROR] Что-то пошло не так при работе утилиты tar!"
    exit 1
fi