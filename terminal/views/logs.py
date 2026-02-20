from textual.app import ComposeResult
from textual.widgets import Static

from terminal.log_window import LogWindow


class LogsView(Static):
    def __init__(self, log_window: LogWindow, **kwargs):
        super().__init__(**kwargs)
        self.log_window = log_window

    def compose(self) -> ComposeResult:
        text = "Logs (latest):\n\n" + "\n".join(self.log_window.get_recent_lines(50))
        yield Static(text)
