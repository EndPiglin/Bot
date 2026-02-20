import asyncio
from datetime import datetime, time as dtime, timedelta, timezone

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from utils.logger import log
from utils.json_store import save_daily_summary
from discord_bot.embeds import build_daily_summary_embed
from .tiktok_api import TikTokAPI


class DailySummaryEngine:
    def __init__(self, config_manager: ConfigManager, feature_flags: FeatureFlags, discord_client):
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.discord_client = discord_client
        self._running = True
        self.api = TikTokAPI(self.config_manager.config.get("tiktok_username", ""))

    async def run(self):
        await self.discord_client.wait_until_ready()
        while self._running:
            if not self.feature_flags.is_enabled("daily_summary"):
                await asyncio.sleep(60)
                continue

            cfg = self.config_manager.config
            time_str = cfg["daily_summary"]["time_gmt"]
            hour, minute = map(int, time_str.split(":"))
            now = datetime.now(timezone.utc)
            target = datetime.combine(now.date(), dtime(hour, minute, tzinfo=timezone.utc))
            if target <= now:
                target += timedelta(days=1)
            wait_seconds = (target - now).total_seconds()
            log.info(f"Daily summary scheduled in {int(wait_seconds)} seconds.")
            await asyncio.sleep(wait_seconds)

            await self._send_daily_summary()

    async def _send_daily_summary(self):
        cfg = self.config_manager.config
        channel_id = cfg["channels"]["summary"]
        if not channel_id:
            log.warning("Daily summary channel not set.")
            return
        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            log.warning("Daily summary channel not found.")
            return

        stats = await self.api.get_daily_stats()
        if not stats:
            log.warning("Daily summary: failed to fetch stats.")
            return

        embed = build_daily_summary_embed(
            username=cfg.get("tiktok_username", ""),
            stats=stats,
        )
        await channel.send(embed=embed)
        log.info("Sent daily summary.")
        save_daily_summary(
            username=cfg.get("tiktok_username", ""),
            stats=stats,
        )

    async def stop(self):
        self._running = False
