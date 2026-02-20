from textual.app import ComposeResult
from textual.widgets import Static

from config.config_manager import ConfigManager


class ConfigView(Static):
    def __init__(self, cfg_mgr: ConfigManager, **kwargs):
        super().__init__(**kwargs)
        self.cfg_mgr = cfg_mgr

    def compose(self) -> ComposeResult:
        cfg = self.cfg_mgr.config
        text = "Config (read-only view)\n\n" + str(cfg)
        yield Static(text)
