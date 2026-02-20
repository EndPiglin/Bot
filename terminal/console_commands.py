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
        cmd = cmd.strip()
        if not cmd:
            return ""

        parts = cmd.split()
        name = parts[0].lower()
        args = parts[1:]

        # ---------------------------------------------------------
        # HELP
        # ---------------------------------------------------------
        if name in ("help", "?"):
            return (
                "=== GENERAL ===\n"
                "  help                      - show this help\n"
                "  status                    - show basic status\n"
                "  uptime                    - show uptime\n"
                "  ping                      - quick responsiveness check\n"
                "\n"
                "=== ADMIN CONTROL ===\n"
                "  admin adduser <id>        - add admin user\n"
                "  admin removeuser <id>     - remove admin user\n"
                "  admin addrole <id>        - add admin role\n"
                "  admin removerole <id>     - remove admin role\n"
                "  channels                  - list feature channels\n"
                "  roles                     - list feature roles\n"
                "  setchannel <feature> <id> - set channel for feature\n"
                "  setrole <feature> <id>    - set role for feature\n"
                "\n"
                "=== FEATURES & MAINTENANCE ===\n"
                "  features                  - list feature flags\n"
                "  feature <name> on/off     - toggle feature\n"
                "  maintenance on/off        - toggle maintenance mode\n"
                "\n"
                "=== TIKTOK SETTINGS ===\n"
                "  settiktok <username>      - set TikTok username\n"
                "\n"
                "=== INTERVALS ===\n"
                "  interval offline N        - set offline interval (min)\n"
                "  interval live N           - set live summary interval (min)\n"
                "  interval video N          - set video interval (min)\n"
                "  interval retry N          - set TikTok retry interval (sec)\n"
                "  interval daily N          - set daily stats save interval (min)\n"
                "  dailytime HH:MM           - set daily summary time (GMT)\n"
                "\n"
                "=== SLASH COMMANDS ===\n"
                "  slash disable <cmd>       - hide a slash command\n"
                "  slash enable <cmd>        - show a slash command\n"
                "  slash list                - list disabled slash commands\n"
                "\n"
                "=== CONFIG & SYSTEM ===\n"
                "  save                      - save config\n"
                "  shutdown                  - shutdown whole bot\n"
                "  exit / quit / stop        - stop terminal loop only\n"
            )


        # ---------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------
        if name == "status":
            cfg = self.cfg_mgr.config
            return (
                f"TikTok username: @{cfg.get('tiktok_username', '') or '<not set>'}\n"
                f"Intervals: {cfg.get('intervals', {})}\n"
                f"Daily time (GMT): {cfg.get('daily_summary', {}).get('time_gmt', '23:00')}\n"
                f"Maintenance: {cfg.get('maintenance_mode', False)}\n"
                f"Admin users: {cfg.get('admin_users', [])}\n"
                f"Admin roles: {cfg.get('admin_roles', [])}\n"
            )

        # ---------------------------------------------------------
        # BASIC COMMANDS
        # ---------------------------------------------------------
        if name == "uptime":
            return f"Uptime: {self.uptime.get_uptime_str()}"

        if name == "ping":
            return "pong"

        if name == "features":
            return f"Features: {self.cfg_mgr.config.get('features', {})}"

        # ---------------------------------------------------------
        # FEATURE FLAGS
        # ---------------------------------------------------------
        if name == "feature" and len(args) == 2:
            fname, state = args
            state = state.lower()
            if state not in ("on", "off"):
                return "Usage: feature <name> on/off"
            enabled = state == "on"
            self.feature_flags.set_flag(fname, enabled)
            return f"Feature '{fname}' set to {enabled} (not saved yet)."

        # ---------------------------------------------------------
        # MAINTENANCE MODE
        # ---------------------------------------------------------
        if name == "maintenance" and len(args) == 1:
            state = args[0].lower()
            if state not in ("on", "off"):
                return "Usage: maintenance on/off"
            enabled = state == "on"
            self.feature_flags.set_maintenance(enabled)
            return f"Maintenance mode set to {enabled} (not saved yet)."

        # ---------------------------------------------------------
        # SET TIKTOK USERNAME
        # ---------------------------------------------------------
        if name == "settiktok" and len(args) == 1:
            username = args[0]
            self.cfg_mgr.config["tiktok_username"] = username
            return f"TikTok username set to @{username} (not saved yet)."

        # ---------------------------------------------------------
        # INTERVALS
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # DAILY SUMMARY TIME
        # ---------------------------------------------------------
        if name == "dailytime" and len(args) == 1:
            time_str = args[0]
            self.cfg_mgr.config.setdefault("daily_summary", {})["time_gmt"] = time_str
            return f"Daily summary time set to {time_str} GMT (not saved yet)."

        # ---------------------------------------------------------
        # ADMIN COMMANDS
        # ---------------------------------------------------------
        if name == "admin" and len(args) >= 2:
            sub = args[0].lower()
            value = args[1]

            cfg = self.cfg_mgr.config
            cfg.setdefault("admin_users", [])
            cfg.setdefault("admin_roles", [])

            if sub == "adduser":
                if value not in cfg["admin_users"]:
                    cfg["admin_users"].append(value)
                return f"Added admin user {value} (not saved yet)."

            if sub == "removeuser":
                if value in cfg["admin_users"]:
                    cfg["admin_users"].remove(value)
                return f"Removed admin user {value} (not saved yet)."

            if sub == "addrole":
                if value not in cfg["admin_roles"]:
                    cfg["admin_roles"].append(value)
                return f"Added admin role {value} (not saved yet)."

            if sub == "removerole":
                if value in cfg["admin_roles"]:
                    cfg["admin_roles"].remove(value)
                return f"Removed admin role {value} (not saved yet)."

            return "Usage: admin <adduser|removeuser|addrole|removerole> <id>"

        # ---------------------------------------------------------
        # SET CHANNEL / ROLE FOR FEATURES
        # ---------------------------------------------------------
        if name == "channels":
            ch = self.cfg_mgr.config.setdefault("channels", {})
            if not ch:
                return "No channels configured."
            return "\n".join(f"{k}: {v}" for k, v in ch.items())

        if name == "roles":
            rl = self.cfg_mgr.config.setdefault("roles", {})
            if not rl:
                return "No roles configured."
            return "\n".join(f"{k}: {v}" for k, v in rl.items())

        if name == "setchannel" and len(args) == 2:
            feature, channel_id = args

            if not channel_id.isdigit():
                return "Channel ID must be numeric."

            self.cfg_mgr.config.setdefault("channels", {})[feature] = int(channel_id)
            return f"Channel for '{feature}' set to {channel_id} (not saved yet)."

        if name == "setrole" and len(args) == 2:
            feature, role_id = args

            if not role_id.isdigit():
                return "Role ID must be numeric."

            self.cfg_mgr.config.setdefault("roles", {})[feature] = int(role_id)
            return f"Role for '{feature}' set to {role_id} (not saved yet)."

        # ---------------------------------------------------------
        # SLASH COMMAND VISIBILITY
        # ---------------------------------------------------------
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
                    return f"Slash command '{cmd}' disabled (not saved yet)."
                else:
                    if cmd in disabled:
                        disabled.remove(cmd)
                    return f"Slash command '{cmd}' enabled (not saved yet)."
            return "Usage: slash disable <cmd> | slash enable <cmd> | slash list"

        # ---------------------------------------------------------
        # SAVE CONFIG
        # ---------------------------------------------------------
        if name == "save":
            self.cfg_mgr.save_config()
            return "Config saved."

        # ---------------------------------------------------------
        # SHUTDOWN
        # ---------------------------------------------------------
        if name == "shutdown":
            log.info("Terminal requested full shutdown.")
            return "__SHUTDOWN__"

        if name in ("exit", "quit", "stop"):
            return "__EXIT__"

        return "Unknown command. Type 'help'."
