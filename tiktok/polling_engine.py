import asyncio
from utils.logger import log


class PollingEngine:
    def __init__(self, cfg_mgr, tiktok_client, interval_minutes: int):
        self.cfg_mgr = cfg_mgr
        self.client = tiktok_client
        self.interval = interval_minutes  # minutes
        self.running = False
        self.on_live_start = None  # callback
        self._was_live = False     # track previous state

    async def start(self):
        self.running = True
        log.info("PollingEngine started.")

        while self.running:
            stats = await self.client.fetch_live_status()

            if stats and stats.get("is_live"):
                if not self._was_live:
                    log.info("Stream detected — switching to live mode.")
                    self._was_live = True
                    if self.on_live_start:
                        await self.on_live_start(stats)
            else:
                self._was_live = False

            await asyncio.sleep(self.interval * 60)

    def stop(self):
        self.running = False
