from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from terminal.decorations import banner
from terminal.status_bar import StatusBar
from terminal.log_window import LogWindow
from terminal.console_commands import ConsoleCommands


class TerminalUI:
    def __init__(
        self,
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
        self.session = PromptSession()
        self.status_bar = StatusBar(config_manager, uptime)
        self.log_window = LogWindow()
        self.commands = ConsoleCommands(
            config_manager=config_manager,
            feature_flags=feature_flags,
            polling_engine=polling_engine,
            live_summary_engine=live_summary_engine,
            final_summary_engine=final_summary_engine,
            video_upload_engine=video_upload_engine,
            daily_summary_engine=daily_summary_engine,
            uptime=uptime,
            log_window=self.log_window,
            app=app,
        )
        self.app = app

    async def loop(self):
        self.log_window.add("Terminal started. Type 'help' for commands.")

        with patch_stdout():
            while True:
                print()
                print(banner("TikTok Monitor Console"))
                print(self.status_bar.get_status_line())
                print("-" * 40)
                print(self.log_window.render())
                print("-" * 40)

                cmd = await self.session.prompt_async("> ")
                cmd = cmd.strip()

                result = self.commands.handle(cmd)

                if result == "__EXIT__":
                    self.log_window.add("Terminal loop exited.")
                    break

                if result == "__SHUTDOWN__":
                    self.log_window.add("Full shutdown requested.")
                    await self.app.stop()
                    break

                if result:
                    self.log_window.add(result)
