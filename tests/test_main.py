import sys
import unittest
from unittest.mock import patch

sys.argv = ['main.py', '{"method": "query", "parameters": [""]}']

def test_query_returns_three_plans():
    from main import PowerManager
    pm = PowerManager()
    
    results = pm.query("")
    
    assert len(results) >= 3
    # Check if we have standard plans at least
    titles = [r["Title"] for r in results]
    assert any("Balanced" in t for t in titles)

@patch('subprocess.run')
def test_set_power_plan_executes_powercfg(mock_run):
    from main import PowerManager
    import sys
    pm = PowerManager()
    
    guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    pm.set_power_plan(guid)
    
    create_no_window = 0x08000000 if sys.platform == "win32" else 0
    mock_run.assert_called_once_with(["powercfg", "/setactive", guid], check=False, creationflags=create_no_window)
