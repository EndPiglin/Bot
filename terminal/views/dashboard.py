from textual.app import ComposeResult
from textual.widgets import Static

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags


class DashboardView(Static):
    def __init__(self, cfg_mgr: ConfigManager, feature_flags: FeatureFlags, **kwargs):
        super().__init__(**kwargs)
        self.cfg_mgr = cfg_mgr
        self.feature_flags = feature_flags

    def compose(self) -> ComposeResult:
        cfg = self.cfg_mgr.config
        ttu = cfg.get("tiktok_username", "") or "<not set>"
        maint = cfg.get("maintenance_mode", False)
        intervals = cfg.get("intervals", {})
        text = (
            f"Dashboard\n\n"
            f"TikTok: @{ttu}\n"
            f"Maintenance: {maint}\n\n"
            f"Intervals:\n"
            f"  offline:      {intervals.get('offline')}\n"
            f"  live_summary: {intervals.get('live_summary')}\n"
            f"  video:        {intervals.get('video')}\n"
            f"  retry:        {intervals.get('retry')}\n"
            f"  daily:        {intervals.get('daily')}\n\n"
            f"Daily summary time (GMT): {cfg.get('daily_summary', {}).get('time_gmt', '23:00')}\n"
        )
        yield Static(text)
