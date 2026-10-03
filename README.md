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
The program is distributed as a portable archive. Simply unpack it into your local applications folder:

1. Download the `smb-sync-gui.tar.xz` archive.
2. Open a terminal and run this single command to unpack and install the shortcut:
```bash
tar -xvf smb-sync-gui.tar.xz -C ~/.local/share/applications/ && mv ~/.local/share/applications/smb-sync-gui/smb-sync-gui.desktop ~/.local/share/applications/
```
3. Make sure the script is executable:
```bash
chmod +x ~/.local/share/applications/smb-sync-gui/smb-sync-gui.py
```
4. **Done!** The "SMB Sync" launcher icon will instantly appear in your system desktop menu.

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

### Установка приложения
Программа поставляется в виде удобного готового архива. Процесс установки сводится к его распаковке:

1. Скачайте архив проекта `smb-sync-gui.tar.xz`.
2. Откройте ваш терминал и выполните одну команду для распаковки и переноса ярлыка:
```bash
tar -xvf smb-sync-gui.tar.xz -C ~/.local/share/applications/ && mv ~/.local/share/applications/smb-sync-gui/smb-sync-gui.desktop ~/.local/share/applications/
```
3. Выдайте файлу скрипта права на запуск:
```bash
chmod +x ~/.local/share/applications/smb-sync-gui/smb-sync-gui.py
```
4. **Готово!** Иконка «SMB Sync» мгновенно появится в системном меню ваших приложений.

---
## License / Лицензия
This project is licensed under the **GPL-3.0 License**.

