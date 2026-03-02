# Power Manager Design

## Architecture

This is a Python-based plugin for Flow Launcher on Windows 11. 
The plugin will inherit from the standard `FlowLauncher` base class. When a user types the plugin's action keyword (e.g. `power`), the plugin returns JSON representing the three power plans. When the user selects a plan, a JsonRPCAction callback executes `powercfg /setactive <GUID>` to switch the active power plan in Windows.

## Components

1. **`plugin.json`**: Standard Flow Launcher configuration registering the plugin name, keyword, execute file, and icon.
2. **`main.py`**: A `FlowLauncher` derived class.
    - `query(self, query)`: Returns the static 3 items (High Performance, Balanced, Power Saver) and specifies `set_power_plan` as the action.
    - `set_power_plan(self, guid)`: Wrapper calling Windows `powercfg` utility using standard library `subprocess`.
3. **Icons**: Basic `.png` assets representing the three different states.

## Data Flow

1. User invokes `power`. 
2. Plugin responds with 3 static items. 
3. User picks an item. 
4. Flow Launcher calls `set_power_plan(GUID)`. 
5. Subprocess calls `powercfg /setactive GUID`.

## Testing 

We will use Test-Driven Development (TDD) as defined in the workflows. Since `powercfg` is a Windows-specific command and we develop in a Linux container, the tests will heavily rely on Python's `unittest.mock` to assert that `subprocess.run` is called correctly without actually executing the Windows command.
