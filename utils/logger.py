import datetime


class Logger:
    def __init__(self, log_window=None):
        self.log_window = log_window

    def _write(self, level: str, msg: str):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {msg}"
        print(line)

        if self.log_window:
            self.log_window.add(line)

    def info(self, msg: str):
        self._write("INFO", msg)

    def warning(self, msg: str):
        self._write("WARN", msg)

    def error(self, msg: str):
        self._write("ERROR", msg)


# Global logger instance
log = Logger()
