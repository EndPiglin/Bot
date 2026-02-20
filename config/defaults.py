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
        "retry": 5,      # NEW: TikTok retry interval (seconds)
        "daily": 60,     # NEW: daily stats save interval (minutes)
    },

    "daily_summary": {
        "time_gmt": "23:00",  # NEW: when to send daily summary
    },

    "disabled_slash_commands": [],  # NEW: commands hidden from Discord

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
