"""Интерактивный цикл и обработка команд эмулятора."""

from collections.abc import Callable
import getpass
import socket

from src.command_parser import parse_command

CommandHandler = Callable[[str, list[str]], str]


class ShellApplication:
    """Минимальный интерактивный эмулятор оболочки."""

    def __init__(self) -> None:
        """Инициализирует обработчики доступных команд."""
        self._is_running = True
        self._handlers: dict[str, CommandHandler] = {
            "ls": self._handle_stub,
            "cd": self._handle_stub,
        }

    def run(self) -> None:
        """Запускает REPL до exit или конца ввода."""
        while self._is_running:
            try:
                line = input(self.prompt)
            except EOFError:
                break
            output = self.execute(line)
            if output:
                print(output)

    @property
    def prompt(self) -> str:
        """Формирует приглашение из данных реальной ОС."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        return f"{username}@{hostname}:~$ "

    def execute(self, line: str) -> str:
        """Выполняет одну строку пользовательского ввода."""
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
        """Возвращает результат выполнения команды-заглушки."""
        arguments_text = " ".join(arguments) or "(none)"
        return f"{command_name}: arguments: {arguments_text}"

    def _handle_exit(self, arguments: list[str]) -> str:
        """Останавливает REPL, если команда не содержит аргументов."""
        if arguments:
            return "exit: too many arguments"
        self._is_running = False
        return ""
