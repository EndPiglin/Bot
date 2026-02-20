from datetime import datetime


def banner(title: str) -> str:
    line = "=" * (len(title) + 4)
    return f"{line}\n| {title} |\n{line}"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_info(msg: str) -> str:
    return f"[INFO {timestamp()}] {msg}"


def format_warn(msg: str) -> str:
    return f"[WARN {timestamp()}] {msg}"


def format_error(msg: str) -> str:
    return f"[ERR  {timestamp()}] {msg}"
