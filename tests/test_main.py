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
    assert any("Сбалансированный" in t for t in titles)

@patch('subprocess.Popen')
def test_set_power_plan_executes_powercfg(mock_popen):
    from main import PowerManager
    import subprocess
    pm = PowerManager()
    
    guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    pm.set_power_plan(guid)
    
    mock_popen.assert_called_once_with(
        ["powercfg", "/setactive", guid],
        creationflags=0x08000000,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

@patch('main.is_power_scheme_installed')
@patch('main.get_active_power_scheme_guid')
def test_ultimate_performance_optional_handling(mock_active, mock_installed):
    from main import PowerManager
    pm = PowerManager()
    
    # Scenario 1: Ultimate Performance is not active and not installed
    mock_active.return_value = "381b4222-f694-41f0-9685-ff5bb260df2e" # Balanced
    mock_installed.return_value = False
    results = pm.query("")
    titles = [r["Title"] for r in results]
    assert "Максимальная производительность" not in titles
    
    # Scenario 2: Ultimate Performance is active
    mock_active.return_value = "e9a42b02-d5df-448d-aa00-03f14749eb61" # Ultimate
    mock_installed.return_value = False
    results = pm.query("")
    titles = [r["Title"] for r in results]
    assert "Максимальная производительность" in titles

    # Scenario 3: Ultimate Performance is not active, but is installed
    mock_active.return_value = "381b4222-f694-41f0-9685-ff5bb260df2e" # Balanced
    mock_installed.return_value = True
    results = pm.query("")
    titles = [r["Title"] for r in results]
    assert "Максимальная производительность" in titles


