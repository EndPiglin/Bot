import asyncio
from utils.logger import log


def safe_loop(func):
    """Wrap an async loop to prevent crashes."""
    async def wrapper(*args, **kwargs):
        while True:
            try:
                await func(*args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.error(f"Engine error: {e}")
                await asyncio.sleep(2)
    return wrapper
