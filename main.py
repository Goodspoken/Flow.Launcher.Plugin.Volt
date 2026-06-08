import os
import sys
import ctypes
import ctypes.wintypes
import subprocess
import uuid
from typing import Any, Dict, List, Optional

# Flow Launcher requires plugins to append to path before importing flowlauncher library
plugindir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(plugindir)
sys.path.append(os.path.join(plugindir, "lib"))

from flowlauncher import FlowLauncher  # noqa: E402

# --- Win32 API Structures ---

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __str__(self):
        return "%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x" % (
            self.Data1, self.Data2, self.Data3,
            self.Data4[0], self.Data4[1], self.Data4[2], self.Data4[3],
            self.Data4[4], self.Data4[5], self.Data4[6], self.Data4[7]
        )

class SystemPowerStatus(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_ubyte),
        ("BatteryFlag", ctypes.c_ubyte),
        ("BatteryLifePercent", ctypes.c_ubyte),
        ("SystemStatusFlag", ctypes.c_ubyte),
        ("BatteryLifeTime", ctypes.wintypes.DWORD),
        ("BatteryFullLifeTime", ctypes.wintypes.DWORD),
    ]

# Standard Windows Power Scheme GUIDs (Universal across all Windows 10/11)
POWER_PLANS = [
    {
        "Name": "High Performance",
        "RussianName": "Высокая производительность",
        "Guid": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "Icon": "Images/high.png"
    },
    {
        "Name": "Balanced",
        "RussianName": "Сбалансированный",
        "Guid": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "Icon": "Images/balanced.png"
    },
    {
        "Name": "Power Saver",
        "RussianName": "Экономия энергии",
        "Guid": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "Icon": "Images/saver.png"
    },
    {
        "Name": "Ultimate Performance",
        "RussianName": "Максимальная производительность",
        "Guid": "e9a42b02-d5df-448d-aa00-03f14749eb61",
        "Icon": "Images/high.png",
        "Optional": True
    }
]

# --- Helper functions ---

def guid_from_string(guid_str: str) -> GUID:
    """Parse a GUID string into a Win32 GUID struct using the uuid module."""
    u = uuid.UUID(guid_str)
    g = GUID()
    g.Data1, g.Data2, g.Data3 = u.fields[0], u.fields[1], u.fields[2]
    for i in range(8):
        g.Data4[i] = u.bytes[8 + i]
    return g


def get_battery_info() -> str:
    """Retrieve Windows system power status string with charging detection."""
    try:
        status = SystemPowerStatus()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            percent = status.BatteryLifePercent
            is_charging = bool(status.BatteryFlag & 8)
            
            if status.ACLineStatus == 1:
                prefix = "⚡ Сеть"
                if is_charging:
                    prefix = "⚡ Зарядка"
                elif percent >= 100:
                    prefix = "⚡ Полный заряд"
                return f"[{prefix} {percent}%]" if percent <= 100 else f"[{prefix}]"
            elif status.ACLineStatus == 0:
                return f"[🔋 Батарея {percent}%]" if percent <= 100 else "[🔋 Батарея]"
    except Exception:
        pass
    return "[🔌 ПК]"


def get_active_power_scheme_guid() -> Optional[str]:
    """Direct Win32 API call to get the active power scheme (instant, 0ms lag)."""
    if sys.platform != "win32":
        return None
    try:
        p_guid = ctypes.POINTER(GUID)()
        res = ctypes.windll.powrprof.PowerGetActiveScheme(None, ctypes.byref(p_guid))
        if res == 0 and p_guid:
            guid_str = str(p_guid.contents).lower()
            ctypes.windll.kernel32.LocalFree(p_guid)
            return guid_str
    except Exception:
        return None


def is_power_scheme_installed(guid_str: str) -> bool:
    """Check if a power scheme GUID is installed on the system using PowerEnumerate."""
    if sys.platform != "win32":
        return False
    try:
        scheme_guid = GUID()
        size = ctypes.c_ulong(ctypes.sizeof(GUID))
        index = 0
        target = guid_str.lower()
        while True:
            res = ctypes.windll.powrprof.PowerEnumerate(
                None,
                None,
                None,
                16,  # ACCESS_SCHEME
                index,
                ctypes.byref(scheme_guid),
                ctypes.byref(size)
            )
            if res != 0:
                break
            if str(scheme_guid).lower() == target:
                return True
            index += 1
            size = ctypes.c_ulong(ctypes.sizeof(GUID))
    except Exception:
        pass
    return False


def _log_error(msg: str) -> None:
    """Write error to a log file next to the plugin for diagnostics."""
    try:
        log_path = os.path.join(plugindir, "volt_debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


# --- Plugin ---

class PowerManager(FlowLauncher):
    def query(self, query: str) -> List[Dict[str, Any]]:
        battery_text = get_battery_info()
        active_guid = get_active_power_scheme_guid()

        results = []
        q = query.strip().lower()

        for plan in POWER_PLANS:
            name = plan["RussianName"]
            eng_name = plan["Name"]
            guid = plan["Guid"].lower()

            # Optional plans are only shown if they are currently active or installed
            if plan.get("Optional"):
                if active_guid != guid and not is_power_scheme_installed(guid):
                    continue

            # Simple filtering: match Russian or English name
            if q and q not in name.lower() and q not in eng_name.lower():
                continue

            is_active = (active_guid == guid)

            # Icon handling
            icon = plan["Icon"]
            if is_active:
                icon = icon.replace(".png", "_active.png")
                status = "Активен"
                score = 100
            else:
                status = "Выбрать"
                score = 50

            results.append({
                "Title": name,
                "SubTitle": f"{battery_text} | {status}",
                "IcoPath": icon,
                "Score": score,
                "JsonRPCAction": {
                    "method": "set_power_plan",
                    "parameters": [guid],
                    "dontHideAfterAction": False,
                },
            })

        # 4. Add "Open Power Settings" shortcut (fixed 4th position)
        results.append({
            "Title": "Настройки электропитания",
            "SubTitle": "Открыть системные настройки Windows",
            "IcoPath": "Images/app.png",
            "Score": 0,
            "JsonRPCAction": {
                "method": "open_settings",
                "parameters": [],
                "dontHideAfterAction": False,
            },
        })

        return results

    def set_power_plan(self, guid_str: str) -> None:
        """Switch power plan and broadcast changes to the system."""
        switched = False

        # Primary: Win32 API (instant)
        try:
            guid = guid_from_string(guid_str)
            res = ctypes.windll.powrprof.PowerSetActiveScheme(None, ctypes.byref(guid))
            if res == 0:
                switched = True
                # Broadcast setting change so system UI (taskbar) updates immediately
                ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 100, None)
            else:
                _log_error(f"PowerSetActiveScheme error: {res}")
        except Exception as e:
            _log_error(f"Win32 API exception: {e}")

        # Fallback: powercfg
        if not switched:
            try:
                subprocess.Popen(
                    ["powercfg", "/setactive", guid_str],
                    creationflags=0x08000000,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                _log_error(f"Powercfg fallback exception: {e}")

    def open_settings(self) -> None:
        """Open Windows Power & Sleep settings."""
        try:
            os.startfile("ms-settings:powersleep")
        except Exception as e:
            _log_error(f"Failed to open settings: {e}")


if __name__ == "__main__":
    PowerManager()
