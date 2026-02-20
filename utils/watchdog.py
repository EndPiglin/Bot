import asyncio

from utils.logger import log


class Watchdog:
    def __init__(self):
        self.tasks = {}
        self._running = True

    def register_task(self, name: str, task: asyncio.Task):
        self.tasks[name] = task

    async def run(self):
        while self._running:
            for name, task in list(self.tasks.items()):
                if task.done():
                    log.warning(f"Task {name} has stopped.")
            await asyncio.sleep(30)

    async def stop_all(self):
        self._running = False
        for name, task in list(self.tasks.items()):
            if not task.done():
                task.cancel()
