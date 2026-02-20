import json
import time

from config.paths import Paths


_paths = Paths()


def save_stream_summary(username: str, duration_seconds: int, stats: dict):
    ts = int(time.time())
    path = _paths.streams_dir / f"{username}_{ts}.json"
    data = {
        "username": username,
        "timestamp": ts,
        "duration_seconds": duration_seconds,
        "stats": stats,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_daily_summary(username: str, stats: dict):
    ts = int(time.time())
    path = _paths.daily_dir / f"{username}_{ts}.json"
    data = {
        "username": username,
        "timestamp": ts,
        "stats": stats,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
