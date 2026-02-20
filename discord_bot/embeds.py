import discord
from datetime import timedelta


def _stream_url(username: str) -> str:
    return f"https://www.tiktok.com/@{username}/live"


def build_live_start_embed(username: str) -> discord.Embed:
    url = _stream_url(username)
    embed = discord.Embed(
        title="🔴 Stream Started",
        description=f"{username} is now live!\n[Watch here]({url})",
        color=discord.Color.red(),
    )
    embed.set_footer(text="TikTok Monitor")
    return embed


def build_live_summary_embed(username: str, duration_seconds: int, stats: dict) -> discord.Embed:
    url = _stream_url(username)
    duration = str(timedelta(seconds=duration_seconds))
    embed = discord.Embed(
        title="📊 Live Summary (Ongoing)",
        description=f"[Watch live]({url})",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Duration", value=duration, inline=False)
    embed.add_field(name="Viewers", value=str(stats.get("viewers", "?")), inline=True)
    embed.add_field(name="Peak Viewers", value=str(stats.get("peak_viewers", "?")), inline=True)
    embed.add_field(name="Likes", value=str(stats.get("likes", "?")), inline=True)
    embed.add_field(name="Gifts", value=str(stats.get("gifts", "?")), inline=True)
    embed.set_footer(text="TikTok Monitor")
    return embed


def build_final_summary_embed(username: str, duration_seconds: int, stats: dict) -> discord.Embed:
    url = f"https://www.tiktok.com/@{username}"
    duration = str(timedelta(seconds=duration_seconds))
    embed = discord.Embed(
        title="✅ Stream Ended — Final Summary",
        description=f"[Profile]({url})",
        color=discord.Color.green(),
    )
    embed.add_field(name="Duration", value=duration, inline=False)
    embed.add_field(name="Peak Viewers", value=str(stats.get("peak_viewers", "?")), inline=True)
    embed.add_field(name="Likes", value=str(stats.get("likes", "?")), inline=True)
    embed.add_field(name="Gifts", value=str(stats.get("gifts", "?")), inline=True)
    embed.set_footer(text="TikTok Monitor")
    return embed


def build_video_upload_embed(video: dict) -> discord.Embed:
    embed = discord.Embed(
        title="📹 New Video Uploaded",
        description=f"[Watch here]({video['url']})",
        color=discord.Color.purple(),
    )
    embed.add_field(name="Caption", value=video.get("desc", "No caption"), inline=False)
    embed.set_footer(text="TikTok Monitor")
    return embed


def build_daily_summary_embed(username: str, stats: dict) -> discord.Embed:
    embed = discord.Embed(
        title="📈 Daily Summary",
        description=f"TikTok: @{username}",
        color=discord.Color.gold(),
    )
    embed.add_field(name="Followers", value=str(stats.get("followers", "?")), inline=True)
    embed.add_field(name="Likes", value=str(stats.get("likes", "?")), inline=True)
    embed.add_field(name="Views", value=str(stats.get("views", '?')), inline=True)
    embed.set_footer(text="TikTok Monitor")
    return embed
