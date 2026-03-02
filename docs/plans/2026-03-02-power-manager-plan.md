# Power Manager Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Create a Windows 11 Power Manager plugin for Flow Launcher allowing users to switch between High Performance, Balanced, and Power Saver plans.

**Architecture:** A Python class inheriting from `FlowLauncher`. Returns 3 static JSON objects representing the power plans via `query()` and executes `powercfg /setactive <GUID>` via `set_power_plan(guid)` when clicked.

**Tech Stack:** Python 3, `flowlauncher`, `subprocess`, `pytest`.

---

### Task 1: Project Configuration

**Files:**
- Create: `requirements.txt`
- Create: `plugin.json`
- Create: `tests/__init__.py`

**Step 1: Write requirements.txt**
Create a file defining project dependencies. We need `flowlauncher` (core API) and `pytest` for TDD.

**Step 2: Write plugin.json**
Create the metadata file Flow Launcher requires to load the extension. Configure `ActionKeyword` to "power" and `ExecuteFileName` to `main.py`.

**Step 3: Commit**
```bash
# git is required to be initialized first if not present
git init
git add requirements.txt plugin.json tests/__init__.py
git commit -m "chore: setup plugin metadata and dependencies"
```

### Task 2: Core Logic with TDD (main.py)

**Files:**
- Create: `tests/test_main.py`
- Create: `main.py`

**Step 1: Write the failing test**

```python
import sys
import os
from unittest.mock import patch

# Mock sys.argv used inside FlowLauncher init
sys.argv = ['main.py', '{"method": "query", "parameters": [""]}']

def test_query_returns_three_plans():
    from main import PowerManager
    pm = PowerManager()
    
    # query method takes an argument as the user input text
    results = pm.query("")
    
    assert len(results) == 3
    assert results[0]["Title"] == "Максимальная производительность"
    assert results[1]["Title"] == "Сбалансированный"
    assert results[2]["Title"] == "Максимальное энергосбережение"
    assert results[0]["JsonRPCAction"]["parameters"][0] == "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

@patch('subprocess.run')
def test_set_power_plan_executes_powercfg(mock_run):
    from main import PowerManager
    pm = PowerManager()
    
    guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    pm.set_power_plan(guid)
    
    mock_run.assert_called_once_with(["powercfg", "/setactive", guid], check=False)
```

**Step 2: Run test to verify it fails**

Run: `pip install -r requirements.txt && pytest tests/test_main.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'main'"

**Step 3: Write minimal implementation**

```python
import sys
import subprocess
from flowlauncher import FlowLauncher

class PowerManager(FlowLauncher):
    def query(self, query):
        return [
            {
                "Title": "Максимальная производительность",
                "SubTitle": "Переключить на Максимальную производительность",
                "IcoPath": "Images/high.png",
                "JsonRPCAction": {
                    "method": "set_power_plan",
                    "parameters": ["8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
                    "dontHideAfterAction": False
                }
            },
            {
                "Title": "Сбалансированный",
                "SubTitle": "Переключить на Сбалансированный режим",
                "IcoPath": "Images/balanced.png",
                "JsonRPCAction": {
                    "method": "set_power_plan",
                    "parameters": ["381b4222-f694-41f0-9685-ff5bb260df2e"],
                    "dontHideAfterAction": False
                }
            },
            {
                "Title": "Максимальное энергосбережение",
                "SubTitle": "Переключить на режим Максимального энергосбережения",
                "IcoPath": "Images/saver.png",
                "JsonRPCAction": {
                    "method": "set_power_plan",
                    "parameters": ["a1841308-3541-4fab-bc81-f71556f20b4a"],
                    "dontHideAfterAction": False
                }
            }
        ]

    def set_power_plan(self, guid):
        subprocess.run(["powercfg", "/setactive", guid], check=False)

if __name__ == "__main__":
    PowerManager()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_main.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_main.py main.py
git commit -m "feat: implement logic for displaying and setting power plans"
```

### Task 3: Visual Assets

**Files:**
- Create: `scripts/gen_icons.py`
- Modify: `Images/` dir (indirectly)

**Step 1: Write script to generate PNGs**

```python
import os
from PIL import Image

def create_color_icon(filename, color):
    # 100x100 solid color icon
    img = Image.new('RGB', (100, 100), color=color)
    img.save(filename)

if __name__ == "__main__":
    os.makedirs('Images', exist_ok=True)
    create_color_icon('Images/app.png', 'grey')
    create_color_icon('Images/high.png', '#e74c3c')       # Red
    create_color_icon('Images/balanced.png', '#3498db')   # Blue
    create_color_icon('Images/saver.png', '#2ecc71')      # Green
```

**Step 2: Generate Icons**
Run: `pip install Pillow && python scripts/gen_icons.py`

**Step 3: Commit**
```bash
git add scripts/gen_icons.py Images/
git commit -m "chore: add default colored status icons"
```
