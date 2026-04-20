# Volt Plugin: Project Passport (v1.2.9)

## Architecture Overview
The Volt plugin is a Python-based Flow Launcher plugin designed to control Windows 11 Power Plans. 

### Key Technical Decisions
1. **Instant Queries (Winreg):**
   - Instead of calling `powercfg /getactivescheme` (which takes ~200ms), we read the active GUID directly from the Windows Registry: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes\ActivePowerScheme`.
   - Result: 0ms lag during typing in Flow Launcher.

2. **Curated Power Plans (Stability & UI):**
   - Instead of dynamic enumeration (which often returns obscure or duplicate plans), we use a curated list of the 3 standard Windows plans.
   - Result: Guaranteed high-quality icons, reliable Russian naming, and a clean UI without clutter.

3. **Silent Execution (ShellExecuteW):**
   - Switched from `subprocess` to `ctypes.windll.shell32.ShellExecuteW` for plan switching.
   - Command: `powercfg /setactive {guid}`
   - Flags: `SW_HIDE (0)` ensures no console window ever flashes.

4. **Power Status (SYSTEM_POWER_STATUS):**
   - Uses `ctypes` to call `GetSystemPowerStatus`. 
   - Uses `ctypes.c_ubyte` for percentage to avoid the signed-byte bug where 100% shows as -1%.

5. **UI Logic:**
   - Active plan is marked with `_active.png` icons (generated via Pillow).
   - Active plan gets `Score: 100` to be forced to the top of results.
   - Subtitles show connection type: `[⚡ Сеть]` or `[🔋 Батарея %]`.

## Version History (Recent)
- **v1.1.7:** Full refactoring (Single Responsibility Principle), added strict typing, and passed Ruff/Mypy checks.
- **v1.1.8:** Optimized performance with `winreg` and generated missing active icons.
- **v1.1.9:** Simplified UI (removed estimations), changed switching logic to `ShellExecuteW` for 100% invisibility and reliability.
- **v1.2.0:** Dynamic power plan discovery via Registry (removed hardcoded GUIDs).
- **v1.2.1:** Fixed search string strip, Score filtering behavior, and powercfg absolute path.
- **v1.2.2:** Added reliable active scheme detection via Win32 API (PowerGetActiveScheme).
- **v1.2.3:** Debug build: Added detected GUID to SubTitle; refined Score and sorting logic.
- **v1.2.4:** Switched to direct API switching (PowerSetActiveScheme) and added WM_SETTINGCHANGE broadcast for instant UI reactivity. Corrected memory handling (LocalFree).
- **v1.2.5:** Reverted plan switching to powercfg.exe for 100% reliability and robust system notifications. Kept Win32 API for instant status reading. Fixed score priority issues when searching.
- **v1.2.6:** Fixed NameError in icon mapping logic (any() call with undefined variable 'w').
- **v1.2.7:** Major code audit & cleanup. Removed unnecessary dependencies (`re`, `winreg`, `json`). Switched to pure Python `guid_from_string`. Fixed critical `self.change_query()` crash. Replaced `self.debug()` with persistent file logging (`volt_debug.log`).
- **v1.2.8:** Store Integration Milestone. Verified and fixed Plugin ID and structure. Successfully merged into Flow Launcher Store.
- **v1.2.9:** Code optimization. Simplified GUID handling via `uuid`, improved battery status (charging detection), and added a shortcut to Windows Power Settings. Added `WM_SETTINGCHANGE` broadcast for instant system-wide UI updates.

## Deployment Instructions (Windows)
1. Copy the project folder to `%APPDATA%\FlowLauncher\Plugins\Volt`.
2. Ensure `Images/` contains both base and `_active.png` icons.
3. Reload Flow Launcher (`pm reload`).

## Debugging
- If a mode doesn't switch, check `Flow Launcher -> Settings -> Logs`.
- Ensure the user has permissions to read the `PowerSchemes` registry key (standard on Win11).
