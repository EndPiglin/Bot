import asyncio
import aiohttp
import json
import re
from utils.logger import log


class TikTokAPI:
    """
    TikTok LIVE detector using TikTok's public web API.
    No API keys, no TikTokLive library, no rate limits.
    Works on Termux.
    """

    def __init__(self, username: str, retry_interval: int = 10):
        self.username = username.lstrip("@")
        self.retry_interval = retry_interval

        # Live state
        self.is_live = False
        self.live_title = None
        self.room_id = None
        self.viewer_count = 0
        self.thumbnail = None

    # ----------------------------------------------------------------------
    # INTERNAL: Fetch TikTok profile HTML
    # ----------------------------------------------------------------------
    async def _fetch_profile_html(self):
        url = f"https://www.tiktok.com/@{self.username}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; Mobile) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36"
            )
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    return await resp.text()
        except Exception as e:
            log.error(f"[TikTokAPI] Failed to fetch profile HTML: {e}")
            return None

    # ----------------------------------------------------------------------
    # INTERNAL: Extract JSON data from HTML
    # ----------------------------------------------------------------------
    def _extract_json(self, html: str):
        """
        TikTok embeds JSON inside <script id="SIGI_STATE"> ... </script>
        """
        try:
            match = re.search(
                r'<script id="SIGI_STATE"[^>]*>(.*?)</script>',
                html,
                re.DOTALL,
            )
            if not match:
                return None

            raw_json = match.group(1)
            return json.loads(raw_json)
        except Exception:
            return None

    # ----------------------------------------------------------------------
    # PUBLIC: Detect live status
    # ----------------------------------------------------------------------
    async def fetch_live_status(self):
        """
        Returns:
            {
                "is_live": bool,
                "viewer_count": int,
                "title": str,
                "room_id": str,
                "thumbnail": str
            }
        """

        html = await self._fetch_profile_html()
        if not html:
            return {"is_live": False}

        data = self._extract_json(html)
        if not data:
            return {"is_live": False}

        # TikTok stores live info under UserModule -> users -> username
        try:
            user_data = data["UserModule"]["users"][self.username]
        except KeyError:
            return {"is_live": False}

        # LIVE detection
        is_live = user_data.get("isLive", False)

        if not is_live:
            # Reset state
            self.is_live = False
            self.room_id = None
            self.live_title = None
            self.viewer_count = 0
            self.thumbnail = None

            return {"is_live": False}

        # Extract live metadata
        room_id = user_data.get("liveRoomId")
        title = user_data.get("liveTitle") or "TikTok LIVE"
        thumbnail = user_data.get("coverUrl")
        viewer_count = user_data.get("liveViewerCount", 0)

        # Update internal state
        self.is_live = True
        self.room_id = room_id
        self.live_title = title
        self.thumbnail = thumbnail
        self.viewer_count = viewer_count

        return {
            "is_live": True,
            "viewer_count": viewer_count,
            "title": title,
            "room_id": room_id,
            "thumbnail": thumbnail,
        }

    # ----------------------------------------------------------------------
    # PUBLIC: Fetch profile stats (followers, likes)
    # ----------------------------------------------------------------------
    async def fetch_profile_stats(self):
        html = await self._fetch_profile_html()
        if not html:
            return {"followers": 0, "likes": 0, "views": 0}

        data = self._extract_json(html)
        if not data:
            return {"followers": 0, "likes": 0, "views": 0}

        try:
            stats = data["UserModule"]["stats"][self.username]
            return {
                "followers": stats.get("followerCount", 0),
                "likes": stats.get("heartCount", 0),
                "views": stats.get("videoCount", 0),
            }
        except KeyError:
            return {"followers": 0, "likes": 0, "views": 0}

    # ----------------------------------------------------------------------
    # Dummy listener (kept for compatibility)
    # ----------------------------------------------------------------------
    async def start_live_listener(self):
        """
        TikTokLive replacement.
        Does nothing, but keeps compatibility with your orchestrator.
        """
        log.info("[TikTokAPI] start_live_listener() is not needed in Web-Polling mode.")
        while True:
            await asyncio.sleep(3600)
