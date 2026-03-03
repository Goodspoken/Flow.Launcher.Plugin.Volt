# Volt ⚡

**Volt** is a lightweight plugin for [Flow Launcher](https://www.flowlauncher.com/) that allows you to instantly switch between Windows 11 power plans.

![Volt Icon](Images/app.png)

## Features

- 🚀 **Fast:** Switch power plans with a single command without opening the Control Panel.
- ⚡ **3 Modes:** Support for standard Windows power schemes (High Performance, Balanced, Power Saver).
- 🎨 **Visual UI:** Colored status icons for each power mode.

## Usage

1. Open Flow Launcher (usually `Alt + Space`).
2. Type the keyword `volt`.
3. Select your desired power plan and press `Enter`.

## Installation

### Via Plugin Store (Coming Soon)
Search for `Volt` in Flow Launcher or type:
`pm install Volt`

### Manual Installation
1. Download the latest release from the [Releases](https://github.com/Goodspoken/Flow.Launcher.Plugin.Volt/releases) section.
2. Extract the archive into your Flow Launcher plugins folder:
   `%APPDATA%\FlowLauncher\Plugins\Volt`
3. Restart Flow Launcher.

## Requirements

- Windows 10/11
- Python 3.x (bundled with Flow Launcher)

## Known Issues

- **Cached results:** When opening Flow Launcher via history (re-opening a previous `volt` query), the active plan status may not refresh. Typing `volt` fresh always shows the correct status. This is a Flow Launcher caching limitation.

## Development

The plugin is written in Python and uses the Win32 API (`powrprof.dll`) for instant power plan switching — no `subprocess` calls in the main path.
All dependencies are bundled in the `lib` folder for out-of-the-box functionality.

---
*Created with ⚡ by Antigravity*
