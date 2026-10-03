#!/bin/bash
# Универсальный деинсталлятор для SMB Sync

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # Без цвета

echo -e "${BLUE}=== Удаление SMB Sync (smb-sync-gui) ===${NC}"

TARGET_DIR="$HOME/.local/share/applications/smb-sync-gui"
APP_DIR="$HOME/.local/share/applications"

# 1. Проверяем наличие папки приложения
if [ -d "$TARGET_DIR" ]; then
    echo "Удаление файлов приложения и ярлыка из $TARGET_DIR..."
    rm -rf "$TARGET_DIR"
    
    # 2. Обновляем кэш меню приложений, чтобы иконка мгновенно пропала из системы
    echo "Обновление системного меню..."
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$APP_DIR"
    fi
    
    # 3. Пиннаем оболочку GNOME для полной очистки кэша графики
    killall -HUP gnome-shell &>/dev/null
    
    echo -e "${GREEN}=== SMB Sync успешно и полностью удалён! ===${NC}"
else
    echo -e "${RED}Ошибка: Папка приложения не найдена в $TARGET_DIR.${NC}"
    echo "Возможно, программа уже была удалена ранее."
fi

