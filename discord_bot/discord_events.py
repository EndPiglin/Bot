import asyncio
import discord
from utils.logger import log


def setup_discord_events(
    client,
    config_manager,
    feature_flags,
    uptime,
    shutdown_event,
    app,
):
    @client.event
    async def on_ready():
        log.info(f"Logged in as {client.user} (ID: {client.user.id})")

        # Sync slash commands HERE
        try:
            await client.tree.sync()
            log.info("Slash commands synced successfully.")
        except Exception as e:
            log.error(f"Failed to sync slash commands: {e}")

        uptime.mark_start()
        await app.start_background_tasks()

    @client.event
    async def on_disconnect():
        log.warning("Discord disconnected.")

    @client.event
    async def on_resumed():
        log.info("Discord connection resumed.")
