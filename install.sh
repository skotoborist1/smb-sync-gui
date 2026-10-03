#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # Без цвета

# Ссылка на твой репозиторий GitHub (используем специальный URL для скачивания чистых файлов)
REPO_RAW_URL="https://raw.githubusercontent.com/skotoborist1/smb-sync-gui/main"

echo -e "${BLUE}=== Сетевая установка SMB Sync (smb-sync-gui) ===${NC}"

# Шаг 1: Автоопределение дистрибутива и установка системных зависимостей
echo -e "\n${BLUE}[1/3] Проверка и установка системных зависимостей...${NC}"

if [ -f /etc/fedora-release ]; then
    echo -e "Обнаружена система: ${GREEN}Fedora${NC}"
    sudo dnf install -y python3-gobject gtk4 libadwaita rsync cifs-utils smbclient curl
elif [ -f /etc/debian_version ] || [ -f /etc/lsb-release ]; then
    echo -e "Обнаружена система: ${GREEN}Ubuntu / Debian${NC}"
    sudo apt update && sudo apt install -y python3-gi gist-adwaita-icon-theme rsync cifs-utils smbclient policykit-1 curl
elif [ -f /etc/arch-release ]; then
    echo -e "Обнаружена система: ${GREEN}Arch Linux${NC}"
    sudo pacman -Sy --needed --noconfirm python-gobject gtk4 libadwaita rsync cifs-utils smbclient curl
else
    echo -e "${RED}Предупреждение: Не удалось точно определить дистрибутив.${NC}"
    echo "Пожалуйста, убедитесь, что у вас установлены: python3, rsync, cifs-utils, smbclient, GTK4, Libadwaita и curl."
fi

# Шаг 2: Создание папки приложения и скачивание файлов из репозитория
echo -e "\n${BLUE}[2/3] Загрузка файлов приложения из GitHub...${NC}"

TARGET_DIR="$HOME/.local/share/applications/smb-sync-gui"
APP_DIR="$HOME/.local/share/applications"

# Создаем целевую директорию
mkdir -p "$TARGET_DIR"

# Скачиваем каждый файл напрямую с GitHub в нужную папку
echo "Загрузка smb-sync-gui.py..."
curl -sL "$REPO_RAW_URL/smb-sync-gui.py" -o "$TARGET_DIR/smb-sync-gui.py"

echo "Загрузка locales.json..."
curl -sL "$REPO_RAW_URL/locales.json" -o "$TARGET_DIR/locales.json"

echo "Загрузка smb-sync-gui.png..."
curl -sL "$REPO_RAW_URL/smb-sync-gui.png" -o "$TARGET_DIR/smb-sync-gui.png"

echo "Загрузка smb-sync-gui.desktop..."
curl -sL "$REPO_RAW_URL/smb-sync-gui.desktop" -o "$TARGET_DIR/smb-sync-gui.desktop"

# Проверяем, что файлы скачались успешно (не пустые)
if [ -s "$TARGET_DIR/smb-sync-gui.py" ] && [ -s "$TARGET_DIR/locales.json" ]; then
    # Выдаем права на исполнение
    chmod +x "$TARGET_DIR/smb-sync-gui.py"
    chmod +x "$TARGET_DIR/smb-sync-gui.desktop"
    echo -e "${GREEN}Все файлы успешно загружены в: $TARGET_DIR${NC}"
else
    echo -e "${RED}ОШИБКА: Не удалось скачать файлы приложения с GitHub!${NC}"
    echo "Проверьте подключение к интернету или правильность ссылки на репозиторий."
    exit 1
fi

# Шаг 3: Обновление кэша меню приложений
echo -e "\n${BLUE}[3/3] Обновление системного меню...${NC}"

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APP_DIR"
fi

echo -e "\n${GREEN}=== Установка успешно завершена! ===${NC}"
echo -e "Программа готова к работе. Для удаления просто удалите папку приложения:"
echo -e "${BLUE}rm -rf $TARGET_DIR${NC}"

