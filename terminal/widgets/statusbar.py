from textual.app import ComposeResult
from textual.widgets import Static


class StatusBar(Static):
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def compose(self) -> ComposeResult:
        yield Static(self.text or "Bot TUI")
