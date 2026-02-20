import asyncio
import json
import shutil
import subprocess

from config.config_manager import ConfigManager
from utils.logger import log


class BatteryMonitor:
    def __init__(self, config_manager: ConfigManager, discord_client):
        self.config_manager = config_manager
        self.discord_client = discord_client
        self._running = True
        self._last_level = None

    async def run(self):
        await self.discord_client.wait_until_ready()
        while self._running:
            if not self.config_manager.config["features"].get("battery_warnings", True):
                await asyncio.sleep(300)
                continue

            if shutil.which("termux-battery-status") is None:
                await asyncio.sleep(600)
                continue

            try:
                out = subprocess.check_output(["termux-battery-status"])
                data = json.loads(out.decode("utf-8"))
                level = int(data.get("percentage", 100))
            except Exception as e:
                log.warning(f"Battery monitor error: {e}")
                await asyncio.sleep(300)
                continue

            if self._last_level is None:
                self._last_level = level

            if level <= 10 and (self._last_level is None or self._last_level > 10):
                log.warning(f"Battery critical: {level}%")
            elif level <= 20 and (self._last_level is None or self._last_level > 20):
                log.warning(f"Battery low: {level}%")

            self._last_level = level
            await asyncio.sleep(300)

    async def stop(self):
        self._running = False
