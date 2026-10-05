"""Interactive loop and command handling for the shell emulator."""

from collections.abc import Callable
import getpass
import socket

from src.command_parser import parse_command

CommandHandler = Callable[[str, list[str]], str]


class ShellApplication:
    """Minimal interactive shell emulator."""

    def __init__(self) -> None:
        """Initialize command handlers and the application state."""
        self._is_running = True
        self._handlers: dict[str, CommandHandler] = {
            "ls": self._handle_stub,
            "cd": self._handle_stub,
        }

    def run(self) -> None:
        """Run the REPL until exit or end of input."""
        while self._is_running:
            try:
                line = input(self.prompt)
            except EOFError:
                break
            output = self.execute(line)
            if output:
                print(output)

    def run_script(self, script_path: str) -> None:
        """Run commands from a text file and continue after errors."""
        try:
            with open(script_path, encoding="utf-8") as script_file:
                lines = script_file.readlines()
        except OSError as error:
            print(f"script error: {error}")
            return
        for line in lines:
            command_line = line.strip()
            if not command_line or command_line.startswith("#"):
                continue
            print(f"{self.prompt}{command_line}")
            output = self.execute(command_line)
            if output:
                print(output)
            if not self._is_running:
                break

    @property
    def prompt(self) -> str:
        """Build a prompt from the current operating system data."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        return f"{username}@{hostname}:~$ "

    def execute(self, line: str) -> str:
        """Execute one command line entered by the user."""
        try:
            command_name, arguments = parse_command(line)
        except ValueError as error:
            return f"parse error: {error}"
        if not command_name:
            return ""
        if command_name == "exit":
            return self._handle_exit(arguments)
        handler = self._handlers.get(command_name)
        if handler is None:
            return f"command not found: {command_name}"
        return handler(command_name, arguments)

    def _handle_stub(self, command_name: str, arguments: list[str]) -> str:
        """Return the name and arguments of a stub command."""
        arguments_text = " ".join(arguments) or "(none)"
        return f"{command_name}: arguments: {arguments_text}"

    def _handle_exit(self, arguments: list[str]) -> str:
        """Stop the REPL when exit has no arguments."""
        if arguments:
            return "exit: too many arguments"
        self._is_running = False
        return ""
