import asyncio

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from utils.logger import log
from discord_bot.embeds import build_live_start_embed
from .tiktok_client import TikTokClientWrapper


class LiveModeEngine:
    def __init__(self, config_manager: ConfigManager, feature_flags: FeatureFlags, discord_client):
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.discord_client = discord_client
        self._running = True
        self._already_notified = False
        self._tt = TikTokClientWrapper(self.config_manager.config.get("tiktok_username", ""))

    async def run(self):
        await self.discord_client.wait_until_ready()
        asyncio.create_task(self._tt.start_forever())

        while self._running:
            if self.feature_flags.is_maintenance():
                await asyncio.sleep(10)
                continue

            if not self.feature_flags.is_enabled("live_notifications"):
                await asyncio.sleep(30)
                continue

            is_live = await self._tt.is_live()
            if is_live and not self._already_notified:
                await self._send_live_start()
                self._already_notified = True
            elif not is_live:
                self._already_notified = False

            await asyncio.sleep(30)

    async def _send_live_start(self):
        cfg = self.config_manager.config
        channel_id = cfg["channels"]["live"]
        if not channel_id:
            log.warning("Live channel not set; cannot send live notification.")
            return
        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            log.warning("Live channel not found in guilds.")
            return

        embed = build_live_start_embed(cfg.get("tiktok_username", ""))
        await channel.send(embed=embed)
        log.info("Sent live start notification.")

    async def stop(self):
        self._running = False
