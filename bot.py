import asyncio
import signal
import sys

import discord

from config.paths import Paths
from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags

from utils.logger import log
from utils.uptime import Uptime

from tiktok.tiktok_api import TikTokAPI
from tiktok.polling_engine import PollingEngine
from tiktok.live_mode_engine import LiveModeEngine
from tiktok.live_summary_engine import LiveSummaryEngine
from tiktok.final_summary_engine import FinalSummaryEngine
from tiktok.video_upload_engine import VideoUploadEngine
from tiktok.daily_save_engine import DailySaveEngine
from tiktok.daily_summary_engine import DailySummaryEngine

from discord_bot.discord_events import DiscordBot

from terminal.app import MainApp
from terminal.log_window import LogWindow
from terminal.console_commands import ConsoleCommands
from terminal.input_handler import InputHandler


class BotOrchestrator:
    def __init__(self):
        # Paths + config
        self.paths = Paths()
        self.cfg_mgr = ConfigManager(self.paths)
        self.config = self.cfg_mgr.load_config()

        # Feature flags
        self.feature_flags = FeatureFlags(self.config)

        # Uptime
        self.uptime = Uptime()

        # Log window (for TUI)
        self.log_window = LogWindow()
        log.log_window = self.log_window  # connect logger to TUI

        # TikTok API
        username = self.config.get("tiktok_username", "")
        retry = self.config["intervals"]["retry"]
        self.tiktok = TikTokAPI(username)
        self.retry_interval = retry

        # Engines
        self.polling_engine = PollingEngine(
            self.cfg_mgr,
            self.tiktok,
            self.config["intervals"]["offline"],
        )

        self.live_mode_engine = LiveModeEngine(
            self.cfg_mgr,
            self.tiktok,
        )

        self.live_summary_engine = LiveSummaryEngine(
            self.cfg_mgr,
            self.tiktok,
            self.config["intervals"]["live_summary"],
        )

        self.final_summary_engine = FinalSummaryEngine(self.cfg_mgr)

        self.video_upload_engine = VideoUploadEngine(
            self.cfg_mgr,
            self.tiktok,
            self.config["intervals"]["video"],
        )

        self.daily_save_engine = DailySaveEngine(
            self.cfg_mgr,
            self.tiktok,
            self.paths.daily_dir,
            self.config["intervals"]["daily"],
        )

        self.daily_summary_engine = DailySummaryEngine(
            self.cfg_mgr,
            self.paths.daily_dir,
        )

        # Wire engine callbacks
        self._wire_engines()

        # Discord bot
        intents = discord.Intents.default()
        intents.message_content = False
        intents.guilds = True

        self.discord_bot = DiscordBot(
            intents=intents,
            config_manager=self.cfg_mgr,
            feature_flags=self.feature_flags,
            paths=self.paths,
            polling_engine=self.polling_engine,
            live_summary_engine=self.live_summary_engine,
            final_summary_engine=self.final_summary_engine,
            video_upload_engine=self.video_upload_engine,
            daily_summary_engine=self.daily_summary_engine,
            uptime=self.uptime,
        )

        # Terminal commands
        self.console_commands = ConsoleCommands(
            config_manager=self.cfg_mgr,
            feature_flags=self.feature_flags,
            polling_engine=self.polling_engine,
            live_summary_engine=self.live_summary_engine,
            final_summary_engine=self.final_summary_engine,
            video_upload_engine=self.video_upload_engine,
            daily_summary_engine=self.daily_summary_engine,
            uptime=self.uptime,
            log_window=self.log_window,
        )

        self.input_handler = InputHandler(self.console_commands)

        # TUI
        self.tui = MainApp(
            config_manager=self.cfg_mgr,
            feature_flags=self.feature_flags,
            polling_engine=self.polling_engine,
            live_summary_engine=self.live_summary_engine,
            final_summary_engine=self.final_summary_engine,
            video_upload_engine=self.video_upload_engine,
            daily_summary_engine=self.daily_summary_engine,
            log_window=self.log_window,
        )

    # -------------------------------------------------------------------------
    # Engine wiring
    # -------------------------------------------------------------------------

    def _wire_engines(self):
        # When polling detects live start → start live mode + live summary
        async def on_live_start(stats):
            log.info("Callback: LIVE START")
            asyncio.create_task(self.live_mode_engine.start())
            asyncio.create_task(self.live_summary_engine.start())

        self.polling_engine.on_live_start = on_live_start

        # When live mode detects live end → final summary
        async def on_live_end():
            log.info("Callback: LIVE END")
            await self.final_summary_engine.run({"end": True})
            self.live_summary_engine.stop()

        self.live_mode_engine.on_live_end = on_live_end

        # Live summary callback
        async def on_live_summary(stats):
            log.info(f"Live summary callback: {stats}")

        self.live_summary_engine.on_summary = on_live_summary

        # Final summary callback
        async def on_final_summary(data):
            log.info(f"Final summary callback: {data}")

        self.final_summary_engine.on_final_summary = on_final_summary

        # New video callback
        async def on_new_video(video_id):
            log.info(f"New video detected: {video_id}")

        self.video_upload_engine.on_new_video = on_new_video

        # Daily summary callback
        async def on_daily_summary(summary):
            log.info(f"Daily summary callback: {summary}")

        self.daily_summary_engine.on_daily_summary = on_daily_summary

    # -------------------------------------------------------------------------
    # Main run loop
    # -------------------------------------------------------------------------

    async def start_engines(self):
        log.info("Starting all engines...")

        asyncio.create_task(self.polling_engine.start())
        asyncio.create_task(self.video_upload_engine.start())
        asyncio.create_task(self.daily_save_engine.start())
        asyncio.create_task(self.daily_summary_engine.start())

    async def run(self):
        # Start engines
        await self.start_engines()

        # Start Discord bot
        token = self.config.get("discord_token", "")
        if not token:
            log.error("No Discord token set in config.json")
            return

        # Run Discord + TUI concurrently
        await asyncio.gather(
            self.discord_bot.start(token),
            self.tui.run_async(),
        )


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------

def main():
    orchestrator = BotOrchestrator()

    loop = asyncio.get_event_loop()

    # Graceful shutdown
    def shutdown():
        log.info("Shutting down...")
        orchestrator.polling_engine.stop()
        orchestrator.live_mode_engine.stop()
        orchestrator.live_summary_engine.stop()
        orchestrator.video_upload_engine.stop()
        orchestrator.daily_save_engine.stop()
        orchestrator.daily_summary_engine.stop()
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown)
        except:
            pass

    try:
        loop.run_until_complete(orchestrator.run())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
