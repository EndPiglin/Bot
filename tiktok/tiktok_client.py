import asyncio
from utils.logger import log


class TikTokClient:
    def __init__(self, username: str, retry_interval: int):
        self.username = username
        self.retry_interval = retry_interval
        self.live_data = None
        self.profile_data = None

    async def fetch_live_status(self):
        """
        Replace this with your actual TikTokLive API call.
        Must return:
            {
                "is_live": bool,
                "viewer_count": int,
                "likes": int,
                "followers": int
            }
        """
        try:
            # TODO: integrate your real TikTok API here
            return {
                "is_live": False,
                "viewer_count": 0,
                "likes": 0,
                "followers": 0,
            }
        except Exception as e:
            log.error(f"TikTok API error: {e}")
            await asyncio.sleep(self.retry_interval)
            return None

    async def fetch_profile_stats(self):
        """
        Replace with your real TikTok profile stats fetch.
        Must return:
            {
                "followers": int,
                "likes": int,
                "views": int
            }
        """
        try:
            return {
                "followers": 0,
                "likes": 0,
                "views": 0,
            }
        except Exception as e:
            log.error(f"TikTok profile fetch error: {e}")
            await asyncio.sleep(self.retry_interval)
            return None
