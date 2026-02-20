import asyncio
from datetime import datetime

from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    DisconnectEvent,
    LiveEndEvent,
    LikeEvent,
    GiftEvent,
    StreamStatusEvent,
)

from utils.logger import log


class TikTokState:
    def __init__(self):
        self.live = False
        self.start_time: datetime | None = None
        self.last_viewers: int = 0
        self.peak_viewers: int = 0
        self.total_likes: int = 0
        self.total_gifts: int = 0


class TikTokClientWrapper:
    def __init__(self, username: str):
        self.username = username
        self.client: TikTokLiveClient | None = None
        self.state = TikTokState()
        self._lock = asyncio.Lock()

    async def ensure_client(self):
        if self.client is not None:
            return
        if not self.username:
            log.warning("TikTok: No username set yet.")
            return

        log.info(f"TikTok: Creating client for @{self.username}")
        self.client = TikTokLiveClient(unique_id=self.username)

        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            log.info(f"TikTok: Connected to @{self.username}")

        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            log.info(f"TikTok: Disconnected from @{self.username}")
            self.state.live = False

        @self.client.on(LiveEndEvent)
        async def on_live_end(event: LiveEndEvent):
            log.info("TikTok: LiveEndEvent received")
            self.state.live = False

        @self.client.on(StreamStatusEvent)
        async def on_stream_status(event: StreamStatusEvent):
            viewers = getattr(event, "viewerCount", 0)
            likes = getattr(event, "likeCount", self.state.total_likes)

            self.state.last_viewers = viewers
            self.state.total_likes = likes
            if viewers > self.state.peak_viewers:
                self.state.peak_viewers = viewers

            log.info(f"TikTok: StreamStatusEvent viewers={viewers} likes={likes}")

            if not self.state.live and viewers > 0:
                self.state.live = True
                self.state.start_time = datetime.utcnow()

        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            total = getattr(event, "totalLikes", None)
            if total is not None:
                self.state.total_likes = total

        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            gift = getattr(event, "gift", None)
            repeat = getattr(event, "repeatCount", 1)
            if gift and hasattr(gift, "diamond_count"):
                self.state.total_gifts += gift.diamond_count * repeat

    async def start_forever(self):
        await self.ensure_client()
        if self.client is None:
            return
        while True:
            try:
                await self.client.start()
            except Exception as e:
                log.warning(f"TikTok: Live mode error: {e}, retrying in 5s")
                await asyncio.sleep(5)
            else:
                break

    async def is_live(self) -> bool:
        await self.ensure_client()
        if self.client is None:
            return False
        return self.state.live
