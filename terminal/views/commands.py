from textual.app import ComposeResult
from textual.widgets import Static


class CommandsView(Static):
    def compose(self) -> ComposeResult:
        text = (
            "Terminal commands:\n\n"
            "  help                      - show this help\n"
            "  status                    - show basic status\n"
            "  uptime                    - show uptime\n"
            "  ping                      - quick responsiveness check\n"
            "  features                  - list feature flags\n"
            "  feature <name> on/off     - toggle feature\n"
            "  maintenance on/off        - toggle maintenance mode\n"
            "  settiktok <username>      - set TikTok username\n"
            "  interval offline N        - set offline interval (min)\n"
            "  interval live N           - set live summary interval (min)\n"
            "  interval video N          - set video interval (min)\n"
            "  interval retry N          - set TikTok retry interval (sec)\n"
            "  interval daily N          - set daily stats save interval (min)\n"
            "  dailytime HH:MM           - set daily summary time (GMT)\n"
            "  slash disable <cmd>       - hide a slash command\n"
            "  slash enable <cmd>        - show a slash command\n"
            "  slash list                - list disabled slash commands\n"
            "  save                      - save config\n"
            "  shutdown                  - shutdown whole bot\n"
            "  exit / quit / stop        - stop terminal loop only\n"
        )
        yield Static(text)
