import sys
import os
import json
import time
import threading
import queue
import ctypes
import webbrowser
import subprocess

import psutil
from PIL import Image, ImageDraw, ImageFont, ImageTk
import pystray
from pystray import MenuItem as item

import tkinter as tk
from tkinter import colorchooser, simpledialog, filedialog, messagebox


APP_NAME = "OS-RSM"
APP_VERSION = "2.2"

# =========================================================================
# ОПРЕДЕЛЕНИЕ ПУТЕЙ (учитываем .exe от PyInstaller)
# =========================================================================
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
    EXE_PATH = sys.executable
else:
    _here = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(_here) == "src":
        BASE_DIR = os.path.dirname(_here)
    else:
        BASE_DIR = _here
    EXE_DIR = BASE_DIR
    EXE_PATH = os.path.abspath(__file__)

FONTS_DIR = os.path.join(BASE_DIR, "fonts")
CONFIG_PATH = os.path.expanduser("~/.config/tray-monitor.json")


# =========================================================================
# ЛОКАЛИЗАЦИЯ
# =========================================================================
STRINGS = {
    "ru": {
        "tray_open":  "Открыть",
        "tray_quit":  "Выход",
        "menu_visible_disks":   "Видимые диски",
        "menu_edit_custom":     "Редактировать CUSTOM…",
        "menu_temp_units":      "Единицы температуры",
        "menu_temp_c":          "Цельсий (°C)",
        "menu_temp_f":          "Фаренгейт (°F)",
        "menu_theme":           "Тема",
        "menu_theme_auto":      "Авто (по системе)",
        "menu_theme_light":     "Светлая",
        "menu_theme_dark":      "Тёмная",
        "menu_tray_mode":       "Режим трея",
        "menu_tray_single":     "Одна метрика (текущая)",
        "menu_tray_dual":       "Две метрики",
        "menu_tray_top":        "Верхняя метрика",
        "menu_tray_bottom":     "Нижняя метрика",
        "menu_inc_font":        "Увеличить шрифт",
        "menu_dec_font":        "Уменьшить шрифт",
        "menu_reset_font":      "Сбросить шрифт (100%)",
        "menu_blink":           "Мигание при критической нагрузке",
        "menu_autostart":       "Автозапуск при старте системы",
        "menu_reset_colors":    "Сбросить цвета к Flat UI",
        "menu_reset_all":       "Сбросить всё…",
        "menu_export":          "Экспорт конфига…",
        "menu_import":          "Импорт конфига…",
        "menu_about":           "О программе",
        "menu_language":        "Язык",
        "menu_lang_ru":         "Русский",
        "menu_lang_en":         "English",
        "menu_system_suffix":   "  (системный)",
        "help_title":           "?  Управление",
        "help_line_1":          "Левый клик по плитке — сделать метрику активной (в трее)",
        "help_line_2":          "Левый клик по подписи диска — детали диска",
        "help_line_3":          "2× клик по CUSTOM — задать свой текст",
        "help_line_4":          "2× клик по TEMP — переключить °C / °F",
        "help_line_5":          "ПКМ по цифре — выбрать цвет плитки",
        "help_line_6":          "ПКМ по подписи диска — детали диска",
        "help_line_7":          "ПКМ по футеру — меню настроек",
        "help_line_8":          "Колесо мыши — масштаб шрифта",
        "help_line_9":          "Левый клик по ? — эта справка",
        "help_line_10":         "Закрытие окна — свернуть в трей",
        "disk_used":            "занято",
        "disk_free":            "свободно",
        "disk_total":           "всего",
        "disk_error":           "ошибка",
        "about_title":          "О программе — OS-RSM",
        "about_subtitle":       "Open Source Resource System Monitor",
        "about_version":        "версия",
        "about_original":       "Оригинальный проект (Linux):",
        "about_windows":        "Windows-версия:",
        "about_tech":           "Технологии: Python · psutil · Pillow · pystray · tkinter",
        "about_license":        "Лицензия: свободное использование · см. оригинальный репозиторий",
        "about_close":          "Закрыть",
        "dlg_custom_title":     "CUSTOM",
        "dlg_custom_prompt":    "Введите текст для плитки CUSTOM:",
        "dlg_color_title":      "Цвет плитки",
        "dlg_reset_all_title":  "OS-RSM",
        "dlg_reset_all_msg":    "Сбросить ВСЕ настройки к значениям по умолчанию?",
        "dlg_reset_done_title": "OS-RSM",
        "dlg_reset_done_msg":   "Настройки сброшены. Перезапустите приложение.",
        "dlg_export_title":     "Экспорт конфига",
        "dlg_export_initialfile": "osrsm-config.json",
        "dlg_export_ft":        "JSON",
        "dlg_all_files":        "Все файлы",
        "dlg_export_saved":     "Конфиг сохранён:",
        "dlg_import_title":     "Импорт конфига",
        "dlg_import_confirm":   "Заменить текущие настройки содержимым файла?\nПриложение нужно будет перезапустить.",
        "dlg_import_done":      "Конфиг импортирован.\nПерезапустите приложение, чтобы применить.",
        "dlg_error_title":      "Ошибка",
        "dlg_autostart_err_title": "Автозапуск",
        "dlg_autostart_err_msg":   "Не удалось изменить автозапуск:\n{err}",
        "dlg_autostart_unsupported": "Автозапуск не поддерживается на этой системе.",
    },
    "en": {
        "tray_open":  "Open",
        "tray_quit":  "Quit",
        "menu_visible_disks":   "Visible disks",
        "menu_edit_custom":     "Edit CUSTOM…",
        "menu_temp_units":      "Temperature units",
        "menu_temp_c":          "Celsius (°C)",
        "menu_temp_f":          "Fahrenheit (°F)",
        "menu_theme":           "Theme",
        "menu_theme_auto":      "Auto (system)",
        "menu_theme_light":     "Light",
        "menu_theme_dark":      "Dark",
        "menu_tray_mode":       "Tray mode",
        "menu_tray_single":     "Single metric (current)",
        "menu_tray_dual":       "Two metrics",
        "menu_tray_top":        "Top metric",
        "menu_tray_bottom":     "Bottom metric",
        "menu_inc_font":        "Increase font",
        "menu_dec_font":        "Decrease font",
        "menu_reset_font":      "Reset font (100%)",
        "menu_blink":           "Blink on critical load",
        "menu_autostart":       "Start with system",
        "menu_reset_colors":    "Reset colors to Flat UI",
        "menu_reset_all":       "Reset all…",
        "menu_export":          "Export config…",
        "menu_import":          "Import config…",
        "menu_about":           "About",
        "menu_language":        "Language",
        "menu_lang_ru":         "Русский",
        "menu_lang_en":         "English",
        "menu_system_suffix":   "  (system)",
        "help_title":           "?  Controls",
        "help_line_1":          "Left click on tile — make metric active (in tray)",
        "help_line_2":          "Left click on disk label — disk details",
        "help_line_3":          "2× click on CUSTOM — set custom text",
        "help_line_4":          "2× click on TEMP — toggle °C / °F",
        "help_line_5":          "Right click on value — pick tile color",
        "help_line_6":          "Right click on disk label — disk details",
        "help_line_7":          "Right click on footer — settings menu",
        "help_line_8":          "Mouse wheel — font scale",
        "help_line_9":          "Left click on ? — this help",
        "help_line_10":         "Closing window — minimize to tray",
        "disk_used":            "used",
        "disk_free":            "free",
        "disk_total":           "total",
        "disk_error":           "error",
        "about_title":          "About — OS-RSM",
        "about_subtitle":       "Open Source Resource System Monitor",
        "about_version":        "version",
        "about_original":       "Original project (Linux):",
        "about_windows":        "Windows version:",
        "about_tech":           "Technologies: Python · psutil · Pillow · pystray · tkinter",
        "about_license":        "License: free use · see original repository",
        "about_close":          "Close",
        "dlg_custom_title":     "CUSTOM",
        "dlg_custom_prompt":    "Enter text for CUSTOM tile:",
        "dlg_color_title":      "Tile color",
        "dlg_reset_all_title":  "OS-RSM",
        "dlg_reset_all_msg":    "Reset ALL settings to defaults?",
        "dlg_reset_done_title": "OS-RSM",
        "dlg_reset_done_msg":   "Settings reset. Please restart the application.",
        "dlg_export_title":     "Export config",
        "dlg_export_initialfile": "osrsm-config.json",
        "dlg_export_ft":        "JSON",
        "dlg_all_files":        "All files",
        "dlg_export_saved":     "Config saved:",
        "dlg_import_title":     "Import config",
        "dlg_import_confirm":   "Replace current settings with file contents?\nThe application needs to be restarted.",
        "dlg_import_done":      "Config imported.\nRestart the application to apply.",
        "dlg_error_title":      "Error",
        "dlg_autostart_err_title": "Autostart",
        "dlg_autostart_err_msg":   "Failed to change autostart:\n{err}",
        "dlg_autostart_unsupported": "Autostart is not supported on this system.",
    },
}

LANG = "ru"


def t(key, **kw):
    s = STRINGS.get(LANG, STRINGS["ru"]).get(key, key)
    if kw:
        try:
            return s.format(**kw)
        except Exception:
            return s
    return s


def detect_system_language():
    try:
        if sys.platform == "win32":
            langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            primary = langid & 0x3FF
            if primary == 0x19:
                return "ru"
            return "en"
        elif sys.platform == "darwin":
            out = subprocess.run(
                ["defaults", "read", "-g", "AppleLocale"],
                capture_output=True, text=True, timeout=2)
            s = (out.stdout or "").strip().lower()
            if s.startswith("ru"):
                return "ru"
            return "en"
        else:
            env = (os.environ.get("LANG") or
                   os.environ.get("LC_ALL") or
                   os.environ.get("LC_MESSAGES") or "").lower()
            if env.startswith("ru"):
                return "ru"
    except Exception as e:
        print("detect_system_language:", e)
    return "en"


# =========================================================================
# АВТОЗАПУСК
# =========================================================================
AUTOSTART_NAME = "OS-RSM"


def autostart_supported():
    return sys.platform in ("win32", "linux")


def _autostart_shortcut_path_win():
    startup = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    return os.path.join(startup, AUTOSTART_NAME + ".lnk")


def _autostart_desktop_path_linux():
    return os.path.expanduser(
        f"~/.config/autostart/{AUTOSTART_NAME.lower()}.desktop")


def autostart_path():
    if sys.platform == "win32":
        return _autostart_shortcut_path_win()
    if sys.platform == "linux":
        return _autostart_desktop_path_linux()
    return None


def is_autostart_enabled():
    p = autostart_path()
    if p is None:
        return False
    return os.path.exists(p)


def _target_command():
    """Возвращает (target_path, arguments, working_dir)."""
    if getattr(sys, "frozen", False):
        # запущено как .exe
        return (EXE_PATH, "", os.path.dirname(EXE_PATH))
    # запуск из исходника — используем pythonw.exe без консоли
    py = sys.executable
    pyw = os.path.join(os.path.dirname(py), "pythonw.exe")
    if os.path.exists(pyw):
        py = pyw
    return (py, f'"{EXE_PATH}"', os.path.dirname(EXE_PATH))


def enable_autostart():
    """Создаёт ярлык/файл автозапуска. Кидает исключение при ошибке."""
    if sys.platform == "win32":
        import pythoncom
        from win32com.client import Dispatch
        target, args, workdir = _target_command()
        path = autostart_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pythoncom.CoInitialize()
        try:
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = args
            shortcut.WorkingDirectory = workdir
            ico = os.path.join(BASE_DIR, "assets", "icon.ico")
            if os.path.exists(ico):
                shortcut.IconLocation = ico
            shortcut.save()
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
        return

    if sys.platform == "linux":
        target, args, workdir = _target_command()
        exec_line = target
        if args:
            exec_line += " " + args
        desktop = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            f"Name={APP_NAME}\n"
            "Comment=Open Source Resource System Monitor\n"
            f"Exec={exec_line}\n"
            f"Path={workdir}\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n"
        )
        path = autostart_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(desktop)
        return

    raise RuntimeError(t("dlg_autostart_unsupported"))


def disable_autostart():
    p = autostart_path()
    if p and os.path.exists(p):
        try:
            os.remove(p)
        except Exception:
            raise


def toggle_autostart(enable):
    """Включает/выключает автозапуск. Возвращает True при успехе, иначе кидает."""
    if not autostart_supported():
        raise RuntimeError(t("dlg_autostart_unsupported"))
    if enable:
        enable_autostart()
    else:
        disable_autostart()


# =========================================================================
# ОПРЕДЕЛЕНИЕ ТЕМЫ
# =========================================================================
def detect_system_theme():
    try:
        if sys.platform == "win32":
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as k:
                val, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
                return "light" if val == 1 else "dark"
        elif sys.platform == "darwin":
            out = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True, timeout=2)
            if "Dark" in (out.stdout or ""):
                return "dark"
            return "light"
        else:
            try:
                out = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface",
                     "color-scheme"],
                    capture_output=True, text=True, timeout=2)
                s = (out.stdout or "").strip().lower()
                if "dark" in s:
                    return "dark"
                if "light" in s or "default" in s:
                    return "light"
            except Exception:
                pass
            env = os.environ.get("GTK_THEME", "").lower()
            if "dark" in env:
                return "dark"
    except Exception as e:
        print("detect_system_theme:", e)
    return "dark"


def resolve_theme():
    pref = CONFIG.get("theme", "auto")
    if pref == "light":
        return "light"
    if pref == "dark":
        return "dark"
    return detect_system_theme()


# =========================================================================
# ПАЛИТРА
# =========================================================================
THEME_COLORS = {
    "dark": {
        "BG":             "#1e1e1e",
        "POPUP_BG":       "#252525",
        "POPUP_BORDER":   "#3a3a3a",
        "TEXT_PRIMARY":   "#dddddd",
        "TEXT_SECONDARY": "#cccccc",
        "TEXT_MUTED":     "#777777",
        "TEXT_FAINT":     "#999999",
        "FOOTER_BTN_BG":  "#333333",
        "FOOTER_BTN_FG":  "#cccccc",
        "MENU_BG":        "#252525",
        "MENU_FG":        "#dddddd",
        "MENU_ACTIVE_BG": "#3a3a3a",
        "MENU_ACTIVE_FG": "#ffffff",
        "BAR_BG":         "#333333",
        "BAR_TEXT_ON_EMPTY": "#cccccc",
        "LINK_FG":        "#4ea1ff",
        "DISABLED":       "#666666",
    },
    "light": {
        "BG":             "#f5f5f5",
        "POPUP_BG":       "#ffffff",
        "POPUP_BORDER":   "#d0d0d0",
        "TEXT_PRIMARY":   "#222222",
        "TEXT_SECONDARY": "#444444",
        "TEXT_MUTED":     "#888888",
        "TEXT_FAINT":     "#777777",
        "FOOTER_BTN_BG":  "#e0e0e0",
        "FOOTER_BTN_FG":  "#333333",
        "MENU_BG":        "#ffffff",
        "MENU_FG":        "#222222",
        "MENU_ACTIVE_BG": "#e5e5e5",
        "MENU_ACTIVE_FG": "#000000",
        "BAR_BG":         "#e8e8e8",
        "BAR_TEXT_ON_EMPTY": "#666666",
        "LINK_FG":        "#0066cc",
        "DISABLED":       "#aaaaaa",
    },
}


# =========================================================================
# ШРИФТЫ
# =========================================================================
BOLD_FONT_CANDIDATES = [
    "dejavu-sans.bold.ttf",
    "DejaVuSans-Bold.ttf", "DejaVuSans-Bold.otf",
    "arialbd.ttf", "Arial Bold.ttf", "Arial_Bold.ttf",
    "LiberationSans-Bold.ttf", "Roboto-Bold.ttf",
    "NotoSans-Bold.ttf", "SegoeUI-Bold.ttf", "segoeuib.ttf",
]
REGULAR_FONT_CANDIDATES = [
    "DejaVuSans.ttf", "arial.ttf", "Arial.ttf",
    "LiberationSans-Regular.ttf", "Roboto-Regular.ttf",
    "NotoSans-Regular.ttf", "SegoeUI.ttf", "segoeui.ttf",
]


def _find_font_in_dir(names):
    try:
        local = os.listdir(FONTS_DIR)
    except OSError:
        local = []
    lower_map = {f.lower(): f for f in local}
    for n in names:
        if n.lower() in lower_map:
            return os.path.join(FONTS_DIR, lower_map[n.lower()])

    system_dirs = []
    if sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        system_dirs.append(os.path.join(windir, "Fonts"))
    elif sys.platform == "darwin":
        system_dirs += ["/System/Library/Fonts", "/Library/Fonts",
                        os.path.expanduser("~/Library/Fonts")]
    else:
        system_dirs += [
            "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts/truetype/liberation",
            "/usr/share/fonts/TTF",
            "/usr/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
        ]

    for d in system_dirs:
        if not os.path.isdir(d):
            continue
        try:
            files = os.listdir(d)
        except OSError:
            continue
        lower = {f.lower(): f for f in files}
        for n in names:
            if n.lower() in lower:
                return os.path.join(d, lower[n.lower()])
    return None


BOLD_FONT_FILE = _find_font_in_dir(BOLD_FONT_CANDIDATES)
REGULAR_FONT_FILE = _find_font_in_dir(REGULAR_FONT_CANDIDATES)

FONT_FILE = BOLD_FONT_FILE or REGULAR_FONT_FILE
if FONT_FILE is None:
    try:
        files = os.listdir(FONTS_DIR)
    except OSError:
        files = []
    for f in sorted(files):
        if f.lower().endswith((".ttf", ".otf")):
            FONT_FILE = os.path.join(FONTS_DIR, f)
            break

POPUP_FONT_FILE = _find_font_in_dir(["dejavu-sans.bold.ttf",
                                     "DejaVuSans-Bold.ttf",
                                     "DejaVuSans-Bold.otf"]) or BOLD_FONT_FILE


# =========================================================================
# ДИСКАВЕРИ
# =========================================================================
def get_system_mount():
    if sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        return os.path.splitdrive(windir)[0] + "\\"
    return "/"


def get_volume_label(mount):
    if sys.platform != "win32":
        return ""
    try:
        letter = mount.rstrip("\\/").rstrip(":").upper()
        if not letter:
            return ""
        buf = ctypes.create_unicode_buffer(261)
        fs = ctypes.create_unicode_buffer(261)
        serial = ctypes.c_uint()
        maxlen = ctypes.c_uint()
        flags = ctypes.c_uint()
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(letter + ":\\"),
            buf, 261, ctypes.byref(serial),
            ctypes.byref(maxlen), ctypes.byref(flags), fs, 261)
        return buf.value if ok else ""
    except Exception:
        return ""


def short_disk_label(mount, is_system):
    if sys.platform == "win32":
        letter = mount.rstrip("\\/").rstrip(":").upper()
        return f"DISK {letter}" if letter else "DISK"
    if mount == "/":
        return "DISK /"
    name = mount.rstrip("/").split("/")[-1].upper() or "/"
    return f"DISK {name}"


def discover_disks():
    result = []
    system_mount = get_system_mount()
    try:
        parts = psutil.disk_partitions(all=False)
    except Exception as e:
        print("disk_partitions:", e)
        parts = []

    seen = set()
    for p in parts:
        mp = p.mountpoint
        if not mp or mp in seen:
            continue
        if "cdrom" in p.opts.lower():
            continue
        if not p.fstype:
            continue
        try:
            psutil.disk_usage(mp)
        except Exception:
            continue
        seen.add(mp)

        if sys.platform == "win32":
            is_system = (os.path.normcase(mp.rstrip("\\")) ==
                         os.path.normcase(system_mount.rstrip("\\")))
        else:
            is_system = (mp == system_mount)

        if sys.platform == "win32":
            letter = mp.rstrip("\\/").rstrip(":").upper()
            key = "DISK_SYSTEM" if is_system else f"DISK_{letter}"
        else:
            key = "DISK_ROOT" if mp == "/" else \
                  f"DISK_{mp.strip('/').upper().replace('/', '_')}"

        result.append({
            "key": key,
            "label": short_disk_label(mp, is_system),
            "mount": mp,
            "is_system": is_system,
        })

    result.sort(key=lambda d: (not d["is_system"], d["label"]))
    return result


DISKS = discover_disks()
print("Discovered disks:", [(d["key"], d["mount"], d["is_system"]) for d in DISKS])


# =========================================================================
# КОНФИГ
# =========================================================================
DEFAULT_COLORS = {
    "CPU":  "#2ecc71",
    "RAM":  "#9b59b6",
    "SWAP": "#3498db",
    "TEMP": "#e74c3c",
    "CUSTOM": "#95a5a6",
    "__disk_default__": "#f1c40f",
    "__temp_na__": "#7f8c8d",
}

WARN_OUTLINE_RGB = (44, 62, 80)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("config broken:", e)
        return {}


def save_config(cfg):
    d = os.path.dirname(CONFIG_PATH)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


CONFIG = load_config()

COLORS = dict(DEFAULT_COLORS)
COLORS.update(CONFIG.get("colors", {}))


def color_for(key):
    if key in COLORS:
        return COLORS[key]
    if key.startswith("DISK_"):
        return COLORS.get("__disk_default__", "#f1c40f")
    return "#95a5a6"


if "show_disks" not in CONFIG:
    SHOWN_DISKS = [d["key"] for d in DISKS]
    CONFIG["show_disks"] = SHOWN_DISKS
    save_config(CONFIG)
else:
    SHOWN_DISKS = CONFIG["show_disks"]

POPUP_AUTOCLOSE_SEC = int(CONFIG.get("popup_autoclose_sec", 5))
if "popup_autoclose_sec" not in CONFIG:
    CONFIG["popup_autoclose_sec"] = POPUP_AUTOCLOSE_SEC
    save_config(CONFIG)

BLINK_ON_CRITICAL = bool(CONFIG.get("blink_on_critical", True))
if "blink_on_critical" not in CONFIG:
    CONFIG["blink_on_critical"] = BLINK_ON_CRITICAL
    save_config(CONFIG)

WIN_X = CONFIG.get("win_x")
WIN_Y = CONFIG.get("win_y")

if "theme" not in CONFIG:
    CONFIG["theme"] = "auto"
    save_config(CONFIG)

TRAY_MODE = CONFIG.get("tray_mode", "single")
if "tray_mode" not in CONFIG:
    CONFIG["tray_mode"] = TRAY_MODE
    save_config(CONFIG)

TRAY_TOP_KEY = CONFIG.get("tray_top", "CPU")
if "tray_top" not in CONFIG:
    CONFIG["tray_top"] = TRAY_TOP_KEY
    save_config(CONFIG)

TRAY_BOTTOM_KEY = CONFIG.get("tray_bottom", "RAM")
if "tray_bottom" not in CONFIG:
    CONFIG["tray_bottom"] = TRAY_BOTTOM_KEY
    save_config(CONFIG)

if "language" not in CONFIG:
    CONFIG["language"] = "auto"
    save_config(CONFIG)

_lang_pref = CONFIG.get("language", "auto")
if _lang_pref == "auto":
    LANG = detect_system_language()
elif _lang_pref in ("ru", "en"):
    LANG = _lang_pref
else:
    LANG = detect_system_language()

THEME = resolve_theme()

BG = THEME_COLORS[THEME]["BG"]
POPUP_BG = THEME_COLORS[THEME]["POPUP_BG"]
POPUP_BORDER = THEME_COLORS[THEME]["POPUP_BORDER"]
TEXT_PRIMARY = THEME_COLORS[THEME]["TEXT_PRIMARY"]
TEXT_SECONDARY = THEME_COLORS[THEME]["TEXT_SECONDARY"]
TEXT_MUTED = THEME_COLORS[THEME]["TEXT_MUTED"]
TEXT_FAINT = THEME_COLORS[THEME]["TEXT_FAINT"]
FOOTER_BTN_BG = THEME_COLORS[THEME]["FOOTER_BTN_BG"]
FOOTER_BTN_FG = THEME_COLORS[THEME]["FOOTER_BTN_FG"]
MENU_BG = THEME_COLORS[THEME]["MENU_BG"]
MENU_FG = THEME_COLORS[THEME]["MENU_FG"]
MENU_ACTIVE_BG = THEME_COLORS[THEME]["MENU_ACTIVE_BG"]
MENU_ACTIVE_FG = THEME_COLORS[THEME]["MENU_ACTIVE_FG"]
BAR_BG = THEME_COLORS[THEME]["BAR_BG"]
BAR_TEXT_ON_EMPTY = THEME_COLORS[THEME]["BAR_TEXT_ON_EMPTY"]
LINK_FG = THEME_COLORS[THEME]["LINK_FG"]
DISABLED_FG = THEME_COLORS[THEME]["DISABLED"]


# =========================================================================
# МЕТРИКИ
# =========================================================================
def get_cpu():
    return psutil.cpu_percent(interval=None)


def get_ram():
    return psutil.virtual_memory().percent


def get_swap():
    return psutil.swap_memory().percent


def get_temp_c():
    try:
        temps = psutil.sensors_temperatures()
    except Exception:
        return None
    if not temps:
        return None
    for name in ("coretemp", "k10temp", "zenpower", "acpitz"):
        if name in temps and temps[name]:
            return temps[name][0].current
    for v in temps.values():
        if v:
            return v[0].current
    return None


def make_disk_fn(mount):
    def _fn():
        try:
            return psutil.disk_usage(mount).percent
        except Exception:
            return None
    return _fn


BASE_METRICS = {
    "CPU":  {"fn": get_cpu,    "label": "CPU"},
    "RAM":  {"fn": get_ram,    "label": "RAM"},
    "SWAP": {"fn": get_swap,   "label": "SWAP"},
    "TEMP": {"fn": get_temp_c, "label": "TEMP"},
}

CUSTOM_KEY = "CUSTOM"


def build_metrics():
    m = {}
    m["CPU"] = BASE_METRICS["CPU"]
    m["RAM"] = BASE_METRICS["RAM"]
    for d in DISKS:
        if d["key"] in SHOWN_DISKS:
            m[d["key"]] = {
                "fn": make_disk_fn(d["mount"]),
                "label": d["label"],
                "mount": d["mount"],
                "is_system": d["is_system"],
            }
    m["SWAP"] = BASE_METRICS["SWAP"]
    m["TEMP"] = BASE_METRICS["TEMP"]
    return m


METRICS = build_metrics()


def rebuild_metrics():
    global METRICS
    METRICS = build_metrics()


def is_disk_key(key):
    return key in METRICS and "mount" in METRICS[key]


# =========================================================================
# HEX / LUM
# =========================================================================
def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def lum(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


# =========================================================================
# ШРИФТЫ (кэш)
# =========================================================================
_font_cache = {}
_popup_font_cache = {}


def get_font(size, bold=True):
    key = (int(size), bold)
    if key in _font_cache:
        return _font_cache[key]
    size = max(6, int(size))

    paths = []
    if bold:
        if BOLD_FONT_FILE:
            paths.append(BOLD_FONT_FILE)
        paths += ["dejavu-sans.bold.ttf",
                  "DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"]
    else:
        if REGULAR_FONT_FILE:
            paths.append(REGULAR_FONT_FILE)
        paths += ["DejaVuSans.ttf", "arial.ttf", "Arial.ttf"]

    font = None
    for p in paths:
        try:
            font = ImageFont.truetype(p, size)
            break
        except Exception:
            continue
    if font is None and FONT_FILE:
        try:
            font = ImageFont.truetype(FONT_FILE, size)
        except Exception:
            font = None
    if font is None:
        font = ImageFont.load_default()

    _font_cache[key] = font
    return font


def _popup_tk_font(size=10, bold=False):
    if sys.platform == "win32":
        family = "Segoe UI"
    elif sys.platform == "darwin":
        family = "Helvetica"
    else:
        family = "DejaVu Sans"
    return (family, size, "bold") if bold else (family, size)


# =========================================================================
# СОСТОЯНИЕ
# =========================================================================
class State:
    def __init__(self):
        cur = CONFIG.get("current", "CPU")
        if cur != CUSTOM_KEY and cur not in METRICS:
            cur = "CPU"
        self.current = cur
        self.custom_text = CONFIG.get("custom_text", "")
        self.temp_unit = CONFIG.get("temp_unit", "C")
        self.font_scale = float(CONFIG.get("font_scale", 1.0))
        self.values = {k: 0 for k in METRICS}
        self.blink_state = False
        self.lock = threading.Lock()


state = State()


def _scaled(n):
    return max(6, int(round(n * state.font_scale)))


def stats_worker():
    psutil.cpu_percent(interval=None)
    while True:
        for name, meta in METRICS.items():
            try:
                v = meta["fn"]()
            except Exception:
                v = None
            with state.lock:
                state.values[name] = v
        time.sleep(1.0)


# =========================================================================
# ИКОНКА ТРЕЯ
# =========================================================================
WARN_THRESHOLD = 85
WARN_TEMP_C = 80
CRITICAL_THRESHOLD = 95
CRITICAL_TEMP_C = 90

TRAY_SIZE = 64


def _is_warn(key, val):
    if val is None:
        return False
    if key == "TEMP":
        with state.lock:
            unit = state.temp_unit
        t_c = val if unit == "C" else (val - 32) * 5 / 9
        return t_c >= WARN_TEMP_C
    return val >= WARN_THRESHOLD


def _is_critical(key, val):
    if val is None:
        return False
    if key == "TEMP":
        with state.lock:
            unit = state.temp_unit
        t_c = val if unit == "C" else (val - 32) * 5 / 9
        return t_c >= CRITICAL_TEMP_C
    return val >= CRITICAL_THRESHOLD


def _metric_color_rgb(key):
    if key == CUSTOM_KEY:
        return hex_to_rgb(color_for(CUSTOM_KEY))
    if key == "TEMP":
        with state.lock:
            raw = state.values.get("TEMP", 0)
        if raw is None:
            return hex_to_rgb(COLORS["__temp_na__"])
        return hex_to_rgb(color_for("TEMP"))
    if key in METRICS:
        return hex_to_rgb(color_for(key))
    return (128, 128, 128)


def _metric_text_value(key):
    with state.lock:
        custom = state.custom_text
        unit = state.temp_unit
        raw = state.values.get(key, 0)
    if key == CUSTOM_KEY:
        return (custom if custom else "·", False)
    if key == "TEMP":
        if raw is None:
            return ("—", False)
        t_val = int(round(raw))
        if unit == "F":
            t_val = int(round(t_val * 9 / 5 + 32))
        return (str(t_val), True)
    if raw is None:
        return ("--", False)
    return (str(int(round(raw))), False)


def _draw_value_on_canvas(draw, box, text, font, fill):
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    cx = x0 + (x1 - x0 - tw) / 2 - bbox[0]
    cy = y0 + (y1 - y0 - th) / 2 - bbox[1]
    draw.text((cx, cy), text, font=font, fill=fill)


def _fit_font_to_box(draw, text, max_w, max_h, start_size):
    size = int(start_size)
    while size > 8:
        f = get_font(size, bold=True)
        bbox = draw.textbbox((0, 0), text, font=f)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= max_w and h <= max_h:
            return f
        size -= 2
    return get_font(8, bold=True)


def _render_single_icon():
    with state.lock:
        name = state.current
        blink = state.blink_state
        raw = state.values.get(name, 0)
    critical = BLINK_ON_CRITICAL and _is_critical(name, raw) and blink
    color = _metric_color_rgb(name)
    if critical:
        color = (150, 30, 30)
    size = TRAY_SIZE
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1, 1, size - 2, size - 2), radius=6, fill=color)
    if _is_warn(name, raw) and not critical:
        d.rounded_rectangle((1, 1, size - 2, size - 2), radius=6,
                            outline=WARN_OUTLINE_RGB, width=4)
    fg = (0, 0, 0) if lum(color) > 140 else (255, 255, 255)
    text, is_temp = _metric_text_value(name)
    if is_temp:
        f_big = get_font(48, bold=True)
        bbox = d.textbbox((0, 0), text, font=f_big)
        tw = bbox[2] - bbox[0]
        d.text(((size - tw) / 2 - bbox[0], -2 - bbox[1]),
               text, font=f_big, fill=fg)
        with state.lock:
            unit = state.temp_unit
        deg = "°C" if unit == "C" else "°F"
        f_deg = get_font(16, bold=True)
        bb = d.textbbox((0, 0), deg, font=f_deg)
        dw = bb[2] - bb[0]
        d.text(((size - dw) / 2 - bb[0], size - 20 - bb[1]),
               deg, font=f_deg, fill=fg)
    else:
        f_big = _fit_font_to_box(d, text, size - 8, size - 8, 52)
        bbox = d.textbbox((0, 0), text, font=f_big)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
               text, font=f_big, fill=fg)
    return img


def _render_dual_icon():
    with state.lock:
        blink = state.blink_state
        raw_top = state.values.get(TRAY_TOP_KEY, 0)
        raw_bottom = state.values.get(TRAY_BOTTOM_KEY, 0)
    any_critical = BLINK_ON_CRITICAL and (
        _is_critical(TRAY_TOP_KEY, raw_top) or
        _is_critical(TRAY_BOTTOM_KEY, raw_bottom)
    ) and blink
    any_warn = _is_warn(TRAY_TOP_KEY, raw_top) or \
               _is_warn(TRAY_BOTTOM_KEY, raw_bottom)
    color_top = _metric_color_rgb(TRAY_TOP_KEY)
    color_bottom = _metric_color_rgb(TRAY_BOTTOM_KEY)
    if any_critical:
        color_top = (150, 30, 30)
        color_bottom = (150, 30, 30)
    size = TRAY_SIZE
    split = size // 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1, 1, size - 2, split + 3), radius=6, fill=color_top)
    d.rounded_rectangle((1, split - 3, size - 2, size - 2), radius=6,
                        fill=color_bottom)
    d.rectangle((1, split - 1, size - 2, split + 1), fill=(0, 0, 0, 0))
    if any_warn and not any_critical:
        d.rounded_rectangle((1, 1, size - 2, size - 2), radius=6,
                            outline=WARN_OUTLINE_RGB, width=3)
    text_top, is_temp_top = _metric_text_value(TRAY_TOP_KEY)
    text_bottom, is_temp_bottom = _metric_text_value(TRAY_BOTTOM_KEY)
    fg_top = (0, 0, 0) if lum(color_top) > 140 else (255, 255, 255)
    fg_bottom = (0, 0, 0) if lum(color_bottom) > 140 else (255, 255, 255)
    box_top = (2, 2, size - 2, split - 1)
    max_h_top = (split - 1) - 2 - 2
    f_top = _fit_font_to_box(d, text_top, size - 6, max_h_top, 30)
    _draw_value_on_canvas(d, box_top, text_top, f_top, fg_top)
    box_bottom = (2, split + 1, size - 2, size - 2)
    max_h_bottom = (size - 2) - (split + 1) - 2
    f_bot = _fit_font_to_box(d, text_bottom, size - 6, max_h_bottom, 30)
    _draw_value_on_canvas(d, box_bottom, text_bottom, f_bot, fg_bottom)
    return img


def render_tray_icon():
    if TRAY_MODE == "dual":
        return _render_dual_icon()
    return _render_single_icon()


ui_queue = queue.Queue()


def build_tray():
    def on_open(icon, item_):
        ui_queue.put("open_window")

    def on_quit(icon, item_):
        icon.stop()
        ui_queue.put("quit")

    icon = pystray.Icon(
        name="sysmon",
        icon=render_tray_icon(),
        title=APP_NAME + " · v" + APP_VERSION,
        menu=pystray.Menu(
            item(t("tray_open"), on_open, default=True),
            item(t("tray_quit"), on_quit),
        ),
    )

    def refresh():
        while True:
            try:
                icon.icon = render_tray_icon()
            except Exception as e:
                print("tray refresh:", e)
            time.sleep(0.7)

    def blink_loop():
        while True:
            time.sleep(0.7)
            try:
                with state.lock:
                    if TRAY_MODE == "dual":
                        raw_top = state.values.get(TRAY_TOP_KEY, 0)
                        raw_bottom = state.values.get(TRAY_BOTTOM_KEY, 0)
                        crit = (_is_critical(TRAY_TOP_KEY, raw_top) or
                                _is_critical(TRAY_BOTTOM_KEY, raw_bottom))
                    else:
                        name = state.current
                        raw = state.values.get(name, 0)
                        crit = _is_critical(name, raw)
                    if BLINK_ON_CRITICAL and crit:
                        state.blink_state = not state.blink_state
                    else:
                        state.blink_state = False
            except Exception:
                pass

    threading.Thread(target=refresh, daemon=True).start()
    threading.Thread(target=blink_loop, daemon=True).start()
    return icon


# =========================================================================
# ОТРИСОВКА ПЛИТКИ
# =========================================================================
TILE_SIZE = 110
TILE_RENDER_SIZE = TILE_SIZE

VALUE_TOP_PAD_RATIO    = 0.02
VALUE_MAX_WIDTH_RATIO  = 0.92
VALUE_MAX_HEIGHT_RATIO = 0.85

LABEL_HEIGHT_RATIO     = 0.16
LABEL_BOTTOM_PAD_RATIO = 0.03
LABEL_MAX_WIDTH_RATIO  = 0.96

LABEL_CLICK_ZONE_RATIO = 0.72


def _fit_font(text, max_w, max_h, start_size, bold=True):
    size = int(start_size)
    while size > 6:
        f = get_font(_scaled(size), bold=bold)
        try:
            bbox = f.getbbox(text)
        except Exception:
            tmp = Image.new("RGB", (10, 10))
            bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=f)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= max_w and h <= max_h:
            return f, bbox
        size -= 1
    f = get_font(_scaled(6), bold=bold)
    tmp = Image.new("RGB", (10, 10))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=f)
    return f, bbox


def render_tile_image(color_hex, value_text, label_text,
                      hovered, pressed, active):
    s = TILE_RENDER_SIZE
    img = Image.new("RGB", (s, s), color_hex)
    d = ImageDraw.Draw(img)
    rgb = hex_to_rgb(color_hex)
    fg = (0, 0, 0) if lum(rgb) > 140 else (255, 255, 255)
    if active:
        bar_h = max(3, int(s * 0.06))
        d.rectangle((0, 0, s, bar_h), fill=(255, 255, 255))
    top_pad = int(s * VALUE_TOP_PAD_RATIO)
    lbl_h = int(s * LABEL_HEIGHT_RATIO)
    lbl_pad = int(s * LABEL_BOTTOM_PAD_RATIO)
    label_top = s - lbl_pad - lbl_h
    value_h = label_top - top_pad - int(s * 0.02)
    max_val_w = int(s * VALUE_MAX_WIDTH_RATIO)
    max_val_h = min(value_h, int(s * VALUE_MAX_HEIGHT_RATIO))
    start_size = int(s * VALUE_MAX_HEIGHT_RATIO)
    f_val, bb = _fit_font(value_text, max_val_w, max_val_h, start_size, bold=True)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    d.text(((s - tw) // 2 - bb[0],
            top_pad + (value_h - th) // 2 - bb[1]),
           value_text, font=f_val, fill=fg)
    start_lbl = int(lbl_h * 1.1)
    f_lbl, bb2 = _fit_font(label_text, int(s * LABEL_MAX_WIDTH_RATIO),
                           lbl_h, start_lbl, bold=True)
    lw = bb2[2] - bb2[0]
    lh = bb2[3] - bb2[1]
    d.text(((s - lw) // 2 - bb2[0],
            label_top + (lbl_h - lh) // 2 - bb2[1]),
           label_text, font=f_lbl, fill=fg)
    return ImageTk.PhotoImage(img)


# =========================================================================
# ПОПАП ДИСКА
# =========================================================================
class DiskPopup:
    def __init__(self, root):
        self.root = root
        self.top = None
        self.current_key = None
        self.update_job = None
        self.autoclose_job = None
        self.mouse_inside = False
        self.lbl_title = None
        self.bar_bg = None
        self.bar = None
        self.lbl_bar_text = None
        self.lbl_used = None
        self.lbl_free = None
        self.lbl_total = None

    def show(self, key):
        if not is_disk_key(key):
            return
        self.current_key = key
        if self.top is None or not self.top.winfo_exists():
            self._build()
        self._refresh()
        self._position_near_window()
        self.top.deiconify()
        self.top.lift()
        self.top.attributes("-topmost", True)
        self.top.attributes("-topmost", False)
        self._reset_autoclose()

    def close(self):
        if self.update_job is not None:
            try:
                self.root.after_cancel(self.update_job)
            except Exception:
                pass
            self.update_job = None
        if self.autoclose_job is not None:
            try:
                self.root.after_cancel(self.autoclose_job)
            except Exception:
                pass
            self.autoclose_job = None
        if self.top is not None and self.top.winfo_exists():
            self.top.destroy()
        self.top = None
        self.current_key = None
        self.mouse_inside = False

    def _build(self):
        top = tk.Toplevel(self.root)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg=POPUP_BORDER)
        self.top = top
        outer = tk.Frame(top, bg=POPUP_BORDER)
        outer.pack(fill="both", expand=True, padx=1, pady=1)
        inner = tk.Frame(outer, bg=POPUP_BG, padx=16, pady=14)
        inner.pack(fill="both", expand=True)
        header = tk.Frame(inner, bg=POPUP_BG)
        header.pack(fill="x")
        self.lbl_title = tk.Label(header, text="", fg=TEXT_PRIMARY, bg=POPUP_BG,
                                  font=_popup_tk_font(12, bold=True),
                                  anchor="w")
        self.lbl_title.pack(side="left")
        close_btn = tk.Label(header, text=" × ", fg=TEXT_MUTED, bg=POPUP_BG,
                             font=_popup_tk_font(13, bold=True),
                             cursor="hand2", padx=4)
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.close())
        sep = tk.Frame(inner, bg=POPUP_BORDER, height=1)
        sep.pack(fill="x", pady=(10, 12))
        self.bar_bg = tk.Frame(inner, bg=BAR_BG, height=20)
        self.bar_bg.pack(fill="x")
        self.bar_bg.pack_propagate(False)
        self.bar = tk.Frame(self.bar_bg, bg="#2ecc71", height=20)
        self.bar.place(x=0, y=0, relheight=1.0, relwidth=0.0)
        self.lbl_bar_text = tk.Label(
            self.bar_bg, text="", fg="#ffffff", bg=BAR_BG,
            font=_popup_tk_font(10, bold=True))
        self.lbl_bar_text.place(relx=0.5, rely=0.5, anchor="center")
        info = tk.Frame(inner, bg=POPUP_BG)
        info.pack(fill="x", pady=(14, 0))
        self.lbl_used = tk.Label(info, text="", fg=TEXT_SECONDARY, bg=POPUP_BG,
                                 font=_popup_tk_font(10), anchor="w")
        self.lbl_used.pack(fill="x", pady=(0, 3))
        self.lbl_free = tk.Label(info, text="", fg=TEXT_SECONDARY, bg=POPUP_BG,
                                 font=_popup_tk_font(10), anchor="w")
        self.lbl_free.pack(fill="x", pady=(0, 3))
        self.lbl_total = tk.Label(info, text="", fg=TEXT_MUTED, bg=POPUP_BG,
                                  font=_popup_tk_font(10), anchor="w")
        self.lbl_total.pack(fill="x")
        for w in (top, outer, inner, header, self.lbl_title, close_btn,
                  self.bar_bg, self.bar, self.lbl_bar_text,
                  self.lbl_used, self.lbl_free, self.lbl_total, info):
            w.bind("<Enter>", self._on_mouse_enter, add="+")
            w.bind("<Leave>", self._on_mouse_leave, add="+")
            w.bind("<Motion>", self._on_mouse_activity, add="+")
            w.bind("<Button-1>", self._on_mouse_activity, add="+")
            w.bind("<MouseWheel>", self._on_mouse_activity, add="+")
            w.bind("<Button-4>", self._on_mouse_activity, add="+")
            w.bind("<Button-5>", self._on_mouse_activity, add="+")
        top.bind("<Escape>", lambda e: self.close())

    def _position_near_window(self):
        if self.top is None or not self.top.winfo_exists():
            return
        self.top.update_idletasks()
        pw = self.top.winfo_reqwidth()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        x = rx + rw + 8
        y = ry + 20
        sw = self.root.winfo_screenwidth()
        if x + pw > sw - 10:
            x = rx - pw - 8
            if x < 10:
                x = 10
        self.top.geometry(f"+{x}+{y}")

    def _on_mouse_enter(self, event=None):
        self.mouse_inside = True
        if self.autoclose_job is not None:
            try:
                self.root.after_cancel(self.autoclose_job)
            except Exception:
                pass
            self.autoclose_job = None

    def _on_mouse_leave(self, event=None):
        if self.top is None or not self.top.winfo_exists():
            return
        try:
            x, y = self.root.winfo_pointerxy()
            wx = self.top.winfo_rootx()
            wy = self.top.winfo_rooty()
            ww = self.top.winfo_width()
            wh = self.top.winfo_height()
            if wx <= x <= wx + ww and wy <= y <= wy + wh:
                return
        except Exception:
            pass
        self.mouse_inside = False
        self._reset_autoclose()

    def _on_mouse_activity(self, event=None):
        if self.mouse_inside:
            return
        self._reset_autoclose()

    def _reset_autoclose(self):
        if self.autoclose_job is not None:
            try:
                self.root.after_cancel(self.autoclose_job)
            except Exception:
                pass
            self.autoclose_job = None
        if POPUP_AUTOCLOSE_SEC <= 0:
            return
        if self.mouse_inside:
            return
        self.autoclose_job = self.root.after(
            POPUP_AUTOCLOSE_SEC * 1000, self.close)

    def _refresh(self):
        if self.top is None or not self.top.winfo_exists():
            return
        key = self.current_key
        if key is None or not is_disk_key(key):
            return
        meta = METRICS[key]
        mount = meta["mount"]
        label = meta["label"]
        try:
            u = psutil.disk_usage(mount)
            total, used, free, percent = u.total, u.used, u.free, u.percent
        except Exception as e:
            self.lbl_title.configure(text=f"{label} — {t('disk_error')}: {e}")
            self.update_job = self.root.after(2000, self._refresh)
            return
        vol_label = get_volume_label(mount)
        if sys.platform == "win32" and vol_label:
            letter = mount.rstrip("\\/").rstrip(":").upper()
            title = f"{vol_label} ({letter}:)"
        else:
            title = f"{label} — {mount}"
        self.lbl_title.configure(text=title)
        frac = max(0.0, min(1.0, percent / 100.0))
        if percent < 70:
            bar_color = "#2ecc71"
        elif percent < 88:
            bar_color = "#f1c40f"
        else:
            bar_color = "#e74c3c"
        self.bar.place_configure(relwidth=frac)
        self.bar.configure(bg=bar_color)
        if frac >= 0.5:
            self.lbl_bar_text.configure(bg=bar_color, fg="#ffffff",
                                        text=f"{percent:.0f}%")
        else:
            self.lbl_bar_text.configure(bg=BAR_BG, fg=BAR_TEXT_ON_EMPTY,
                                        text=f"{percent:.0f}%")
        self.lbl_used.configure(text=f"{self._fmt_gb(used)}  {t('disk_used')}")
        self.lbl_free.configure(text=f"{self._fmt_gb(free)}  {t('disk_free')}")
        self.lbl_total.configure(text=f"{self._fmt_gb(total)}  {t('disk_total')}")
        if self.update_job is not None:
            try:
                self.root.after_cancel(self.update_job)
            except Exception:
                pass
        self.update_job = self.root.after(1000, self._refresh)

    @staticmethod
    def _fmt_gb(bytes_val):
        gb = bytes_val / 1e9
        if gb < 100:
            return f"{gb:.1f} GB"
        return f"{gb:.0f} GB"


# =========================================================================
# О ПРОГРАММЕ
# =========================================================================
class AboutPopup:
    def __init__(self, root):
        self.root = root
        self.top = None

    def show(self):
        if self.top is not None and self.top.winfo_exists():
            self.top.lift()
            self.top.focus_force()
            return
        self.top = tk.Toplevel(self.root)
        self.top.title(t("about_title"))
        self.top.configure(bg=POPUP_BG)
        self.top.resizable(False, False)
        self.top.transient(self.root)
        try:
            icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
            img = tk.PhotoImage(file=icon_path)
            self.top.iconphoto(False, img)
        except Exception:
            pass
        wrap = tk.Frame(self.top, bg=POPUP_BG, padx=22, pady=18)
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text=APP_NAME, fg=TEXT_PRIMARY, bg=POPUP_BG,
                 font=_popup_tk_font(18, bold=True),
                 anchor="w").pack(fill="x")
        tk.Label(wrap, text=t("about_subtitle"),
                 fg=TEXT_FAINT, bg=POPUP_BG,
                 font=_popup_tk_font(10),
                 anchor="w").pack(fill="x")
        tk.Label(wrap, text=f"{t('about_version')} {APP_VERSION}",
                 fg=TEXT_FAINT, bg=POPUP_BG,
                 font=_popup_tk_font(10),
                 anchor="w").pack(fill="x", pady=(0, 10))
        tk.Frame(wrap, bg=POPUP_BORDER, height=1).pack(fill="x", pady=8)
        tk.Label(wrap, text=t("about_original"),
                 fg=TEXT_SECONDARY, bg=POPUP_BG,
                 font=_popup_tk_font(10, bold=True),
                 anchor="w").pack(fill="x", pady=(4, 2))
        self._link(wrap, "MihanPROJECTS", "https://github.com/MihanPROJECTS")
        self._link(wrap, "github.com/MihanPROJECTS/OS-RSM",
                   "https://github.com/MihanPROJECTS/OS-RSM")
        tk.Label(wrap, text=t("about_windows"),
                 fg=TEXT_SECONDARY, bg=POPUP_BG,
                 font=_popup_tk_font(10, bold=True),
                 anchor="w").pack(fill="x", pady=(10, 2))
        self._link(wrap, "alkidnn", "https://github.com/alkidnn")
        tk.Frame(wrap, bg=POPUP_BORDER, height=1).pack(fill="x", pady=10)
        tk.Label(wrap, text=t("about_tech"),
                 fg=TEXT_FAINT, bg=POPUP_BG,
                 font=_popup_tk_font(9),
                 anchor="w").pack(fill="x")
        tk.Label(wrap, text=t("about_license"),
                 fg=TEXT_FAINT, bg=POPUP_BG,
                 font=_popup_tk_font(9),
                 anchor="w").pack(fill="x", pady=(2, 0))
        tk.Button(wrap, text=t("about_close"), command=self.close,
                  bg=FOOTER_BTN_BG, fg=TEXT_PRIMARY,
                  activebackground=MENU_ACTIVE_BG,
                  activeforeground=MENU_ACTIVE_FG,
                  relief="flat", bd=0, padx=14, pady=6,
                  font=_popup_tk_font(10, bold=True),
                  cursor="hand2").pack(pady=(16, 0), anchor="e")
        self.top.update_idletasks()
        pw = self.top.winfo_reqwidth()
        ph = self.top.winfo_reqheight()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        x = rx + (rw - pw) // 2
        y = ry + (rh - ph) // 2
        if x < 10:
            x = 10
        if y < 10:
            y = 10
        self.top.geometry(f"+{x}+{y}")
        self.top.focus_force()
        self.top.bind("<Escape>", lambda e: self.close())
        self.top.protocol("WM_DELETE_WINDOW", self.close)

    def _link(self, parent, text, url):
        lbl = tk.Label(parent, text=text, fg=LINK_FG, bg=POPUP_BG,
                       font=_popup_tk_font(10, bold=True),
                       cursor="hand2", anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    def close(self):
        if self.top is not None and self.top.winfo_exists():
            self.top.destroy()
        self.top = None


# =========================================================================
# МЕНЮ НАСТРОЕК
# =========================================================================
class SettingsMenu:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.menu = None

    def popup(self, event):
        if self.menu is not None:
            try:
                self.menu.destroy()
            except Exception:
                pass
        menu_kwargs = dict(tearoff=0,
                           bg=MENU_BG, fg=MENU_FG,
                           activebackground=MENU_ACTIVE_BG,
                           activeforeground=MENU_ACTIVE_FG,
                           bd=0, relief="flat",
                           font=_popup_tk_font(10))
        self.menu = tk.Menu(self.root, **menu_kwargs)
        m = self.menu

        if DISKS:
            disk_menu = tk.Menu(m, **menu_kwargs)
            for d in DISKS:
                var = tk.BooleanVar(value=(d["key"] in SHOWN_DISKS))
                label = d["label"]
                if d["is_system"]:
                    label += t("menu_system_suffix")
                disk_menu.add_checkbutton(
                    label=label, variable=var,
                    command=lambda k=d["key"], v=var: self._toggle_disk(k, v))
            m.add_cascade(label=t("menu_visible_disks"), menu=disk_menu)
            m.add_separator()

        m.add_command(label=t("menu_edit_custom"),
                      command=self.app.edit_custom_text)

        temp_menu = tk.Menu(m, **menu_kwargs)
        unit_var = tk.StringVar(value=state.temp_unit)
        temp_menu.add_radiobutton(label=t("menu_temp_c"), value="C",
                                  variable=unit_var,
                                  command=lambda: self._set_temp_unit("C"))
        temp_menu.add_radiobutton(label=t("menu_temp_f"), value="F",
                                  variable=unit_var,
                                  command=lambda: self._set_temp_unit("F"))
        m.add_cascade(label=t("menu_temp_units"), menu=temp_menu)

        theme_menu = tk.Menu(m, **menu_kwargs)
        theme_var = tk.StringVar(value=CONFIG.get("theme", "auto"))
        theme_menu.add_radiobutton(label=t("menu_theme_auto"), value="auto",
                                   variable=theme_var,
                                   command=lambda: self._set_theme("auto"))
        theme_menu.add_radiobutton(label=t("menu_theme_light"), value="light",
                                   variable=theme_var,
                                   command=lambda: self._set_theme("light"))
        theme_menu.add_radiobutton(label=t("menu_theme_dark"), value="dark",
                                   variable=theme_var,
                                   command=lambda: self._set_theme("dark"))
        m.add_cascade(label=t("menu_theme"), menu=theme_menu)

        tray_menu = tk.Menu(m, **menu_kwargs)
        mode_var = tk.StringVar(value=TRAY_MODE)
        tray_menu.add_radiobutton(label=t("menu_tray_single"),
                                  value="single", variable=mode_var,
                                  command=lambda: self._set_tray_mode("single"))
        tray_menu.add_radiobutton(label=t("menu_tray_dual"),
                                  value="dual", variable=mode_var,
                                  command=lambda: self._set_tray_mode("dual"))
        top_menu = tk.Menu(tray_menu, **menu_kwargs)
        for key in self._tray_metric_options():
            top_menu.add_radiobutton(
                label=self._metric_display_name(key),
                value=key,
                variable=tk.StringVar(value=TRAY_TOP_KEY),
                command=lambda k=key: self._set_tray_metric("top", k))
        tray_menu.add_cascade(label=t("menu_tray_top"), menu=top_menu)
        bot_menu = tk.Menu(tray_menu, **menu_kwargs)
        for key in self._tray_metric_options():
            bot_menu.add_radiobutton(
                label=self._metric_display_name(key),
                value=key,
                variable=tk.StringVar(value=TRAY_BOTTOM_KEY),
                command=lambda k=key: self._set_tray_metric("bottom", k))
        tray_menu.add_cascade(label=t("menu_tray_bottom"), menu=bot_menu)
        m.add_cascade(label=t("menu_tray_mode"), menu=tray_menu)

        lang_menu = tk.Menu(m, **menu_kwargs)
        lang_var = tk.StringVar(value=LANG)
        lang_menu.add_radiobutton(label=t("menu_lang_ru"), value="ru",
                                  variable=lang_var,
                                  command=lambda: self._set_language("ru"))
        lang_menu.add_radiobutton(label=t("menu_lang_en"), value="en",
                                  variable=lang_var,
                                  command=lambda: self._set_language("en"))
        m.add_cascade(label=t("menu_language"), menu=lang_menu)

        m.add_separator()

        m.add_command(label=t("menu_inc_font"),
                      command=lambda: self.app._wheel_delta(+1))
        m.add_command(label=t("menu_dec_font"),
                      command=lambda: self.app._wheel_delta(-1))
        m.add_command(label=t("menu_reset_font"),
                      command=self._reset_font_scale)

        m.add_separator()

        blink_var = tk.BooleanVar(value=BLINK_ON_CRITICAL)
        m.add_checkbutton(label=t("menu_blink"),
                          variable=blink_var,
                          command=lambda: self._toggle_blink(blink_var))

        if autostart_supported():
            auto_var = tk.BooleanVar(value=is_autostart_enabled())
            m.add_checkbutton(label=t("menu_autostart"),
                              variable=auto_var,
                              command=lambda: self._toggle_autostart(auto_var))

        m.add_separator()

        m.add_command(label=t("menu_reset_colors"),
                      command=self._reset_colors)
        m.add_command(label=t("menu_reset_all"),
                      command=self._reset_all)

        m.add_separator()

        m.add_command(label=t("menu_export"), command=self._export_config)
        m.add_command(label=t("menu_import"), command=self._import_config)

        m.add_separator()

        m.add_command(label=t("menu_about"), command=self.app.about_popup.show)

        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    def _tray_metric_options(self):
        return list(METRICS.keys()) + [CUSTOM_KEY]

    def _metric_display_name(self, key):
        if key == CUSTOM_KEY:
            return "CUSTOM"
        if key in METRICS:
            return METRICS[key].get("label", key)
        return key

    def _toggle_disk(self, key, var):
        on = bool(var.get())
        if on:
            if key not in SHOWN_DISKS:
                SHOWN_DISKS.append(key)
        else:
            if key in SHOWN_DISKS:
                SHOWN_DISKS.remove(key)
        CONFIG["show_disks"] = list(SHOWN_DISKS)
        save_config(CONFIG)
        rebuild_metrics()
        self.app.rebuild_all()

    def _set_temp_unit(self, unit):
        with state.lock:
            state.temp_unit = unit
        CONFIG["temp_unit"] = unit
        save_config(CONFIG)

    def _set_theme(self, theme):
        CONFIG["theme"] = theme
        save_config(CONFIG)
        self.app.apply_theme_and_restart(theme)

    def _set_language(self, lang):
        global LANG
        LANG = lang
        CONFIG["language"] = lang
        save_config(CONFIG)
        self.app.rebuild_all()

    def _set_tray_mode(self, mode):
        global TRAY_MODE
        TRAY_MODE = mode
        CONFIG["tray_mode"] = mode
        save_config(CONFIG)

    def _set_tray_metric(self, which, key):
        global TRAY_TOP_KEY, TRAY_BOTTOM_KEY
        if which == "top":
            TRAY_TOP_KEY = key
            CONFIG["tray_top"] = key
        else:
            TRAY_BOTTOM_KEY = key
            CONFIG["tray_bottom"] = key
        save_config(CONFIG)

    def _reset_font_scale(self):
        with state.lock:
            state.font_scale = 1.0
        CONFIG["font_scale"] = 1.0
        save_config(CONFIG)

    def _toggle_blink(self, var):
        global BLINK_ON_CRITICAL
        BLINK_ON_CRITICAL = bool(var.get())
        CONFIG["blink_on_critical"] = BLINK_ON_CRITICAL
        save_config(CONFIG)

    def _toggle_autostart(self, var):
        enable = bool(var.get())
        try:
            toggle_autostart(enable)
            CONFIG["autostart"] = enable
            save_config(CONFIG)
        except Exception as e:
            # откат галочки в UI
            var.set(is_autostart_enabled())
            messagebox.showerror(
                t("dlg_autostart_err_title"),
                t("dlg_autostart_err_msg", err=str(e)),
                parent=self.root)

    def _reset_colors(self):
        COLORS.clear()
        COLORS.update(DEFAULT_COLORS)
        CONFIG["colors"] = {}
        save_config(CONFIG)

    def _reset_all(self):
        if not messagebox.askyesno(
                t("dlg_reset_all_title"),
                t("dlg_reset_all_msg"),
                parent=self.root):
            return
        CONFIG.clear()
        save_config(CONFIG)
        messagebox.showinfo(t("dlg_reset_done_title"),
                            t("dlg_reset_done_msg"),
                            parent=self.root)

    def _export_config(self):
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title=t("dlg_export_title"),
            defaultextension=".json",
            initialfile=t("dlg_export_initialfile"),
            filetypes=[(t("dlg_export_ft"), "*.json"),
                       (t("dlg_all_files"), "*.*")])
        if not path:
            return
        try:
            export_cfg = dict(CONFIG)
            export_cfg["current"] = state.current
            export_cfg["custom_text"] = state.custom_text
            export_cfg["temp_unit"] = state.temp_unit
            export_cfg["font_scale"] = round(state.font_scale, 2)
            export_cfg["colors"] = dict(COLORS)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(export_cfg, f, ensure_ascii=False, indent=2)
            messagebox.showinfo(t("dlg_export_title"),
                                f"{t('dlg_export_saved')}\n{path}",
                                parent=self.root)
        except Exception as e:
            messagebox.showerror(t("dlg_error_title"),
                                 f"{t('dlg_error_title')}: {e}",
                                 parent=self.root)

    def _import_config(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title=t("dlg_import_title"),
            filetypes=[(t("dlg_export_ft"), "*.json"),
                       (t("dlg_all_files"), "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                imported = json.load(f)
            if not isinstance(imported, dict):
                raise ValueError("Config must be a JSON object")
            if not messagebox.askyesno(
                    t("dlg_import_title"),
                    t("dlg_import_confirm"),
                    parent=self.root):
                return
            save_config(imported)
            messagebox.showinfo(t("dlg_import_title"),
                                t("dlg_import_done"),
                                parent=self.root)
        except Exception as e:
            messagebox.showerror(t("dlg_error_title"),
                                 f"{t('dlg_error_title')}: {e}",
                                 parent=self.root)


# =========================================================================
# СПРАВКА
# =========================================================================
def help_lines():
    return [t(f"help_line_{i}") for i in range(1, 11)]


class HelpPopup:
    def __init__(self, root):
        self.root = root
        self.top = None

    def toggle(self):
        if self.top is not None and self.top.winfo_exists():
            self.close()
        else:
            self.show()

    def show(self):
        self.top = tk.Toplevel(self.root)
        self.top.overrideredirect(True)
        self.top.configure(bg=POPUP_BORDER)
        outer = tk.Frame(self.top, bg=POPUP_BORDER)
        outer.pack(fill="both", expand=True, padx=1, pady=1)
        inner = tk.Frame(outer, bg=POPUP_BG, padx=16, pady=14)
        inner.pack(fill="both", expand=True)
        header = tk.Frame(inner, bg=POPUP_BG)
        header.pack(fill="x")
        tk.Label(header, text=t("help_title"), fg=TEXT_PRIMARY, bg=POPUP_BG,
                 font=_popup_tk_font(12, bold=True),
                 anchor="w").pack(side="left")
        close_btn = tk.Label(header, text=" × ", fg=TEXT_MUTED, bg=POPUP_BG,
                             font=_popup_tk_font(13, bold=True),
                             cursor="hand2", padx=4)
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.close())
        tk.Frame(inner, bg=POPUP_BORDER, height=1).pack(fill="x", pady=(10, 12))
        for line in help_lines():
            row = tk.Frame(inner, bg=POPUP_BG)
            row.pack(fill="x", pady=1)
            tk.Label(row, text="·", fg=TEXT_MUTED, bg=POPUP_BG,
                     font=_popup_tk_font(10, bold=True), width=2,
                     anchor="nw").pack(side="left")
            tk.Label(row, text=line, fg=TEXT_SECONDARY, bg=POPUP_BG,
                     font=_popup_tk_font(10), anchor="w",
                     justify="left").pack(side="left", fill="x")
        self.top.bind("<Escape>", lambda e: self.close())
        self.top.bind("<FocusOut>", lambda e: self.close())
        self.top.update_idletasks()
        pw = self.top.winfo_reqwidth()
        ph = self.top.winfo_reqheight()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rh = self.root.winfo_height()
        sh = self.root.winfo_screenheight()
        x = rx + 10
        y_below = ry + rh + 8
        if y_below + ph + 10 <= sh:
            y = y_below
        else:
            y = ry - ph - 8
            if y < 10:
                y = 10
        sw = self.root.winfo_screenwidth()
        if x + pw > sw - 10:
            x = sw - pw - 10
        self.top.geometry(f"+{x}+{y}")
        self.top.focus_force()

    def close(self):
        if self.top is not None and self.top.winfo_exists():
            self.top.destroy()
        self.top = None


# =========================================================================
# ГЛАВНОЕ ОКНО
# =========================================================================
GRID_COLS = 3


class MainWindow:
    def __init__(self, root, on_tile_click):
        self.root = root
        self.on_tile_click = on_tile_click
        self.root.title(APP_NAME + " · v" + APP_VERSION)
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        try:
            icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
            img = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, img)
        except Exception:
            pass
        self.disk_popup = DiskPopup(root)
        self.help_popup = HelpPopup(root)
        self.about_popup = AboutPopup(root)
        self.settings_menu = SettingsMenu(self)
        self.tiles_frame = None
        self.footer = None
        self.buttons = {}
        self.keys = []
        self._build_tiles()
        self._build_footer()
        self._apply_window_geometry()
        self._save_pos_job = None
        self.root.bind("<Configure>", self._on_window_configure)

    def apply_theme_and_restart(self, new_theme_pref):
        global THEME
        global BG, POPUP_BG, POPUP_BORDER
        global TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_FAINT
        global FOOTER_BTN_BG, FOOTER_BTN_FG
        global MENU_BG, MENU_FG, MENU_ACTIVE_BG, MENU_ACTIVE_FG
        global BAR_BG, BAR_TEXT_ON_EMPTY, LINK_FG, DISABLED_FG

        if new_theme_pref == "auto":
            THEME = detect_system_theme()
        else:
            THEME = new_theme_pref
        c = THEME_COLORS[THEME]
        BG = c["BG"]
        POPUP_BG = c["POPUP_BG"]
        POPUP_BORDER = c["POPUP_BORDER"]
        TEXT_PRIMARY = c["TEXT_PRIMARY"]
        TEXT_SECONDARY = c["TEXT_SECONDARY"]
        TEXT_MUTED = c["TEXT_MUTED"]
        TEXT_FAINT = c["TEXT_FAINT"]
        FOOTER_BTN_BG = c["FOOTER_BTN_BG"]
        FOOTER_BTN_FG = c["FOOTER_BTN_FG"]
        MENU_BG = c["MENU_BG"]
        MENU_FG = c["MENU_FG"]
        MENU_ACTIVE_BG = c["MENU_ACTIVE_BG"]
        MENU_ACTIVE_FG = c["MENU_ACTIVE_FG"]
        BAR_BG = c["BAR_BG"]
        BAR_TEXT_ON_EMPTY = c["BAR_TEXT_ON_EMPTY"]
        LINK_FG = c["LINK_FG"]
        DISABLED_FG = c["DISABLED"]
        self.root.configure(bg=BG)
        try:
            self.disk_popup.close()
        except Exception:
            pass
        try:
            self.help_popup.close()
        except Exception:
            pass
        try:
            self.about_popup.close()
        except Exception:
            pass
        self._build_tiles()
        self._build_footer()
        self._apply_window_geometry()
        self.update_tiles()

    def _build_tiles(self):
        if self.tiles_frame is not None:
            self.tiles_frame.destroy()
        self.keys = list(METRICS.keys()) + [CUSTOM_KEY]
        self.buttons = {}
        self.tiles_frame = tk.Frame(self.root, bg=BG)
        self.tiles_frame.pack(pady=20, padx=20)
        for i, name in enumerate(self.keys):
            r, c = divmod(i, GRID_COLS)
            btn = tk.Label(self.tiles_frame, bd=0, highlightthickness=0,
                           cursor="hand2")
            btn.grid(row=r, column=c, padx=6, pady=6)
            btn.bind("<Button-1>", lambda e, k=name: self._on_left_click(k, e))
            btn.bind("<Button-3>", lambda e, k=name: self._on_right_click(k, e))
            btn.bind("<MouseWheel>", self.on_wheel)
            btn.bind("<Button-4>", lambda e: self._wheel_delta(+1))
            btn.bind("<Button-5>", lambda e: self._wheel_delta(-1))
            if name == CUSTOM_KEY:
                btn.bind("<Double-Button-1>", lambda e: self.edit_custom_text())
            if name == "TEMP":
                btn.bind("<Double-Button-1>", lambda e: self.toggle_temp_unit())
            self.buttons[name] = btn

    def _build_footer(self):
        if self.footer is not None:
            self.footer.destroy()
        self.footer = tk.Frame(self.root, bg=BG, height=36)
        self.footer.pack(side="bottom", fill="x", padx=20, pady=(0, 10))
        self.footer.pack_propagate(False)
        self.gear_btn = tk.Label(self.footer, text=" ⚙ ",
                                 fg=FOOTER_BTN_FG, bg=FOOTER_BTN_BG,
                                 font=_popup_tk_font(11, bold=True),
                                 cursor="hand2", padx=2)
        self.gear_btn.pack(side="left", padx=(0, 6))
        self.gear_btn.bind("<Button-1>", self._open_settings_from_gear)
        self.gear_btn.bind("<Button-3>", self._open_settings_from_gear)
        self.help_btn = tk.Label(self.footer, text=" ? ",
                                 fg=FOOTER_BTN_FG, bg=FOOTER_BTN_BG,
                                 font=_popup_tk_font(11, bold=True),
                                 cursor="hand2", padx=2)
        self.help_btn.pack(side="left")
        self.help_btn.bind("<Button-1>", lambda e: self.help_popup.toggle())
        self.ver_lbl = tk.Label(self.footer, text="v" + APP_VERSION,
                                fg=TEXT_MUTED, bg=BG,
                                font=_popup_tk_font(12))
        self.ver_lbl.pack(side="right")
        for w in (self.footer, self.gear_btn, self.help_btn, self.ver_lbl):
            w.bind("<Button-3>", self._open_settings_from_event)

    def _apply_window_geometry(self):
        self.root.update_idletasks()
        rows = (len(self.keys) + GRID_COLS - 1) // GRID_COLS
        w = 20 + GRID_COLS * (TILE_SIZE + 12) + 20
        h = (20 + rows * (TILE_SIZE + 12) + 20
             + self.footer.winfo_reqheight() + 10)
        if WIN_X is not None and WIN_Y is not None:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x, y = int(WIN_X), int(WIN_Y)
            if 0 <= x <= sw - 100 and 0 <= y <= sh - 100:
                self.root.geometry(f"{w}x{h}+{x}+{y}")
                return
        self.root.geometry(f"{w}x{h}")

    def rebuild_all(self):
        self._build_tiles()
        self._build_footer()
        self._apply_window_geometry()
        self.update_tiles()

    def _on_window_configure(self, event):
        if event.widget is not self.root:
            return
        if self._save_pos_job is not None:
            try:
                self.root.after_cancel(self._save_pos_job)
            except Exception:
                pass
        self._save_pos_job = self.root.after(500, self._save_window_pos)

    def _save_window_pos(self):
        self._save_pos_job = None
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            CONFIG["win_x"] = int(x)
            CONFIG["win_y"] = int(y)
            save_config(CONFIG)
        except Exception:
            pass

    def _open_settings_from_gear(self, event):
        self.settings_menu.popup(event)

    def _open_settings_from_event(self, event):
        self.settings_menu.popup(event)

    def _is_label_zone(self, event):
        return event.y >= TILE_SIZE * LABEL_CLICK_ZONE_RATIO

    def _on_left_click(self, key, event):
        if self._is_label_zone(event) and is_disk_key(key):
            self.disk_popup.show(key)
            return
        self.on_tile_click(key)

    def _on_right_click(self, key, event):
        if self._is_label_zone(event) and is_disk_key(key):
            self.disk_popup.show(key)
            return
        self.pick_color(key)

    def edit_custom_text(self):
        new = simpledialog.askstring(
            t("dlg_custom_title"),
            t("dlg_custom_prompt"),
            initialvalue=state.custom_text, parent=self.root)
        if new is None:
            return
        with state.lock:
            state.custom_text = new.strip()
        CONFIG["custom_text"] = state.custom_text
        save_config(CONFIG)

    def toggle_temp_unit(self):
        with state.lock:
            state.temp_unit = "F" if state.temp_unit == "C" else "C"
            unit = state.temp_unit
        CONFIG["temp_unit"] = unit
        save_config(CONFIG)

    def pick_color(self, key):
        cur = color_for(key)
        result = colorchooser.askcolor(color=cur, parent=self.root,
                                       title=f"{t('dlg_color_title')} {key}")
        if not result or not result[1]:
            return
        COLORS[key] = result[1]
        CONFIG.setdefault("colors", {})[key] = result[1]
        save_config(CONFIG)

    def on_wheel(self, event):
        delta = 1 if event.delta > 0 else -1
        self._wheel_delta(delta)

    def _wheel_delta(self, delta):
        with state.lock:
            state.font_scale = min(2.5, max(0.6,
                                            state.font_scale + 0.05 * delta))
            fs = state.font_scale
        CONFIG["font_scale"] = round(fs, 2)
        save_config(CONFIG)

    def update_tiles(self):
        with state.lock:
            cur = state.current
            custom = state.custom_text
            unit = state.temp_unit
            values = dict(state.values)
        for name, meta in METRICS.items():
            if name not in self.buttons:
                continue
            raw = values.get(name, 0)
            label = meta.get("label", name)
            color = color_for(name)
            if name == "TEMP":
                if raw is None:
                    val_txt = "—"
                    color = COLORS["__temp_na__"]
                else:
                    t_val = int(round(raw))
                    if unit == "F":
                        t_val = int(round(t_val * 9 / 5 + 32))
                    val_txt = str(t_val)
            else:
                val_txt = "--" if raw is None else str(int(round(raw)))
            img = render_tile_image(color, val_txt, label,
                                    False, False, (name == cur))
            self.buttons[name].configure(image=img)
            self.buttons[name].image = img
        if CUSTOM_KEY in self.buttons:
            val_c = custom if custom else "·"
            img_c = render_tile_image(color_for(CUSTOM_KEY), val_c, "CUSTOM",
                                      False, False, (cur == CUSTOM_KEY))
            self.buttons[CUSTOM_KEY].configure(image=img_c)
            self.buttons[CUSTOM_KEY].image = img_c


# =========================================================================
# ТОЧКА ВХОДА
# =========================================================================
def main():
    threading.Thread(target=stats_worker, daemon=True).start()
    tray_icon = build_tray()
    threading.Thread(target=lambda: tray_icon.run(), daemon=True).start()
    root = tk.Tk()

    def on_tile_click(key):
        with state.lock:
            state.current = key
        CONFIG["current"] = key
        save_config(CONFIG)

    win = MainWindow(root, on_tile_click)

    def periodic_update():
        win.update_tiles()
        root.after(1000, periodic_update)

    periodic_update()

    def check_queue():
        try:
            while True:
                msg = ui_queue.get_nowait()
                if msg == "open_window":
                    root.deiconify()
                    root.attributes("-topmost", True)
                    root.attributes("-topmost", False)
                elif msg == "quit":
                    try:
                        win._save_window_pos()
                    except Exception:
                        pass
                    root.destroy()
                    sys.exit(0)
        except queue.Empty:
            pass
        root.after(100, check_queue)

    root.after(100, check_queue)

    def on_close_window():
        try:
            win._save_window_pos()
        except Exception:
            pass
        root.withdraw()

    root.protocol("WM_DELETE_WINDOW", on_close_window)
    root.mainloop()


if __name__ == "__main__":
    main()