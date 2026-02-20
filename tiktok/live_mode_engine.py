import asyncio
from utils.logger import log


class LiveModeEngine:
    def __init__(self, cfg_mgr, tiktok_client):
        self.cfg_mgr = cfg_mgr
        self.client = tiktok_client
        self.running = False
        self.on_live_end = None  # callback

    async def start(self):
        self.running = True
        log.info("LiveModeEngine started.")

        while self.running:
            stats = await self.client.fetch_live_status()
            if stats and not stats["is_live"]:
                log.info("Stream ended — triggering final summary.")
                if self.on_live_end:
                    await self.on_live_end()
                break
            await asyncio.sleep(10)

    def stop(self):
        self.running = False
