from typing import Dict, Any

from .defaults import (
    DEFAULT_CONFIG,
    MIN_OFFLINE_INTERVAL,
    MIN_LIVE_SUMMARY_INTERVAL,
    MIN_VIDEO_INTERVAL,
)


def _ensure_int(value: Any, default: int, minimum: int) -> int:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    return max(v, minimum)


def validate_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    data = DEFAULT_CONFIG.copy()
    data.update(cfg)

    intervals = data.get("intervals", {})
    data["intervals"] = {
        "offline": _ensure_int(
            intervals.get("offline", DEFAULT_CONFIG["intervals"]["offline"]),
            DEFAULT_CONFIG["intervals"]["offline"],
            MIN_OFFLINE_INTERVAL,
        ),
        "live_summary": _ensure_int(
            intervals.get("live_summary", DEFAULT_CONFIG["intervals"]["live_summary"]),
            DEFAULT_CONFIG["intervals"]["live_summary"],
            MIN_LIVE_SUMMARY_INTERVAL,
        ),
        "video": _ensure_int(
            intervals.get("video", DEFAULT_CONFIG["intervals"]["video"]),
            DEFAULT_CONFIG["intervals"]["video"],
            MIN_VIDEO_INTERVAL,
        ),
    }

    return data
