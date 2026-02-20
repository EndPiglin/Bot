import psutil
import time
import os
from utils.battery_monitor import BatteryMonitor


class SystemMonitor:
    def __init__(self):
        self.cpu = 0.0
        self.ram_used = 0
        self.ram_total = 0
        self.ram_percent = 0.0
        self.last_update = 0

        # NEW: battery monitor
        self.battery_monitor = BatteryMonitor()

    def _safe_cpu_percent(self):
        """
        Android/Termux cannot read /proc/stat.
        So we fall back to load average approximation.
        """
        try:
            load1, load5, load15 = os.getloadavg()
            cores = psutil.cpu_count(logical=True) or 1
            cpu_percent = min(100.0, (load1 / cores) * 100)
            return cpu_percent
        except Exception:
            return 0.0

    def update(self):
        now = time.time()
        if now - self.last_update < 1:
            return

        self.last_update = now

        # CPU (safe fallback)
        self.cpu = self._safe_cpu_percent()

        # RAM (psutil works fine on Android)
        mem = psutil.virtual_memory()
        self.ram_used = mem.used // (1024 * 1024)
        self.ram_total = mem.total // (1024 * 1024)
        self.ram_percent = mem.percent

    def get_stats(self):
        return {
            "cpu": self.cpu,
            "ram_used": self.ram_used,
            "ram_total": self.ram_total,
            "ram_percent": self.ram_percent,
        }
