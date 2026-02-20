import time
from typing import Callable
from functools import wraps

import discord
from discord import app_commands

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from config.defaults import (
    MIN_OFFLINE_INTERVAL,
    MIN_LIVE_SUMMARY_INTERVAL,
    MIN_VIDEO_INTERVAL,
)
from discord_bot.permissions import is_admin
from discord_bot.admin_roles import add_admin_role, remove_admin_role
from utils.logger import log


def _is_disabled(config, name: str) -> bool:
    return name in config.get("disabled_slash_commands", [])


async def setup_slash_commands(
    tree: app_commands.CommandTree,
    client: discord.Client,
    config_manager: ConfigManager,
    feature_flags: FeatureFlags,
    polling_engine,
    live_summary_engine,
    final_summary_engine,
    video_upload_engine,
    daily_summary_engine,
    uptime,
):
    cfg = config_manager.config

    async def guard(interaction: discord.Interaction, cmd_name: str) -> bool:
        if _is_disabled(cfg, cmd_name):
            await interaction.response.send_message(
                "This command is disabled by the administrator.",
                ephemeral=True,
            )
            return False
        return True

    def admin_only(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
                await interaction.response.send_message(
                    "You are not an admin.", ephemeral=True
                )
                return
            return await func(interaction, *args, **kwargs)

        return wrapper

    class AdminGroup(app_commands.Group, name="admin"):
        pass

    admin_group = AdminGroup()

    @admin_group.command(name="addrole", description="Add an admin role")
    @admin_only
    async def addrole_cmd(interaction: discord.Interaction, role: discord.Role):
        add_admin_role(config_manager, role.id)
        await interaction.response.send_message(
            f"Added admin role: {role.name}", ephemeral=True
        )

    @admin_group.command(name="removerole", description="Remove an admin role")
    @admin_only
    async def removerole_cmd(interaction: discord.Interaction, role: discord.Role):
        remove_admin_role(config_manager, role.id)
        await interaction.response.send_message(
            f"Removed admin role: {role.name}", ephemeral=True
        )

    tree.add_command(admin_group)

    @tree.command(name="ping", description="Ping the bot")
    async def ping(interaction: discord.Interaction):
        if not await guard(interaction, "ping"):
            return
        before = time.time()
        await interaction.response.send_message("Pinging...", ephemeral=True)
        after = time.time()
        ms = int((after - before) * 1000)
        await interaction.edit_original_response(content=f"Pong! {ms}ms")

    @tree.command(name="uptime", description="Show bot uptime")
    async def uptime_cmd(interaction: discord.Interaction):
        if not await guard(interaction, "uptime"):
            return
        await interaction.response.send_message(
            f"Uptime: {uptime.get_uptime_str()}", ephemeral=True
        )

    @tree.command(name="status", description="Show bot status")
    async def status(interaction: discord.Interaction):
        if not await guard(interaction, "status"):
            return
        maint = cfg.get("maintenance_mode", False)
        ttu = cfg.get("tiktok_username", "") or "<not set>"
        await interaction.response.send_message(
            f"Bot is running.\nMaintenance: {maint}\nTikTok: @{ttu}",
            ephemeral=True,
        )

    @tree.command(name="maintenance", description="Toggle maintenance mode")
    @admin_only
    async def maintenance_cmd(interaction: discord.Interaction, enabled: bool):
        if not await guard(interaction, "maintenance"):
            return
        feature_flags.set_maintenance(enabled)
        config_manager.save_config()
        await interaction.response.send_message(
            f"Maintenance mode set to {enabled}.", ephemeral=True
        )

    @tree.command(name="settiktok", description="Set TikTok username")
    @admin_only
    async def settiktok_cmd(interaction: discord.Interaction, username: str):
        if not await guard(interaction, "settiktok"):
            return
        cfg["tiktok_username"] = username
        config_manager.save_config()
        await interaction.response.send_message(
            f"TikTok username set to @{username}.", ephemeral=True
        )

    @tree.command(
        name="setofflineinterval", description="Set offline polling interval (minutes)"
    )
    @admin_only
    async def setofflineinterval_cmd(interaction: discord.Interaction, minutes: int):
        if not await guard(interaction, "setofflineinterval"):
            return
        if minutes < MIN_OFFLINE_INTERVAL:
            await interaction.response.send_message(
                f"Minimum offline interval is {MIN_OFFLINE_INTERVAL} minutes.",
                ephemeral=True,
            )
            return
        cfg["intervals"]["offline"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(
            f"Offline interval set to {minutes} minutes.", ephemeral=True
        )

    @tree.command(
        name="setlivesummaryinterval",
        description="Set live summary interval (minutes)",
    )
    @admin_only
    async def setlivesummaryinterval_cmd(
        interaction: discord.Interaction, minutes: int
    ):
        if not await guard(interaction, "setlivesummaryinterval"):
            return
        if minutes < MIN_LIVE_SUMMARY_INTERVAL:
            await interaction.response.send_message(
                f"Minimum live summary interval is {MIN_LIVE_SUMMARY_INTERVAL} minutes.",
                ephemeral=True,
            )
            return
        cfg["intervals"]["live_summary"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(
            f"Live summary interval set to {minutes} minutes.", ephemeral=True
        )

    @tree.command(
        name="setvideointerval", description="Set video check interval (minutes)"
    )
    @admin_only
    async def setvideointerval_cmd(interaction: discord.Interaction, minutes: int):
        if not await guard(interaction, "setvideointerval"):
            return
        if minutes < MIN_VIDEO_INTERVAL:
            await interaction.response.send_message(
                f"Minimum video interval is {MIN_VIDEO_INTERVAL} minutes.",
                ephemeral=True,
            )
            return
        cfg["intervals"]["video"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(
            f"Video interval set to {minutes} minutes.", ephemeral=True
        )

    @tree.command(
        name="setdailysaveinterval",
        description="Set daily stats save interval (minutes)",
    )
    @admin_only
    async def setdailysaveinterval_cmd(
        interaction: discord.Interaction, minutes: int
    ):
        if not await guard(interaction, "setdailysaveinterval"):
            return
        cfg["intervals"]["daily"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(
            f"Daily save interval set to {minutes} minutes.", ephemeral=True
        )

    @tree.command(
        name="setdailysummarytime",
        description="Set daily summary time (GMT, HH:MM)",
    )
    @admin_only
    async def setdailysummarytime_cmd(
        interaction: discord.Interaction, time_str: str
    ):
        if not await guard(interaction, "setdailysummarytime"):
            return
        cfg.setdefault("daily_summary", {})["time_gmt"] = time_str
        config_manager.save_config()
        await interaction.response.send_message(
            f"Daily summary time set to {time_str} GMT.", ephemeral=True
        )

    @tree.command(name="feature", description="Toggle a feature on or off")
    @admin_only
    async def feature_cmd(
        interaction: discord.Interaction,
        name: str,
        enabled: bool,
    ):
        if not await guard(interaction, "feature"):
            return
        feature_flags.set_flag(name, enabled)
        config_manager.save_config()
        await interaction.response.send_message(
            f"Feature `{name}` set to {enabled}.", ephemeral=True
        )

    @tree.command(name="setchannel", description="Set a channel for a feature")
    @admin_only
    async def setchannel_cmd(
        interaction: discord.Interaction,
        feature_name: str,
        channel: discord.TextChannel,
    ):
        if not await guard(interaction, "setchannel"):
            return
        cfg["channels"][feature_name] = channel.id
        config_manager.save_config()
        await interaction.response.send_message(
            f"Channel for `{feature_name}` set to {channel.mention}.",
            ephemeral=True,
        )

    @tree.command(name="setrole", description="Set a role for a feature")
    @admin_only
    async def setrole_cmd(
        interaction: discord.Interaction,
        feature_name: str,
        role: discord.Role,
    ):
        if not await guard(interaction, "setrole"):
            return
        cfg["roles"][feature_name] = role.id
        config_manager.save_config()
        await interaction.response.send_message(
            f"Role for `{feature_name}` set to {role.mention}.",
            ephemeral=True,
        )

    log.info("Slash commands registered (sync will happen in on_ready).")
