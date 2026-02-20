import asyncio
import time

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from utils.logger import log
from discord_bot.embeds import build_live_summary_embed
from .tiktok_client import TikTokClientWrapper


class LiveSummaryEngine:
    def __init__(self, config_manager: ConfigManager, feature_flags: FeatureFlags, discord_client):
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.discord_client = discord_client
        self._running = True
        self._tt = TikTokClientWrapper(self.config_manager.config.get("tiktok_username", ""))
        self._last_message = None
        self._stream_start = None

    async def run(self):
        await self.discord_client.wait_until_ready()
        while self._running:
            if not self.feature_flags.is_enabled("livesummary"):
                await asyncio.sleep(10)
                continue

            cfg = self.config_manager.config
            interval = cfg["intervals"]["live_summary"]
            is_live = await self._tt.is_live()
            if not is_live:
                self._stream_start = None
                await asyncio.sleep(interval * 60)
                continue

            if self._stream_start is None:
                self._stream_start = int(time.time())

            state = self._tt.state
            duration = int(time.time()) - self._stream_start

            channel_id = cfg["channels"]["livesummary"]
            if not channel_id:
                log.warning("Live summary channel not set.")
                await asyncio.sleep(interval * 60)
                continue

            channel = self.discord_client.get_channel(channel_id)
            if not channel:
                log.warning("Live summary channel not found.")
                await asyncio.sleep(interval * 60)
                continue

            stats = {
                "viewers": state.last_viewers,
                "peak_viewers": state.peak_viewers,
                "likes": state.total_likes,
                "gifts": state.total_gifts,
            }

            embed = build_live_summary_embed(
                username=cfg.get("tiktok_username", ""),
                duration_seconds=duration,
                stats=stats,
            )

            if self._last_message is None:
                self._last_message = await channel.send(embed=embed)
            else:
                await self._last_message.edit(embed=embed)

            log.info("Updated live summary.")
            await asyncio.sleep(interval * 60)

    async def get_last_message(self):
        return self._last_message

    async def stop(self):
        self._running = False
