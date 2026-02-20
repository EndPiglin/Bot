import asyncio
from utils.logger import log


class LiveSummaryEngine:
    def __init__(self, cfg_mgr, tiktok_client, interval_minutes: int):
        self.cfg_mgr = cfg_mgr
        self.client = tiktok_client
        self.interval = interval_minutes
        self.running = False
        self.on_summary = None  # callback

    async def start(self):
        self.running = True
        log.info("LiveSummaryEngine started.")

        while self.running:
            stats = await self.client.fetch_live_status()
            if stats and stats["is_live"]:
                if self.on_summary:
                    await self.on_summary(stats)
            await asyncio.sleep(self.interval * 60)

    def stop(self):
        self.running = False
