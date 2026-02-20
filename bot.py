import asyncio
import os
import signal
import sys

import discord

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from config.paths import Paths
from utils.logger import log, setup_logging
from utils.uptime import UptimeTracker
from utils.watchdog import Watchdog
from utils.battery_monitor import BatteryMonitor
from discord_bot.discord_events import setup_discord_events
from discord_bot.slash_commands import setup_slash_commands
from terminal.tui import start_terminal_loop
from tiktok.polling_engine import PollingEngine
from tiktok.live_mode_engine import LiveModeEngine
from tiktok.live_summary_engine import LiveSummaryEngine
from tiktok.final_summary_engine import FinalSummaryEngine
from tiktok.video_upload_engine import VideoUploadEngine
from tiktok.daily_summary_engine import DailySummaryEngine

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.messages = True


class BotApp:
    def __init__(self):
        setup_logging()
        self.paths = Paths()
        self.config_manager = ConfigManager(self.paths)
        self.config = self.config_manager.load_config()
        self.feature_flags = FeatureFlags(self.config)
        self.uptime = UptimeTracker()

        self.client = discord.Client(intents=INTENTS)
        self.tree = discord.app_commands.CommandTree(self.client)

        # expose tree to events
        self.client.tree = self.tree

        self.loop = asyncio.get_event_loop()
        self.shutdown_event = asyncio.Event()

        # Engines
        self.polling_engine = PollingEngine(self.config_manager, self.feature_flags, self.client)
        self.live_mode_engine = LiveModeEngine(self.config_manager, self.feature_flags, self.client)
        self.live_summary_engine = LiveSummaryEngine(self.config_manager, self.feature_flags, self.client)
        self.final_summary_engine = FinalSummaryEngine(self.config_manager, self.feature_flags, self.client)
        self.video_upload_engine = VideoUploadEngine(self.config_manager, self.feature_flags, self.client)
        self.daily_summary_engine = DailySummaryEngine(self.config_manager, self.feature_flags, self.client)

        self.watchdog = Watchdog()
        self.battery_monitor = BatteryMonitor(self.config_manager, self.client)

    async def start(self):
        setup_discord_events(
            client=self.client,
            config_manager=self.config_manager,
            feature_flags=self.feature_flags,
            uptime=self.uptime,
            shutdown_event=self.shutdown_event,
            app=self,
        )

        await setup_slash_commands(
            tree=self.tree,
            client=self.client,
            config_manager=self.config_manager,
            feature_flags=self.feature_flags,
            polling_engine=self.polling_engine,
            live_summary_engine=self.live_summary_engine,
            final_summary_engine=self.final_summary_engine,
            video_upload_engine=self.video_upload_engine,
            daily_summary_engine=self.daily_summary_engine,
            uptime=self.uptime,
        )

        # BOT_TOKEN from environment overrides config
        token = os.getenv("DISCORD_TOKEN") or self.config.get("discord_token")
        if not token:
            log.error("No BOT_TOKEN set. Use: export BOT_TOKEN=xxxx")
            sys.exit(1)

        try:
            self.loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(self.stop()))
            self.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.stop()))
        except NotImplementedError:
            pass

        await self.client.start(token)

    async def start_background_tasks(self):
        log.info("Starting background engines...")

        self.watchdog.register_task("polling", self.loop.create_task(self.polling_engine.run()))
        self.watchdog.register_task("live_mode", self.loop.create_task(self.live_mode_engine.run()))
        self.watchdog.register_task("live_summary", self.loop.create_task(self.live_summary_engine.run()))
        self.watchdog.register_task("final_summary", self.loop.create_task(self.final_summary_engine.run()))
        self.watchdog.register_task("video_upload", self.loop.create_task(self.video_upload_engine.run()))
        self.watchdog.register_task("daily_summary", self.loop.create_task(self.daily_summary_engine.run()))
        self.watchdog.register_task("battery", self.loop.create_task(self.battery_monitor.run()))
        self.watchdog.register_task("watchdog", self.loop.create_task(self.watchdog.run()))

        # Terminal UI
        self.loop.create_task(
            start_terminal_loop(
                config_manager=self.config_manager,
                feature_flags=self.feature_flags,
                polling_engine=self.polling_engine,
                live_summary_engine=self.live_summary_engine,
                final_summary_engine=self.final_summary_engine,
                video_upload_engine=self.video_upload_engine,
                daily_summary_engine=self.daily_summary_engine,
                uptime=self.uptime,
                app=self,
            )
        )

    async def stop(self):
        if self.shutdown_event.is_set():
            return
        log.info("Shutdown requested...")
        self.shutdown_event.set()
        await self.client.close()
        await self.watchdog.stop_all()
        log.info("Bot stopped.")
        asyncio.get_event_loop().stop()


app = BotApp()

if __name__ == "__main__":
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        pass
