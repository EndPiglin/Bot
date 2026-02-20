from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from config.paths import Paths
from terminal.views.dashboard import DashboardView
from terminal.views.logs import LogsView
from terminal.views.engines import EnginesView
from terminal.views.config import ConfigView
from terminal.views.commands import CommandsView


class Sidebar(Static):
    def __init__(self, on_select, **kwargs):
        super().__init__(**kwargs)
        self.on_select = on_select

    def compose(self) -> ComposeResult:
        items = [
            ("Dashboard", "dashboard"),
            ("Logs", "logs"),
            ("Engines", "engines"),
            ("Config", "config"),
            ("Commands", "commands"),
        ]
        lv = ListView(
            *[ListItem(Label(label), id=key) for label, key in items],
            id="sidebar-list",
        )
        yield lv

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if self.on_select:
            self.on_select(event.item.id)


class MainApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #body {
        height: 1fr;
    }
    #sidebar {
        width: 24;
        border: solid #444444;
    }
    #content {
        border: solid #444444;
    }
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        feature_flags: FeatureFlags,
        polling_engine,
        live_summary_engine,
        final_summary_engine,
        video_upload_engine,
        daily_summary_engine,
        log_window,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.cfg_mgr = config_manager
        self.feature_flags = feature_flags
        self.polling_engine = polling_engine
        self.live_summary_engine = live_summary_engine
        self.final_summary_engine = final_summary_engine
        self.video_upload_engine = video_upload_engine
        self.daily_summary_engine = daily_summary_engine
        self.log_window = log_window

        self.current_view = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            yield Sidebar(self.switch_view, id="sidebar")
            with Vertical(id="content"):
                yield DashboardView(self.cfg_mgr, self.feature_flags)
        yield Footer()

    def on_mount(self) -> None:
        self.current_view = "dashboard"

    def switch_view(self, view_id: str) -> None:
        self.current_view = view_id
        content = self.query_one("#content", Vertical)
        content.remove_children()

        if view_id == "dashboard":
            content.mount(DashboardView(self.cfg_mgr, self.feature_flags))
        elif view_id == "logs":
            content.mount(LogsView(self.log_window))
        elif view_id == "engines":
            content.mount(
                EnginesView(
                    self.cfg_mgr,
                    self.polling_engine,
                    self.live_summary_engine,
                    self.final_summary_engine,
                    self.video_upload_engine,
                    self.daily_summary_engine,
                )
            )
        elif view_id == "config":
            content.mount(ConfigView(self.cfg_mgr))
        elif view_id == "commands":
            content.mount(CommandsView(self.cfg_mgr))
        else:
            content.mount(Static(f"Unknown view: {view_id}"))
