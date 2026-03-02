import sys
import unittest
from unittest.mock import patch

sys.argv = ['main.py', '{"method": "query", "parameters": [""]}']

def test_query_returns_three_plans():
    from main import PowerManager
    pm = PowerManager()
    
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
