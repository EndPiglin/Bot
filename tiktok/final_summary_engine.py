import asyncio
import time

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from utils.logger import log
from utils.json_store import save_stream_summary
from discord_bot.embeds import build_final_summary_embed
from .tiktok_client import TikTokClientWrapper


class FinalSummaryEngine:
    def __init__(self, config_manager: ConfigManager, feature_flags: FeatureFlags, discord_client):
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.discord_client = discord_client
        self._running = True
        self._tt = TikTokClientWrapper(self.config_manager.config.get("tiktok_username", ""))
        self._was_live = False
        self._stream_start = None

    async def run(self):
        await self.discord_client.wait_until_ready()
        while self._running:
            if not self.feature_flags.is_enabled("finalsummary"):
                await asyncio.sleep(30)
                continue

            is_live = await self._tt.is_live()
            now = int(time.time())

            if is_live and not self._was_live:
                self._stream_start = now
                self._was_live = True
            elif not is_live and self._was_live:
                await self._send_final_summary()
                self._was_live = False
                self._stream_start = None

            await asyncio.sleep(30)

    async def _send_final_summary(self):
        cfg = self.config_manager.config
        channel_id = cfg["channels"]["finalsummary"]
        if not channel_id:
            log.warning("Final summary channel not set.")
            return
        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            log.warning("Final summary channel not found.")
            return

        state = self._tt.state
        duration = 0
        if self._stream_start:
            duration = int(time.time()) - self._stream_start

        stats = {
            "peak_viewers": state.peak_viewers,
            "likes": state.total_likes,
            "gifts": state.total_gifts,
        }

        embed = build_final_summary_embed(
            username=cfg.get("tiktok_username", ""),
            duration_seconds=duration,
            stats=stats,
        )
        await channel.send(embed=embed)
        log.info("Sent final summary.")

        save_stream_summary(
            username=cfg.get("tiktok_username", ""),
            duration_seconds=duration,
            stats=stats,
        )

    async def stop(self):
        self._running = False
