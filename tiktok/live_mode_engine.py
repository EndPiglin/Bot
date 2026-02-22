import asyncio
from utils.logger import log


class LiveModeEngine:
    def __init__(self, cfg_mgr, tiktok_client):
        self.cfg_mgr = cfg_mgr
        self.client = tiktok_client
        self.running = False
        self.on_live_end = None

        self.was_live = False

    async def start(self):
        self.running = True
        log.info("LiveModeEngine started.")

        while self.running:
            stats = await self.client.fetch_live_status()

            if stats.get("is_live"):
                self.was_live = True

            # Only trigger live end if:
            # 1. A live was detected earlier
            # 2. Now the user is offline
            if self.was_live and not stats.get("is_live"):
                log.info("Stream ended — triggering final summary.")
                if self.on_live_end:
                    await self.on_live_end()
                break

            await asyncio.sleep(10)

    def stop(self):
        self.running = False
        self.was_live = False
