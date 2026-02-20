import psutil
import time


class SystemMonitor:
    def __init__(self):
        self.cpu = 0.0
        self.ram_used = 0
        self.ram_total = 0
        self.ram_percent = 0.0
        self.last_update = 0

    def update(self):
        now = time.time()
        if now - self.last_update < 1:
            return  # update at most once per second

        self.last_update = now

        self.cpu = psutil.cpu_percent(interval=None)

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
