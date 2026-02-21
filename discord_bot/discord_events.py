import discord
from discord import app_commands

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from config.paths import Paths
from utils.logger import log
from utils.uptime import Uptime
from .slash_commands import setup_slash_commands


class DiscordBot(discord.Client):
    def __init__(
        self,
        intents: discord.Intents,
        config_manager: ConfigManager,
        feature_flags: FeatureFlags,
        paths: Paths,
        polling_engine,
        live_summary_engine,
        final_summary_engine,
        video_upload_engine,
        daily_summary_engine,
        uptime: Uptime,
    ) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.config_manager = config_manager
        self.feature_flags = feature_flags
        self.paths = paths
        self.polling_engine = polling_engine
        self.live_summary_engine = live_summary_engine
        self.final_summary_engine = final_summary_engine
        self.video_upload_engine = video_upload_engine
        self.daily_summary_engine = daily_summary_engine
        self.uptime = uptime

    async def setup_hook(self) -> None:
        await setup_slash_commands(
            tree=self.tree,
            client=self,
            config_manager=self.config_manager,
            feature_flags=self.feature_flags,
            polling_engine=self.polling_engine,
            live_summary_engine=self.live_summary_engine,
            final_summary_engine=self.final_summary_engine,
            video_upload_engine=self.video_upload_engine,
            daily_summary_engine=self.daily_summary_engine,
            uptime=self.uptime,
        )

    async def on_ready(self) -> None:
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        try:
            await self.tree.sync()
            log.info("Slash commands synced.")
        except Exception as e:
            log.error(f"Failed to sync slash commands: {e}")

    async def _send(self, feature_name: str, channel_key: str, message: str):
        cfg = self.config_manager.config

        if not cfg.get("features", {}).get(feature_name, False):
            return

        channel_id = cfg.get("channels", {}).get(channel_key)
        if not channel_id:
            log.error(f"{feature_name} enabled but no channel set for '{channel_key}'.")
            return

        channel = self.get_channel(int(channel_id))
        if not channel:
            log.error(f"Channel {channel_id} not found for {feature_name}.")
            return

        try:
            await channel.send(message)
        except Exception as e:
            log.error(f"Failed to send {feature_name}: {e}")

    # ---- Notification types (aligned with config.json) ----

    async def send_live_notification(self, stats=None):
        await self._send("live_notifications", "live", "🔴 **The streamer is LIVE on TikTok!**")

    async def send_live_summary(self, summary_text: str):
        await self._send("livesummary", "livesummary", f"📊 **Live Summary:**\n{summary_text}")

    async def send_final_summary(self, summary_text: str):
        await self._send("finalsummary", "finalsummary", f"📘 **Final Summary:**\n{summary_text}")

    async def send_new_video(self, video_id: str):
        await self._send("video_notifications", "videos", f"🎥 **New TikTok video posted!**\nID: `{video_id}`")

    async def send_daily_summary(self, summary_text: str):
        # your config uses "daily_summary" feature and "summary" channel
        await self._send("daily_summary", "summary", f"🗓️ **Daily Summary:**\n{summary_text}")

    async def send_battery_warning(self, pct: int):
        await self._send("battery_warnings", "battery", f"⚠️ **Battery low:** {pct}%")
