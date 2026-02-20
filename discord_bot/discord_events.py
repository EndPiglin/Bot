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
