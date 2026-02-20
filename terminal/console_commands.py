from config.config_manager import ConfigManager
from config.defaults import (
    MIN_OFFLINE_INTERVAL,
    MIN_LIVE_SUMMARY_INTERVAL,
    MIN_VIDEO_INTERVAL,
)
from utils.logger import log


class ConsoleCommands:
    def __init__(
        self,
        config_manager: ConfigManager,
        feature_flags,
        polling_engine,
        live_summary_engine,
        final_summary_engine,
        video_upload_engine,
        daily_summary_engine,
        uptime,
        log_window,
        app=None,
    ):
        self.cfg_mgr = config_manager
        self.feature_flags = feature_flags
        self.polling_engine = polling_engine
        self.live_summary_engine = live_summary_engine
        self.final_summary_engine = final_summary_engine
        self.video_upload_engine = video_upload_engine
        self.daily_summary_engine = daily_summary_engine
        self.uptime = uptime
        self.log_window = log_window
        self.app = app

    def _set_interval(self, key: str, value: int, minimum: int | None = None) -> str:
        if minimum is not None and value < minimum:
            self.log_window.add(
                f"Warning: {key} below recommended minimum ({minimum})."
            )
        self.cfg_mgr.config.setdefault("intervals", {})[key] = value
        return f"Interval '{key}' set to {value} (not saved yet)."

    def handle(self, cmd: str) -> str:
        if not cmd:
            return ""

        parts = cmd.split()
        name = parts[0].lower()
        args = parts[1:]

        if name in ("help", "?"):
            return (
                "Commands:\n"
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

        if name == "status":
            cfg = self.cfg_mgr.config
            return (
                f"TikTok username: @{cfg.get('tiktok_username', '') or '<not set>'}\n"
                f"Intervals: {cfg.get('intervals', {})}\n"
                f"Daily time (GMT): {cfg.get('daily_summary', {}).get('time_gmt', '23:00')}\n"
                f"Maintenance: {cfg.get('maintenance_mode', False)}\n"
            )

        if name == "uptime":
            return f"Uptime: {self.uptime.get_uptime_str()}"

        if name == "ping":
            return "pong"

        if name == "features":
            return f"Features: {self.cfg_mgr.config.get('features', {})}"

        if name == "feature" and len(args) == 2:
            fname, state = args
            state = state.lower()
            if state not in ("on", "off"):
                return "Usage: feature <name> on/off"
            enabled = state == "on"
            self.feature_flags.set_flag(fname, enabled)
            return f"Feature '{fname}' set to {enabled} (not saved yet)."

        if name == "maintenance" and len(args) == 1:
            state = args[0].lower()
            if state not in ("on", "off"):
                return "Usage: maintenance on/off"
            enabled = state == "on"
            self.feature_flags.set_maintenance(enabled)
            return f"Maintenance mode set to {enabled} (not saved yet)."

        if name == "settiktok" and len(args) == 1:
            username = args[0]
            self.cfg_mgr.config["tiktok_username"] = username
            return f"TikTok username set to @{username} (not saved yet)."

        if name == "interval" and len(args) == 2:
            which, val = args
            if not val.isdigit():
                return "Usage: interval <offline|live|video|retry|daily> <value>"
            n = int(val)
            if which == "offline":
                return self._set_interval("offline", n, MIN_OFFLINE_INTERVAL)
            if which == "live":
                return self._set_interval("live_summary", n, MIN_LIVE_SUMMARY_INTERVAL)
            if which == "video":
                return self._set_interval("video", n, MIN_VIDEO_INTERVAL)
            if which == "retry":
                return self._set_interval("retry", n, None)
            if which == "daily":
                return self._set_interval("daily", n, None)
            return "Unknown interval type. Use offline/live/video/retry/daily."

        if name == "dailytime" and len(args) == 1:
            time_str = args[0]
            self.cfg_mgr.config.setdefault("daily_summary", {})["time_gmt"] = time_str
            return f"Daily summary time set to {time_str} GMT (not saved yet)."

        if name == "slash" and len(args) >= 1:
            sub = args[0].lower()
            disabled = self.cfg_mgr.config.setdefault("disabled_slash_commands", [])
            if sub == "list":
                return f"Disabled slash commands: {disabled or 'none'}"
            if sub in ("disable", "enable") and len(args) == 2:
                cmd = args[1]
                if sub == "disable":
                    if cmd not in disabled:
                        disabled.append(cmd)
                    return f"Slash command '{cmd}' disabled (hidden, not saved yet)."
                else:
                    if cmd in disabled:
                        disabled.remove(cmd)
                    return f"Slash command '{cmd}' enabled (visible, not saved yet)."
            return "Usage: slash disable <cmd> | slash enable <cmd> | slash list"

        if name == "save":
            self.cfg_mgr.save_config()
            return "Config saved."

        if name == "shutdown":
            log.info("Terminal requested full shutdown.")
            return "__SHUTDOWN__"

        if name in ("exit", "quit", "stop"):
            return "__EXIT__"

        return "Unknown command. Type 'help'."
