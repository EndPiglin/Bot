import asyncio
from utils.logger import log


class VideoUploadEngine:
    def __init__(self, cfg_mgr, tiktok_client, interval_minutes: int):
        self.cfg_mgr = cfg_mgr
        self.client = tiktok_client
        self.interval = interval_minutes
        self.running = False
        self.last_video_id = None
        self.on_new_video = None  # callback

    async def start(self):
        self.running = True
        log.info("VideoUploadEngine started.")

        while self.running:
            profile = await self.client.fetch_profile_stats()
            if profile:
                # TODO: replace with real video ID detection
                video_id = profile.get("latest_video_id")
                if video_id and video_id != self.last_video_id:
                    self.last_video_id = video_id
                    if self.on_new_video:
                        await self.on_new_video(video_id)
            await asyncio.sleep(self.interval * 60)

    def stop(self):
        self.running = False
