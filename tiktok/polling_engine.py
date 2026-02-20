import asyncio

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from utils.logger import log
from .tiktok_client import TikTokClientWrapper


class PollingEngine:
    def __init__(self, config_manager: ConfigManager, feature_flags: FeatureFlags, discord_client):
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.discord_client = discord_client
        self._running = True
        self._tt = TikTokClientWrapper(self.config_manager.config.get("tiktok_username", ""))

    async def run(self):
        await self.discord_client.wait_until_ready()
        # Start TikTok client in background (live mode engine also uses it)
        asyncio.create_task(self._tt.start_forever())

        while self._running:
            cfg = self.config_manager.config
            interval = cfg["intervals"]["offline"]
            is_live = await self._tt.is_live()
            log.info(f"PollingEngine: is_live={is_live}")
            await asyncio.sleep(interval * 60)

    async def stop(self):
        self._running = False
