import json
import re
from typing import Optional, Dict, Any, List

import aiohttp
from bs4 import BeautifulSoup

from utils.logger import log


class TikTokAPI:
    """
    Hybrid scraping:
    - Primary: parse SIGI_STATE JSON from HTML
    - Fallback: regex scraping
    """

    def __init__(self, username: str):
        self.username = username
        self.base_url = f"https://www.tiktok.com/@{username}"

    # ----------------------------------------------------------------------
    # HTML fetch
    # ----------------------------------------------------------------------
    async def _fetch_html(self) -> Optional[str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile)",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, headers=headers, timeout=15) as resp:
                    if resp.status != 200:
                        log.warning(f"TikTokAPI: status {resp.status} for {self.base_url}")
                        return None
                    return await resp.text()
        except Exception as e:
            log.warning(f"TikTokAPI: error fetching HTML: {e}")
            return None

    # ----------------------------------------------------------------------
    # SIGI_STATE parsing
    # ----------------------------------------------------------------------
    def _parse_sigi_state(self, html: str) -> Optional[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="SIGI_STATE")
        if not script or not script.string:
            return None
        try:
            return json.loads(script.string)
        except Exception as e:
            log.warning(f"TikTokAPI: error parsing SIGI_STATE JSON: {e}")
            return None

    def _extract_from_sigi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "followers": None,
            "likes": None,
            "views": None,
            "is_live": False,
            "videos": [],
        }

        # Followers / Likes
        try:
            user_module = data.get("UserModule", {})
            users = user_module.get("users", {})
            stats = user_module.get("stats", {})
            if users:
                user_key = next(iter(users.keys()))
                user_stats = stats.get(user_key, {})
                result["followers"] = user_stats.get("followerCount")
                result["likes"] = user_stats.get("heartCount")
        except Exception:
            pass

        # Live detection
        try:
            live_room = data.get("LiveRoom", {})
            if live_room and live_room.get("status") == 1:
                result["is_live"] = True
        except Exception:
            pass

        # Videos
        try:
            item_module = data.get("ItemModule", {})
            videos = []
            for vid_id, item in item_module.items():
                videos.append(
                    {
                        "id": vid_id,
                        "url": f"{self.base_url}/video/{vid_id}",
                        "playCount": item.get("stats", {}).get("playCount"),
                        "diggCount": item.get("stats", {}).get("diggCount"),
                        "desc": item.get("desc", ""),
                    }
                )
            videos.sort(key=lambda v: v.get("playCount") or 0, reverse=True)
            result["videos"] = videos
            result["views"] = sum(v.get("playCount") or 0 for v in videos)
        except Exception:
            pass

        return result

    # ----------------------------------------------------------------------
    # Fallback regex
    # ----------------------------------------------------------------------
    def _fallback_regex(self, html: str) -> Dict[str, Any]:
        result = {
            "followers": None,
            "likes": None,
            "views": None,
            "is_live": False,
            "videos": [],
        }

        try:
            m = re.search(r'"followerCount":(\d+)', html)
            if m:
                result["followers"] = int(m.group(1))
        except Exception:
            pass

        try:
            m = re.search(r'"heartCount":(\d+)', html)
            if m:
                result["likes"] = int(m.group(1))
        except Exception:
            pass

        try:
            m = re.search(r'"videoId":"(.*?)"', html)
            if m:
                vid_id = m.group(1)
                result["videos"] = [{"id": vid_id, "url": f"{self.base_url}/video/{vid_id}"}]
        except Exception:
            pass

        return result

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    async def get_profile_stats(self) -> Optional[Dict[str, Any]]:
        html = await self._fetch_html()
        if not html:
            return None

        data = self._parse_sigi_state(html)
        if data:
            return self._extract_from_sigi(data)
        return self._fallback_regex(html)

    async def get_latest_video(self) -> Optional[Dict[str, Any]]:
        stats = await self.get_profile_stats()
        if not stats:
            return None
        videos = stats.get("videos") or []
        return videos[0] if videos else None

    async def get_daily_stats(self) -> Optional[Dict[str, Any]]:
        stats = await self.get_profile_stats()
        if not stats:
            return None
        return {
            "followers": stats.get("followers"),
            "likes": stats.get("likes"),
            "views": stats.get("views"),
        }

    # ----------------------------------------------------------------------
    # Engine compatibility wrappers
    # ----------------------------------------------------------------------
    async def fetch_profile_stats(self):
        return await self.get_profile_stats()

    async def fetch_live_status(self):
        stats = await self.get_profile_stats()
        if not stats:
            return None

        return {
            "is_live": stats.get("is_live", False),
            "viewer_count": 0,  # TikTok web does not expose this
            "likes": stats.get("likes"),
            "followers": stats.get("followers"),
        }
