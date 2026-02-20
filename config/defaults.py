MIN_OFFLINE_INTERVAL = 5
MIN_LIVE_SUMMARY_INTERVAL = 5
MIN_VIDEO_INTERVAL = 5

DEFAULT_CONFIG = {
    "discord_token": "",
    "tiktok_username": "",
    "admin_users": [],
    "admin_roles": [],
    "maintenance_mode": False,

    "features": {
        "live_notifications": True,
        "livesummary": True,
        "finalsummary": True,
        "video_notifications": True,
        "daily_summary": True,
        "battery_warnings": True,
        "shutdown_alerts": True,
    },

    "intervals": {
        "offline": 10,
        "live_summary": 10,
        "video": 15,
        "retry": 5,   # seconds
        "daily": 60,  # minutes (daily stats save)
    },

    "daily_summary": {
        "time_gmt": "23:00",
    },

    "disabled_slash_commands": [],

    "channels": {
        "live": None,
        "livesummary": None,
        "finalsummary": None,
        "videos": None,
        "summary": None,
    },

    "roles": {
        "live": None,
        "livesummary": None,
        "finalsummary": None,
        "videos": None,
        "summary": None,
    },
}
