from datetime import datetime


def now_gmt_hhmm() -> str:
    """Return current GMT time as HH:MM."""
    return datetime.utcnow().strftime("%H:%M")


def parse_hhmm(s: str) -> str:
    """Validate HH:MM format, fallback to 23:00."""
    if len(s) == 5 and s[2] == ":":
        hh, mm = s.split(":")
        if hh.isdigit() and mm.isdigit():
            h = int(hh)
            m = int(mm)
            if 0 <= h <= 23 and 0 <= m <= 59:
                return s
    return "23:00"
