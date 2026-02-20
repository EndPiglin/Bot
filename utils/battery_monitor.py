import os
from utils.logger import log


class BatteryMonitor:
    def __init__(self, threshold=15):
        self.threshold = threshold

    def get_battery_percent(self):
        try:
            with open("/sys/class/power_supply/battery/capacity") as f:
                return int(f.read().strip())
        except:
            return None

    def check(self):
        pct = self.get_battery_percent()
        if pct is None:
            return
        if pct <= self.threshold:
            log.warning(f"Battery low: {pct}%")
