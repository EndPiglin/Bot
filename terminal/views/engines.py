from textual.app import ComposeResult
from textual.widgets import Static

from config.config_manager import ConfigManager


class EnginesView(Static):
    def __init__(
        self,
        cfg_mgr: ConfigManager,
        polling_engine,
        live_summary_engine,
        final_summary_engine,
        video_upload_engine,
        daily_summary_engine,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.cfg_mgr = cfg_mgr
        self.polling_engine = polling_engine
        self.live_summary_engine = live_summary_engine
        self.final_summary_engine = final_summary_engine
        self.video_upload_engine = video_upload_engine
        self.daily_summary_engine = daily_summary_engine

    def compose(self) -> ComposeResult:
        text = (
            "Engines\n\n"
            "PollingEngine:        running\n"
            "LiveSummaryEngine:    running\n"
            "FinalSummaryEngine:   running\n"
            "VideoUploadEngine:    running\n"
            "DailySaveEngine:      running\n"
            "DailySummaryEngine:   running\n"
            "\n(Replace with real status wiring later.)"
        )
        yield Static(text)
