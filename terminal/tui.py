from terminal.input_handler import TerminalUI


async def start_terminal_loop(
    config_manager,
    feature_flags,
    polling_engine,
    live_summary_engine,
    final_summary_engine,
    video_upload_engine,
    daily_summary_engine,
    uptime,
    app,
):
    ui = TerminalUI(
        config_manager=config_manager,
        feature_flags=feature_flags,
        polling_engine=polling_engine,
        live_summary_engine=live_summary_engine,
        final_summary_engine=final_summary_engine,
        video_upload_engine=video_upload_engine,
        daily_summary_engine=daily_summary_engine,
        uptime=uptime,
        app=app,
    )
    await ui.loop()
