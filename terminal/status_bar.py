from typing import Dict

from config.config_manager import ConfigManager
from utils.uptime import UptimeTracker


class StatusBar:
    def __init__(self, config_manager: ConfigManager, uptime: UptimeTracker):
        self.config_manager = config_manager
        self.uptime = uptime

    def get_status_line(self) -> str:
        cfg = self.config_manager.config
        username = cfg.get("tiktok_username", "") or "<not set>"
        features: Dict = cfg.get("features", {})
        enabled = [k for k, v in features.items() if v]
        uptime_str = self.uptime.get_uptime_str()
        maint = "ON" if cfg.get("maintenance_mode", False) else "OFF"
        return (
            f"[Uptime: {uptime_str}] "
            f"[TikTok: @{username}] "
            f"[Features: {', '.join(enabled) or 'none'}] "
            f"[Maintenance: {maint}]"
        )
