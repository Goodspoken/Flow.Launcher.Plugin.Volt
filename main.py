import sys
import subprocess

try:
    from flowlauncher import FlowLauncher
except ImportError:
    class FlowLauncher:
        def __init__(self):
            pass

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
