# OS-RSM — Windows version

**Languages:** English | [Русский](README.ru.md)

Open Source Resource System Monitor — a system tray utility that shows real-time CPU, RAM, swap, disk usage, and temperature, right from your taskbar.

> Based on the original [OS-RSM](https://github.com/MihanPROJECTS/OS-RSM) project for Linux by [MihanPROJECTS](https://github.com/MihanPROJECTS). This is the Windows version with extended features.

![OS-RSM main window](assets/SCREENSHOT_1.png)

![OS-RSM tray popup](assets/SCREENSHOT_2.png)

![OS-RSM settings](assets/SCREENSHOT_3.png)

## Features

### Metrics
- **CPU** usage %
- **RAM** usage %
- **SWAP** usage %
- **DISK** usage % for any drive (C:, D:, E: — discovered automatically)
- **TEMP** (°C / °F, if sensor is available)
- **CUSTOM** — your own text on a tile

### Interface
- Flat UI color palette, easily customizable via right-click on any tile
- Large, high-contrast digits with auto-fit sizing
- Font scaling (mouse wheel over any tile)
- Light / dark / auto theme (follows system theme on Windows)
- Window position is remembered between launches
- Grid grows automatically when new disks are enabled

### Tray icon
- Single metric mode — shows the currently active metric
- **Dual metric mode** — shows two metrics at once, split horizontally
- Blinking on critical load (CPU/RAM/DISK/SWAP ≥ 95%, TEMP ≥ 90°C)
- Warning outline at ≥ 85%

### Disk details popup
- Left-click on a disk label → popup with volume label, used / free / total
- Colored progress bar (green → yellow → red)
- Auto-closes after 5 seconds of inactivity (configurable)
- Custom popup: click on `?` in the footer for full help

### Settings menu (right-click on footer)
- Visible disks (checkbox list)
- Edit CUSTOM text
- Temperature units (°C / °F)
- Theme (auto / light / dark)
- Tray mode (single / dual)
- Font size, color reset, config export/import
- Autostart with system
- Language: Русский / English

## Requirements

- **Windows 10 / 11** (also works on Linux and macOS with minor limitations)
- Python 3.9+ (if running from source)

## Installation

### From source

```bash
git clone https://github.com/alkidnn/osrsm-windows.git
cd osrsm-windows
pip install psutil pillow pystray
python src/osrsm.py
