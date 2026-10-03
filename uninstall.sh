#!/bin/bash
# Universal Uninstaller for SMB Sync (smb-sync-gui)

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [[ "$LANG" == ru* ]]; then
    IS_RU=true
else
    IS_RU=false
fi

if [ "$IS_RU" = true ]; then
    MSG_START="${BLUE}=== Удаление SMB Sync (smb-sync-gui) ===${NC}"
    MSG_REMOVING="Удаление файлов приложения из"
    MSG_UPDATING="Обновление системного меню..."
    MSG_SUCCESS="${GREEN}=== SMB Sync успешно и полностью удалён! ===${NC}"
    MSG_ERR="${RED}Ошибка: Папка приложения не найдена в${NC}"
    MSG_ERR_HINT="Возможно, программа уже была удалена ранее."
else
    MSG_START="${BLUE}=== Removing SMB Sync (smb-sync-gui) ===${NC}"
    MSG_REMOVING="Removing files from"
    MSG_UPDATING="Updating system applications menu..."
    MSG_SUCCESS="${GREEN}=== SMB Sync has been completely removed! ===${NC}"
    MSG_ERR="${RED}Error: Application folder not found in${NC}"
    MSG_ERR_HINT="It looks like the application was already removed."
fi

echo -e "$MSG_START"

TARGET_DIR="$HOME/.local/share/applications/smb-sync-gui"
APP_DIR="$HOME/.local/share/applications"

if [ -d "$TARGET_DIR" ]; then
    echo "$MSG_REMOVING $TARGET_DIR..."
    rm -rf "$TARGET_DIR"
    
    echo "$MSG_UPDATING"
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$APP_DIR"
    fi
    
    echo -e "$MSG_SUCCESS"
else
    echo -e "$MSG_ERR $TARGET_DIR."
    echo "$MSG_ERR_HINT"
fi


