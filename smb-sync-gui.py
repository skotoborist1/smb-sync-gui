#!/usr/bin/env python3
"""SMB Sync — графическое приложение для зеркалирования SMB-шар."""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import os
import configparser
import subprocess
import threading
import tempfile
import re
import json
from datetime import datetime

# Пути к конфигурации и лог-файлу
# Paths to configuration and log file
CONFIG_DIR = os.path.expanduser('~/.config/smb-sync-gui')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.ini')
LOG_FILE = os.path.expanduser('~/.local/share/applications/smb-sync-gui/smb-sync-gui.log')

# Безопасная загрузка локализации из внешнего JSON-файла
# Safely loading localization from an external JSON file
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locales.json')
try:
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        TRANSLATIONS = json.load(f)
except Exception as e:
    print(f"Предупреждение: Не удалось загрузить locales.json ({e}). Используются базовые строки.")
    # Запасной минимальный словарь на случай отсутствия файла
    # Backup minimal dictionary in case the file is missing
    TRANSLATIONS = {
        'ru': {'settings': 'Настройки', 'about': 'О программе', 'ready': 'Готово к работе'},
        'en': {'settings': 'Settings', 'about': 'About', 'ready': 'Ready'}
    }

# Дефолтные строки для логов bash-скрипта (на случай отсутствия в locales.json)
# Default lines for bash script logs (in case they are missing from locales.json)
_LOG_DEFAULTS = {
    'ru': {
        'log_mount_src': 'Монтирование источника...',
        'log_err_mount_src': 'ОШИБКА: не удалось смонтировать источник',
        'log_mount_dst': 'Монтирование приемника...',
        'log_err_mount_dst': 'ОШИБКА: не удалось смонтировать приемник',
        'log_start_rsync': 'Запуск зеркалирования (удаление лишнего на приемнике включено)...',
        'log_cleanup': 'Очистка: размонтирование сетевых дисков...',
    },
    'en': {
        'log_mount_src': 'Mounting source...',
        'log_err_mount_src': 'ERROR: failed to mount source',
        'log_mount_dst': 'Mounting destination...',
        'log_err_mount_dst': 'ERROR: failed to mount destination',
        'log_start_rsync': 'Starting mirroring (deleting extras on destination enabled)...',
        'log_cleanup': 'Cleanup: unmounting network drives...',
    }
}
for _lang in ('ru', 'en'):
    for _k, _v in _LOG_DEFAULTS[_lang].items():
        TRANSLATIONS.setdefault(_lang, {}).setdefault(_k, _v)

def log_message(message):
    """Красивое логирование одновременно в файл лога и консоль (аналог tee -a)."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"Не удалось записать в лог: {e}")
    print(message)

class SMBSyncWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title('SMB Sync')
        self.set_default_size(520, 360)

        self.config = configparser.ConfigParser()
        self._load_config()
        
        # Считываем сохраненный язык
        # Read the saved language
        self.lang = self.config.get('SMB', 'lang', fallback='ru')

        # Header bar
        header = Adw.HeaderBar()
        self.set_titlebar(header)
        self.lang_btn = Gtk.ToggleButton(label="RUS" if self.lang == 'ru' else "ENG")
        self.lang_btn.set_active(self.lang == 'en')
        self.lang_btn.connect('toggled', self._on_lang_toggled)
        header.pack_start(self.lang_btn)
        self.menu = Gio.Menu()
        self.menu_btn = Gtk.MenuButton()
        self.menu_btn.set_icon_name('open-menu-symbolic')
        self.menu_btn.set_menu_model(self.menu)
        header.pack_end(self.menu_btn)
        self.log_btn = Gtk.Button(label="📋")
        self.log_btn.set_tooltip_text("Открыть логи" if self.lang == 'ru' else "Open logs")
        self.log_btn.connect('clicked', self._on_open_logs_clicked)
        header.pack_end(self.log_btn)

        self.set_child(self._build_main())
        self._update_ui_strings()  # Загружаем переводы в виджеты при старте
                                   # Load translations into widgets at startup

    def _load_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH)
        if 'SMB' not in self.config:
            self.config['SMB'] = {
                'ip': '192.168.1.1',
                'user': '',
                'password': '',
                'src': '',
                'dst': '',
                'lang': 'ru',
            }
            self._save_config()

    def _save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            self.config.write(f)
        os.chmod(CONFIG_PATH, 0o600)

    def _t(self, key):
        """Хелпер для безопасного получения строки на выбранном языке."""
        return TRANSLATIONS.get(self.lang, {}).get(key, f"[{key}]")


    def _on_lang_toggled(self, btn):
        """Обработчик нажатия на переключатель RUS/ENG."""
        if btn.get_active():
            self.lang = 'en'
            btn.set_label("ENG")
        else:
            self.lang = 'ru'
            btn.set_label("RUS")
        
        self.config.set('SMB', 'lang', self.lang)
        self._save_config()
        self._update_ui_strings()

    def _on_open_logs_clicked(self, _btn):
        """Обработчик нажатия на кнопку логов. Открывает файл в дефолтном редакторе."""
        if not os.path.exists(LOG_FILE):
            log_message("--- Создан новый файл логов ---" if self.lang == 'ru' else "--- New log file created ---")
        
        try:
            subprocess.Popen(['xdg-open', LOG_FILE])
        except Exception as e:
            self.status_label.set_text(f"Не удалось открыть лог: {e}" if self.lang == 'ru' else f"Failed to open log: {e}")

    def _update_ui_strings(self):
        """Метод перевода всех строк интерфейса на лету без изменения разметки."""
        self.menu.remove_all()
        self.menu.append(self._t('settings'), 'app.settings')
        self.menu.append(self._t('about'), 'app.about')

        self.src_frame.set_label(self._t('src_label'))
        self.src_entry.set_placeholder_text(self._t('src_ph'))
        self.src_browse_btn.set_label(self._t('browse'))

        self.dst_frame.set_label(self._t('dst_label'))
        self.dst_entry.set_placeholder_text(self._t('dst_ph'))
        self.dst_browse_btn.set_label(self._t('browse'))

        self.log_btn.set_tooltip_text("Открыть логи" if self.lang == 'ru' else "Open logs")

        if self.sync_btn.get_sensitive():
            self.sync_btn.set_label(self._t('sync_btn'))
        if self.progress.get_fraction() == 0:
            self.progress.set_text(self._t('ready'))

    def _build_main(self):
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        for m in ('margin_start', 'margin_end', 'margin_top', 'margin_bottom'):
            getattr(main, f'set_{m}')(16)

        # Источник
        # Source
        self.src_frame = Gtk.Frame()
        src_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for m in ('margin_start', 'margin_end', 'margin_top', 'margin_bottom'):
            getattr(src_box, f'set_{m}')(8)
        self.src_frame.set_child(src_box)
        main.append(self.src_frame)

        self.src_entry = Gtk.Entry()
        self.src_entry.set_text(self.config.get('SMB', 'src', fallback=''))
        self.src_entry.set_hexpand(True)
        src_box.append(self.src_entry)

        self.src_browse_btn = Gtk.Button()
        self.src_browse_btn.connect('clicked', self._on_browse, 'src')
        src_box.append(self.src_browse_btn)

        # Назначение
        # Target
        self.dst_frame = Gtk.Frame()
        dst_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for m in ('margin_start', 'margin_end', 'margin_top', 'margin_bottom'):
            getattr(dst_box, f'set_{m}')(8)
        self.dst_frame.set_child(dst_box)
        main.append(self.dst_frame)

        self.dst_entry = Gtk.Entry()
        self.dst_entry.set_text(self.config.get('SMB', 'dst', fallback=''))
        self.dst_entry.set_hexpand(True)
        dst_box.append(self.dst_entry)

        self.dst_browse_btn = Gtk.Button()
        self.dst_browse_btn.connect('clicked', self._on_browse, 'dst')
        dst_box.append(self.dst_browse_btn)

        # Кнопка запуска
        # Start button
        self.sync_btn = Gtk.Button()
        self.sync_btn.add_css_class('suggested-action')
        self.sync_btn.connect('clicked', self._on_sync)
        main.append(self.sync_btn)

        # Прогресс-бар
        # Progress bar
        self.progress = Gtk.ProgressBar()
        self.progress.set_show_text(True)
        main.append(self.progress)

        # Статус
        # Status
        self.status_label = Gtk.Label(label='')
        self.status_label.set_wrap(True)
        self.status_label.set_xalign(0)
        main.append(self.status_label)

        return main
    def _on_browse(self, _btn, target):
        ip = self.config.get('SMB', 'ip', fallback='192.168.1.1')
        user = self.config.get('SMB', 'user', fallback='')
        password = self.config.get('SMB', 'password', fallback='')

        shares = self._list_shares(ip, user, password)
        if not shares:
            self.status_label.set_text(self._t('err_list_shares'))
            return

        dialog = Gtk.Dialog(title=self._t('dlg_title_shares'), transient_for=self, modal=True)
        dialog.set_default_size(320, 400)
        content = dialog.get_content_area()

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        for share in shares:
            lbl = Gtk.Label(label=share, xalign=0)
            lbl.set_margin_start(12)
            lbl.set_margin_end(12)
            lbl.set_margin_top(8)
            lbl.set_margin_bottom(8)
            listbox.append(lbl)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(listbox)
        scroll.set_vexpand(True)
        content.append(scroll)

        cancel_btn = Gtk.Button(label=self._t('cancel'))
        ok_btn = Gtk.Button(label=self._t('select'))
        dialog.add_action_widget(cancel_btn, Gtk.ResponseType.CANCEL)
        dialog.add_action_widget(ok_btn, Gtk.ResponseType.OK)

        def on_response(_dlg, response):
            if response == Gtk.ResponseType.OK:
                row = listbox.get_selected_row()
                if row:
                    name = row.get_child().get_text()
                    if target == 'src':
                        self.src_entry.set_text(name)
                    else:
                        self.dst_entry.set_text(name)
            dialog.close()

        listbox.connect('row-activated', lambda _lb, _row: dialog.response(Gtk.ResponseType.OK))
        dialog.connect('response', on_response)
        dialog.present()

    @staticmethod
    def _list_shares(ip, user, password):
        try:
            cmd = ['smbclient', '-L', f'//{ip}', '-U', f'{user}%{password}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            shares = []
            for line in result.stdout.splitlines():
                if 'Disk' in line:
                    parts = line.split()
                    if parts and not parts[0].endswith('$'):
                        shares.append(parts[0])
            return shares if shares else None
        except Exception:
            return None
    def _on_sync(self, _btn):
        ip = self.config.get('SMB', 'ip', fallback='192.168.1.1')
        user = self.config.get('SMB', 'user', fallback='')
        password = self.config.get('SMB', 'password', fallback='')
        src = self.src_entry.get_text().strip()
        dst = self.dst_entry.get_text().strip()

        if not src or not dst:
            self.status_label.set_text(self._t('err_fill_fields'))
            return
        if not user:
            self.status_label.set_text(self._t('err_no_login'))
            return

        self.config.set('SMB', 'src', src)
        self.config.set('SMB', 'dst', dst)
        self._save_config()
        self.sync_btn.set_sensitive(False)
        self.progress.set_fraction(0)
        self.progress.set_text(self._t('preparing'))
        self.status_label.set_text('')

        threading.Thread(target=self._run_sync, args=(ip, user, password, src, dst), daemon=True).start()

    def _run_sync(self, ip, user, password, src, dst):
        mnt_src = '/mnt/smb-sync-src'
        mnt_dst = '/mnt/smb-sync-dst'
        src_share = f'//{ip}/{src}'
        dst_share = f'//{ip}/{dst}'

        start_banner = f"=== {self._t('log_start')}: {datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')} ==="
        log_message(start_banner)

        script = (
            "#!/bin/bash\n"
            f"mkdir -p '{mnt_src}' '{mnt_dst}'\n"
            f"echo '{self._t('log_mount_src')}' && mount -t cifs '{src_share}' '{mnt_src}' -o username='{user}',password='{password}',iocharset=utf8 "
            f"|| {{ echo '{self._t('log_err_mount_src')}'; exit 1; }}\n"
            f"echo '{self._t('log_mount_dst')}' && mount -t cifs '{dst_share}' '{mnt_dst}' -o username='{user}',password='{password}',iocharset=utf8 "
            f"|| {{ echo '{self._t('log_err_mount_dst')}'; exit 1; }}\n"
            f"echo '{self._t('log_start_rsync')}' && "
            f"rsync -rtv --info=progress2 --delete --modify-window=1 --inplace --preallocate --bwlimit=45m '{mnt_src}/' '{mnt_dst}/'\n"
            f"RET=${{PIPESTATUS}}\n"
            f"echo '{self._t('log_cleanup')}' \n"
            f"umount -l '{mnt_src}' 2>/dev/null\n"
            f"umount -l '{mnt_dst}' 2>/dev/null\n"
            f"rmdir '{mnt_src}' '{mnt_dst}' 2>/dev/null\n"
            f"exit $RET\n"
        )

        fd, script_path = tempfile.mkstemp(suffix='.sh')
        with os.fdopen(fd, 'w') as f:
            f.write(script)
        os.chmod(script_path, 0o700)

        try:
            proc = subprocess.Popen(['pkexec', 'bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            buf = b''
            progress_pattern = re.compile(r'(\d+)\s+(\d+)%\s+[\d.,]+[kKMG]?B/s\s+\d+:\d+:\d+')

            while True:
                try:
                    chunk = proc.stdout.read1(1024)
                except Exception:
                    break
                if not chunk:
                    break
                buf += chunk
                parts = re.split(rb'[\r\n]', buf)
                buf = parts[-1]
                for part in parts[:-1]:
                    line = part.decode('utf-8', errors='replace').strip()
                    if not line:
                        continue
                    
                    is_progress_line = bool(progress_pattern.search(line))
                    if not is_progress_line:
                        log_message(line)
                    else:
                        print(f"[UI Progress Context]: {line}")

                    m = re.search(r'(\d+)%', line)
                    if m:
                        pct = int(m.group(1))
                        GLib.idle_add(self._update_progress, pct)
                    else:
                        if not is_progress_line:
                            GLib.idle_add(self._update_status, line)

            proc.wait()
            rc = proc.returncode

            if rc == 0:
                GLib.idle_add(self._update_progress, 100)
                GLib.idle_add(self._update_status, self._t('success'))
                log_message(self._t('log_success'))
            elif rc in (126, 127):
                GLib.idle_add(self._update_status, self._t('err_pkexec'))
                log_message(self._t('log_err_pkexec'))
            else:
                GLib.idle_add(self._update_status, self._t('err_sync_code').format(rc))
                log_message(self._t('log_err_sync'))
        except FileNotFoundError:
            GLib.idle_add(self._update_status, self._t('err_no_pkexec'))
            log_message(self._t('log_err_no_pkexec'))
        except Exception as e:
            GLib.idle_add(self._update_status, self._t('exception').format(e))
            log_message(f"{self._t('log_exception')}: {e}")
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass
            end_banner = f"=== {self._t('log_end')}: {datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')} ==="
            log_message(end_banner)
            log_message("----------------------------------------------------------------------------")
            GLib.idle_add(self._reset_sync_ui)

    def _reset_sync_ui(self):
        self.sync_btn.set_sensitive(True)
        self.sync_btn.set_label(self._t('sync_btn'))

    def _update_progress(self, pct):
        self.progress.set_fraction(pct / 100.0)
        self.progress.set_text(f'{pct}%')

    def _update_status(self, text):
        self.status_label.set_text(text[:120])
    def show_settings(self):
        dialog = Gtk.Dialog(title=self._t('settings'), transient_for=self, modal=True)
        dialog.set_default_size(380, 220)
        content = dialog.get_content_area()
        content.set_spacing(10)
        for m in ('margin_start', 'margin_end', 'margin_top', 'margin_bottom'):
            getattr(content, f'set_{m}')(16)

        ip_entry = self._add_setting_row(content, self._t('ip_label'), self.config.get('SMB', 'ip', fallback='192.168.1.1'), False)
        user_entry = self._add_setting_row(content, self._t('login_label'), self.config.get('SMB', 'user', fallback=''), False)
        pass_entry = self._add_setting_row(content, self._t('pass_label'), self.config.get('SMB', 'password', fallback=''), True)

        cancel_settings_btn = Gtk.Button(label=self._t('cancel'))
        save_settings_btn = Gtk.Button(label=self._t('save'))
        dialog.add_action_widget(cancel_settings_btn, Gtk.ResponseType.CANCEL)
        dialog.add_action_widget(save_settings_btn, Gtk.ResponseType.OK)

        def on_response(_dlg, response):
            if response == Gtk.ResponseType.OK:
                self.config.set('SMB', 'ip', ip_entry.get_text().strip())
                self.config.set('SMB', 'user', user_entry.get_text().strip())
                self.config.set('SMB', 'password', pass_entry.get_text())
                self._save_config()
                self.status_label.set_text(self._t('settings_saved'))
            dialog.close()

        dialog.connect('response', on_response)
        dialog.present()

    @staticmethod
    def _add_setting_row(parent, label_text, value, is_password):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl = Gtk.Label(label=label_text)
        lbl.set_xalign(0)
        lbl.set_size_request(100, -1)
        entry = Gtk.Entry()
        entry.set_text(value)
        entry.set_hexpand(True)
        if is_password:
            entry.set_visibility(False)
        box.append(lbl)
        box.append(entry)
        parent.append(box)
        return entry

    def show_about(self):
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_modal(True)
        about.set_program_name('SMB Sync')
        about.set_version('2.3')
        about.set_comments(self._t('about_comments'))
        about.set_license_type(Gtk.License.GPL_3_0)
        about.present()


class SMBSyncApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='org.example.smbsync')
        self.connect('activate', self._on_activate)

        a = Gio.SimpleAction.new('settings', None)
        a.connect('activate', lambda _a, _p: self.win.show_settings())
        self.add_action(a)

        a = Gio.SimpleAction.new('about', None)
        a.connect('activate', lambda _a, _p: self.win.show_about())
        self.add_action(a)

    def _on_activate(self, app):
        self.win = SMBSyncWindow(application=app)
        self.win.present()


if __name__ == '__main__':
    import sys
    SMBSyncApp().run(sys.argv)

