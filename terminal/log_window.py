from collections import deque
from typing import Deque, List


class LogWindow:
    def __init__(self, max_lines: int = 500) -> None:
        self.lines: Deque[str] = deque(maxlen=max_lines)

    def add(self, line: str) -> None:
        self.lines.append(line)

    def get_recent_lines(self, n: int) -> List[str]:
        return list(self.lines)[-n:]
