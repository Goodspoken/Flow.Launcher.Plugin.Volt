import os
import sys
import ctypes
import ctypes.wintypes
import subprocess
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
    }
]

# --- Helper functions ---

def guid_from_string(guid_str: str) -> GUID:
    """Parse a GUID string like '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c' into a GUID struct.
    
    Pure Python — no ole32.dll dependency.
    """
    parts = guid_str.strip().lower().split("-")
    # parts: ['8c5e7fda', 'e8bf', '4a96', '9a85', 'a6e23a8c635c']
    g = GUID()
    g.Data1 = int(parts[0], 16)
    g.Data2 = int(parts[1], 16)
    g.Data3 = int(parts[2], 16)
    # Data4 is 8 bytes: first 2 from parts[3], last 6 from parts[4]
    d4_hex = parts[3] + parts[4]  # '9a85' + 'a6e23a8c635c' = 16 hex chars = 8 bytes
    for i in range(8):
        g.Data4[i] = int(d4_hex[i*2:i*2+2], 16)
    return g


def get_battery_info() -> str:
    """Retrieve Windows system power status string."""
    try:
        status = SystemPowerStatus()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            percent = status.BatteryLifePercent
            if status.ACLineStatus == 1:
                return f"[⚡ Сеть {percent}%]" if percent <= 100 else "[⚡ Сеть]"
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

        return results

    def set_power_plan(self, guid_str: str) -> None:
        """Switch power plan. Uses Win32 API first, falls back to non-blocking powercfg."""
        switched = False

        # Primary: Win32 API (instant, no subprocess)
        try:
            guid = guid_from_string(guid_str)
            res = ctypes.windll.powrprof.PowerSetActiveScheme(None, ctypes.byref(guid))
            if res == 0:
                switched = True
            else:
                _log_error(f"PowerSetActiveScheme returned error code: {res}")
        except Exception as e:
            _log_error(f"Win32 API exception: {e}")

        # Fallback: non-blocking powercfg (Popen, NOT run — avoids freeze)
        if not switched:
            try:
                subprocess.Popen(
                    ["powercfg", "/setactive", guid_str],
                    creationflags=0x08000000,  # CREATE_NO_WINDOW
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                _log_error(f"Powercfg fallback exception: {e}")


if __name__ == "__main__":
    PowerManager()
