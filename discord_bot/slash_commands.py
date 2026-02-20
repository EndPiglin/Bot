import time

import discord
from discord import app_commands

from config.config_manager import ConfigManager
from config.feature_flags import FeatureFlags
from config.defaults import MIN_OFFLINE_INTERVAL, MIN_LIVE_SUMMARY_INTERVAL, MIN_VIDEO_INTERVAL
from discord_bot.permissions import is_admin
from discord_bot.admin_roles import add_admin_role, remove_admin_role
from utils.logger import log


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

    class AdminGroup(app_commands.Group, name="admin"):
        pass

    admin_group = AdminGroup()

    @admin_group.command(name="addrole", description="Add an admin role")
    async def addrole(interaction: discord.Interaction, role: discord.Role):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        add_admin_role(config_manager, role.id)
        await interaction.response.send_message(f"Added admin role: {role.name}", ephemeral=True)

    @admin_group.command(name="removerole", description="Remove an admin role")
    async def removerole(interaction: discord.Interaction, role: discord.Role):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        remove_admin_role(config_manager, role.id)
        await interaction.response.send_message(f"Removed admin role: {role.name}", ephemeral=True)

    tree.add_command(admin_group)

    @tree.command(name="ping", description="Ping the bot")
    async def ping(interaction: discord.Interaction):
        before = time.time()
        await interaction.response.send_message("Pinging...", ephemeral=True)
        after = time.time()
        ms = int((after - before) * 1000)
        await interaction.edit_original_response(content=f"Pong! {ms}ms")

    @tree.command(name="uptime", description="Show bot uptime")
    async def uptime_cmd(interaction: discord.Interaction):
        await interaction.response.send_message(f"Uptime: {uptime.get_uptime_str()}", ephemeral=True)

    @tree.command(name="status", description="Show bot status")
    async def status(interaction: discord.Interaction):
        maint = cfg.get("maintenance_mode", False)
        await interaction.response.send_message(
            f"Bot is running. Maintenance: {maint}. TikTok: @{cfg.get('tiktok_username','') or '<not set>'}",
            ephemeral=True,
        )

    @tree.command(name="maintenance", description="Toggle maintenance mode")
    async def maintenance(interaction: discord.Interaction, enabled: bool):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        feature_flags.set_maintenance(enabled)
        config_manager.save_config()
        await interaction.response.send_message(f"Maintenance mode set to {enabled}.", ephemeral=True)

    @tree.command(name="settiktok", description="Set TikTok username")
    async def settiktok(interaction: discord.Interaction, username: str):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        cfg["tiktok_username"] = username
        config_manager.save_config()
        await interaction.response.send_message(f"TikTok username set to @{username}.", ephemeral=True)

    @tree.command(name="setofflineinterval", description="Set offline polling interval (minutes)")
    async def setofflineinterval(interaction: discord.Interaction, minutes: int):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        if minutes < MIN_OFFLINE_INTERVAL:
            await interaction.response.send_message(
                f"Minimum offline interval is {MIN_OFFLINE_INTERVAL} minutes.", ephemeral=True
            )
            return
        cfg["intervals"]["offline"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(f"Offline interval set to {minutes} minutes.", ephemeral=True)

    @tree.command(name="setlivesummaryinterval", description="Set live summary interval (minutes)")
    async def setlivesummaryinterval(interaction: discord.Interaction, minutes: int):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        if minutes < MIN_LIVE_SUMMARY_INTERVAL:
            await interaction.response.send_message(
                f"Minimum live summary interval is {MIN_LIVE_SUMMARY_INTERVAL} minutes.", ephemeral=True
            )
            return
        cfg["intervals"]["live_summary"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(f"Live summary interval set to {minutes} minutes.", ephemeral=True)

    @tree.command(name="setvideointerval", description="Set video check interval (minutes)")
    async def setvideointerval(interaction: discord.Interaction, minutes: int):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        if minutes < MIN_VIDEO_INTERVAL:
            await interaction.response.send_message(
                f"Minimum video interval is {MIN_VIDEO_INTERVAL} minutes.", ephemeral=True
            )
            return
        cfg["intervals"]["video"] = minutes
        config_manager.save_config()
        await interaction.response.send_message(f"Video interval set to {minutes} minutes.", ephemeral=True)

    @tree.command(name="feature", description="Toggle a feature on or off")
    async def feature(
        interaction: discord.Interaction,
        name: str,
        enabled: bool,
    ):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        feature_flags.set_flag(name, enabled)
        config_manager.save_config()
        await interaction.response.send_message(f"Feature `{name}` set to {enabled}.", ephemeral=True)

    @tree.command(name="setchannel", description="Set a channel for a feature")
    async def setchannel(interaction: discord.Interaction, feature_name: str, channel: discord.TextChannel):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        cfg["channels"][feature_name] = channel.id
        config_manager.save_config()
        await interaction.response.send_message(
            f"Channel for `{feature_name}` set to {channel.mention}.", ephemeral=True
        )

    @tree.command(name="setrole", description="Set a role for a feature")
    async def setrole(interaction: discord.Interaction, feature_name: str, role: discord.Role):
        if not is_admin(interaction.user, cfg["admin_users"], cfg["admin_roles"]):
            await interaction.response.send_message("You are not an admin.", ephemeral=True)
            return
        cfg["roles"][feature_name] = role.id
        config_manager.save_config()
        await interaction.response.send_message(
            f"Role for `{feature_name}` set to {role.mention}.", ephemeral=True
        )

    # ❗ DO NOT SYNC HERE
    log.info("Slash commands registered (sync will happen in on_ready).")
