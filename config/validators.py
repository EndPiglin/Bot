from typing import Any, Dict

from .defaults import (
    MIN_OFFLINE_INTERVAL,
    MIN_LIVE_SUMMARY_INTERVAL,
    MIN_VIDEO_INTERVAL,
    DEFAULT_CONFIG,
)


def _ensure_section(cfg: Dict, key: str, default: Any) -> Any:
    if key not in cfg or not isinstance(cfg[key], type(default)):
        cfg[key] = default.copy() if isinstance(default, dict) else default
    return cfg[key]


def validate_config(config: Dict) -> Dict:
    cfg = config or {}

    # Base sections
    _ensure_section(cfg, "features", DEFAULT_CONFIG["features"])
    _ensure_section(cfg, "intervals", DEFAULT_CONFIG["intervals"])
    _ensure_section(cfg, "daily_summary", DEFAULT_CONFIG["daily_summary"])
    _ensure_section(cfg, "channels", DEFAULT_CONFIG["channels"])
    _ensure_section(cfg, "roles", DEFAULT_CONFIG["roles"])

    # Simple scalars
    cfg.setdefault("discord_token", DEFAULT_CONFIG["discord_token"])
    cfg.setdefault("tiktok_username", DEFAULT_CONFIG["tiktok_username"])
    cfg.setdefault("admin_users", [])
    cfg.setdefault("admin_roles", [])
    cfg.setdefault("maintenance_mode", False)
    cfg.setdefault("disabled_slash_commands", [])

    # Intervals
    intervals = cfg["intervals"]
    intervals["offline"] = max(int(intervals.get("offline", 10)), MIN_OFFLINE_INTERVAL)
    intervals["live_summary"] = max(
        int(intervals.get("live_summary", 10)), MIN_LIVE_SUMMARY_INTERVAL
    )
    intervals["video"] = max(int(intervals.get("video", 15)), MIN_VIDEO_INTERVAL)
    intervals["retry"] = max(int(intervals.get("retry", 5)), 1)
    intervals["daily"] = max(int(intervals.get("daily", 60)), 1)

    # Daily summary
    daily_summary = cfg["daily_summary"]
    time_gmt = str(daily_summary.get("time_gmt", "23:00"))
    # very light validation: HH:MM
    if len(time_gmt) != 5 or time_gmt[2] != ":":
        time_gmt = "23:00"
    daily_summary["time_gmt"] = time_gmt

    # Disabled slash commands
    if not isinstance(cfg["disabled_slash_commands"], list):
        cfg["disabled_slash_commands"] = []

    return cfg
