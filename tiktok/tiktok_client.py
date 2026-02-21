import asyncio
from utils.logger import log

from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, LiveEndEvent


class TikTokClient:
    def __init__(self, username: str, retry_interval: int):
        self.username = username
        self.retry_interval = retry_interval

        self.client = TikTokLiveClient(unique_id=username)

        self.is_live = False
        self.viewer_count = 0
        self.likes = 0
        self.followers = 0

        self.client.add_listener(ConnectEvent, self._on_connect)
        self.client.add_listener(LiveEndEvent, self._on_live_end)
        self.client.add_listener("room_update", self._on_room_update)

    async def _on_connect(self, event):
        log.info(f"[TikTokLive] Connected to @{self.username}")

    async def _on_room_update(self, event):
        room_id = getattr(event, "room_id", None)
        if room_id:
            if not self.is_live:
                log.info("[TikTokLive] LIVE START detected (room_update)")
            self.is_live = True

    async def _on_live_end(self, event):
        log.info("[TikTokLive] LIVE END detected")
        self.is_live = False

    async def start_live_listener(self):
        while True:
            try:
                await self.client.start()
            except Exception as e:
                msg = str(e).lower()
                if "only make one connection" in msg:
                    log.warning("[TikTokLive] Duplicate connection prevented")
                else:
                    log.error(f"[TikTokLive] Error: {e}")
                await asyncio.sleep(self.retry_interval)

    async def fetch_live_status(self):
        return {
            "is_live": self.is_live,
            "viewer_count": self.viewer_count,
            "likes": self.likes,
            "followers": self.followers,
        }

    async def fetch_profile_stats(self):
        return {
            "followers": self.followers,
            "likes": self.likes,
            "views": 0,
        }
