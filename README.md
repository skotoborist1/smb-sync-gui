# SMB Sync (smb-sync-gui)

[English](#english) | [Русский](#русский)

---

## English

A modern graphical user interface (GUI) application based on **GTK4** and **Libadwaita** for fast data mirroring between SMB shares using `rsync`.

### Key Features
* 🔄 Unidirectional directory mirroring (deletes redundant files on target).
* 📋 Real-time sync log viewer embedded directly in the header bar.
* 🌐 Built-in instant language switcher (Russian / English).
* 🛡️ Safe and interactive SMB share browser via `smbclient`.
* ⚡ Lightweight architecture using background threads to keep the UI smooth and responsive.

### System Dependencies
Before running the application, make sure your system has the required utilities installed:
* Python 3
* GTK4 & Libadwaita Python bindings (`python3-gi`)
* `rsync` (the core engine for fast mirroring)
* `cifs-utils` (for mounting network drives)
* `smbclient` (for browsing network shares)
* `policykit-1` / `pkexec` (for temporary privileges to handle mounts)

### Installation

To install **SMB Sync** instantly, open your terminal and run the following command:

```bash
curl -sL https://raw.githubusercontent.com/skotoborist1/smb-sync-gui/main/install.sh | bash
```

This script will automatically detect your distribution (Fedora, Ubuntu/Debian, or Arch Linux), install all necessary dependencies (`rsync`, `cifs-utils`, `smbclient`), download the latest app files, and configure the desktop shortcut.

---

## Русский

Современное графическое приложение на базе **GTK4** и **Libadwaita** для быстрого одностороннего зеркалирования данных между сетевыми SMB-шарами с помощью утилиты `rsync`.

### Основные возможности
* 🔄 Зеркалирование каталогов в один клик (с автоматическим удалением лишнего на приемнике).
* 📋 Быстрый просмотр логов синхронизации прямо из верхней панели приложения.
* 🌐 Мгновенное переключение языка интерфейса (Русский / Английский) на лету.
* 🛡️ Интерактивный браузер сетевых ресурсов на удаленном хосте через `smbclient`.
* ⚡ Фоновые потоки выполнения задач: интерфейс никогда не зависает в процессе копирования.

### Системные зависимости
Перед использованием приложения убедитесь, что в вашей системе установлены следующие пакеты:
* Python 3
* Библиотеки привязок GTK4 и Libadwaita (`python3-gi`)
* `rsync` (основной движок синхронизации файлов)
* `cifs-utils` (для монтирования сетевых дисков в систему)
* `smbclient` (для сканирования доступных шар)
* `policykit-1` / `pkexec` (для безопасного выполнения монтирования через sudo-панель)

### Установка

Чтобы мгновенно установить **SMB Sync** в вашу систему, откройте терминал и выполните следующую команду:

```bash
curl -sL https://raw.githubusercontent.com/skotoborist1/smb-sync-gui/main/install.sh | bash
```

Этот скрипт автоматически определит ваш дистрибутив (Fedora, Ubuntu/Debian или Arch Linux), установит все необходимые зависимости (`rsync`, `cifs-utils`, `smbclient`), загрузит свежие файлы приложения и настроит ярлык в системном меню.

4. **Готово!** Иконка «SMB Sync» мгновенно появится в системном меню ваших приложений.

---
## License / Лицензия
This project is licensed under the **GPL-3.0 License**.

