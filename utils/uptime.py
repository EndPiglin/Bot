import time


class Uptime:
    def __init__(self):
        self.start_time = time.time()

    def get_uptime_seconds(self) -> int:
        return int(time.time() - self.start_time)

    def get_uptime_str(self) -> str:
        sec = self.get_uptime_seconds()
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h}h {m}m {s}s"
