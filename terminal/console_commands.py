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
        app,
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

    def _set_interval(self, key: str, value: int, minimum: int) -> str:
        # terminal is allowed to go below minimum, but we still show a warning
        if value < minimum:
            self.log_window.add(f"Warning: {key} below recommended minimum ({minimum} minutes).")
        self.cfg_mgr.config["intervals"][key] = value
        return f"Interval '{key}' set to {value} minutes (not saved yet)."

    def handle(self, cmd: str) -> str:
        if not cmd:
            return ""

        parts = cmd.split()
        name = parts[0].lower()
        args = parts[1:]

        if name in ("help", "?"):
            return (
                "Commands:\n"
                "  help                 - show this help\n"
                "  status               - show basic status\n"
                "  uptime               - show uptime\n"
                "  ping                 - quick responsiveness check\n"
                "  features             - list feature flags\n"
                "  feature <name> on/off- toggle feature\n"
                "  maintenance on/off   - toggle maintenance mode\n"
                "  settiktok <username> - set TikTok username\n"
                "  interval offline N   - set offline interval (min)\n"
                "  interval live N      - set live summary interval (min)\n"
                "  interval video N     - set video interval (min)\n"
                "  save                 - save config\n"
                "  shutdown             - shutdown whole bot\n"
                "  exit / quit / stop   - stop terminal loop only\n"
            )

        if name == "status":
            cfg = self.cfg_mgr.config
            return (
                f"Discord token set: {'yes' if cfg.get('discord_token') else 'env/DISCORD_TOKEN'}\n"
                f"TikTok username: @{cfg.get('tiktok_username', '') or '<not set>'}\n"
                f"Intervals: {cfg.get('intervals', {})}\n"
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
                return "Usage: interval <offline|live|video> <minutes>"
            minutes = int(val)
            if which == "offline":
                return self._set_interval("offline", minutes, MIN_OFFLINE_INTERVAL)
            if which == "live":
                return self._set_interval("live_summary", minutes, MIN_LIVE_SUMMARY_INTERVAL)
            if which == "video":
                return self._set_interval("video", minutes, MIN_VIDEO_INTERVAL)
            return "Unknown interval type. Use offline/live/video."

        if name == "save":
            self.cfg_mgr.save_config()
            return "Config saved."

        if name == "shutdown":
            log.info("Terminal requested full shutdown.")
            return "__SHUTDOWN__"

        if name in ("exit", "quit", "stop"):
            return "__EXIT__"

        return "Unknown command. Type 'help'."
