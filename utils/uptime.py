import time

class UptimeTracker:
    def __init__(self):
        self.start_time = None

    def mark_start(self):
        self.start_time = time.time()

    def get_uptime_seconds(self) -> int:
        if self.start_time is None:
            return 0
        return int(time.time() - self.start_time)

    def get_uptime_str(self) -> str:
        secs = self.get_uptime_seconds()
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h}h {m}m {s}s"
