import asyncio

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from utils.logger import log
from discord_bot.embeds import build_video_upload_embed
from .tiktok_api import TikTokAPI


class VideoUploadEngine:
    def __init__(self, config_manager: ConfigManager, feature_flags: FeatureFlags, discord_client):
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.discord_client = discord_client
        self._running = True
        self.api = TikTokAPI(self.config_manager.config.get("tiktok_username", ""))
        self._last_video_id = None

    async def run(self):
        await self.discord_client.wait_until_ready()
        while self._running:
            if not self.feature_flags.is_enabled("video_notifications"):
                await asyncio.sleep(30)
                continue

            cfg = self.config_manager.config
            interval = cfg["intervals"]["video"]
            video = await self.api.get_latest_video()
            if video:
                vid_id = video["id"]
                if self._last_video_id is None:
                    self._last_video_id = vid_id
                elif vid_id != self._last_video_id:
                    await self._send_video_notification(video)
                    self._last_video_id = vid_id

            await asyncio.sleep(interval * 60)

    async def _send_video_notification(self, video: dict):
        cfg = self.config_manager.config
        channel_id = cfg["channels"]["videos"]
        if not channel_id:
            log.warning("Video channel not set.")
            return
        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            log.warning("Video channel not found.")
            return

        embed = build_video_upload_embed(video)
        await channel.send(embed=embed)
        log.info("Sent video upload notification.")

    async def stop(self):
        self._running = False
