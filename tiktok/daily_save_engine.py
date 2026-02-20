import asyncio
import json
from datetime import datetime
from utils.logger import log


class DailySaveEngine:
    def __init__(self, cfg_mgr, tiktok_client, daily_dir, interval_minutes: int):
        self.cfg_mgr = cfg_mgr
        self.client = tiktok_client
        self.daily_dir = daily_dir
        self.interval = interval_minutes
        self.running = False

    async def start(self):
        self.running = True
        log.info("DailySaveEngine started.")

        while self.running:
            stats = await self.client.fetch_profile_stats()
            if stats:
                date = datetime.utcnow().strftime("%Y-%m-%d")
                path = self.daily_dir / f"{date}.json"

                try:
                    with path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(stats) + "\n")
                except Exception as e:
                    log.error(f"Failed to save daily stats: {e}")

            await asyncio.sleep(self.interval * 60)

    def stop(self):
        self.running = False
