import discord


def basic_status_embed(tiktok_username: str, maintenance: bool) -> discord.Embed:
    e = discord.Embed(
        title="Bot status",
        description=f"TikTok: @{tiktok_username or '<not set>'}",
        color=discord.Color.blurple(),
    )
    e.add_field(name="Maintenance", value=str(maintenance))
    return e
