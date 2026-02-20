class InputHandler:
    def __init__(self, console_commands) -> None:
        self.console_commands = console_commands

    def handle_line(self, line: str) -> str:
        return self.console_commands.handle(line)
