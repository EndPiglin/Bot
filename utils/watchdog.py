import time
from utils.logger import log


class Watchdog:
    def __init__(self, timeout_seconds=300):
        self.timeout = timeout_seconds
        self.last_heartbeat = time.time()

    def heartbeat(self):
        self.last_heartbeat = time.time()

    def check(self):
        if time.time() - self.last_heartbeat > self.timeout:
            log.warning("Watchdog timeout — engine may be frozen.")
            return False
        return True
