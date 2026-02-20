import asyncio
import json
from datetime import datetime
from utils.logger import log


class DailySummaryEngine:
    def __init__(self, cfg_mgr, daily_dir):
        self.cfg_mgr = cfg_mgr
        self.daily_dir = daily_dir
        self.running = False
        self.on_daily_summary = None  # callback

    async def start(self):
        self.running = True
        log.info("DailySummaryEngine started.")

        while self.running:
            now = datetime.utcnow().strftime("%H:%M")
            target = self.cfg_mgr.config["daily_summary"]["time_gmt"]

            if now == target:
                await self.generate_summary()

            await asyncio.sleep(30)

    def stop(self):
        self.running = False

    async def generate_summary(self):
        date = datetime.utcnow().strftime("%Y-%m-%d")
        path = self.daily_dir / f"{date}.json"

        if not path.exists():
            log.warning("No daily stats collected yet.")
            return

        snapshots = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    snapshots.append(json.loads(line))
                except:
                    pass

        if len(snapshots) < 2:
            log.warning("Not enough snapshots for daily summary.")
            return

        first = snapshots[0]
        last = snapshots[-1]

        summary = {
            "followers": last["followers"],
            "followers_gained": last["followers"] - first["followers"],
            "likes_gained": last["likes"] - first["likes"],
            "views_gained": last["views"] - first["views"],
        }

        log.info(f"Daily summary: {summary}")

        if self.on_daily_summary:
            await self.on_daily_summary(summary)
