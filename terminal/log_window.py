from collections import deque
from typing import Deque

from terminal.decorations import format_info


class LogWindow:
    def __init__(self, max_lines: int = 50):
        self.lines: Deque[str] = deque(maxlen=max_lines)

    def add(self, msg: str):
        self.lines.append(format_info(msg))

    def render(self) -> str:
        return "\n".join(self.lines)
