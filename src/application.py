"""Интерактивный цикл и обработка команд эмулятора оболочки."""

from collections.abc import Callable
import getpass
import socket

from src.command_parser import parse_command
from src.vfs import VirtualFileSystem


CommandHandler = Callable[[str, list[str]], str]


class ShellApplication:
    """Минимальный интерактивный эмулятор оболочки."""

    def __init__(self, vfs: VirtualFileSystem | None = None) -> None:
        """Инициализирует обработчики команд и состояние приложения."""
        self._is_running = True
        self._vfs = vfs
        self._handlers: dict[str, CommandHandler] = {
            "ls": self._handle_stub,
            "cd": self._handle_stub,
            "vfs-info": self._handle_vfs_info,
        }

    def run(self) -> None:
        """Запускает REPL до команды exit или конца ввода."""
        while self._is_running:
            try:
                line = input(self.prompt)
            except EOFError:
                break
            output = self.execute(line)
            if output:
                print(output)

    def run_script(self, script_path: str) -> None:
        """Выполняет команды из текстового сценария."""
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
        """Создаёт приглашение из данных текущей операционной системы."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        return f"{username}@{hostname}:~$ "

    def execute(self, line: str) -> str:
        """Выполняет одну строку команды."""
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

    def _handle_vfs_info(
        self,
        command_name: str,
        arguments: list[str],
    ) -> str:
        """Выводит имя и SHA-256 загруженной VFS."""
        del command_name
        if arguments:
            return "vfs-info: команда не принимает аргументы"
        if self._vfs is None:
            return "vfs-info: VFS не загружена"
        return f"VFS: {self._vfs.name}\nSHA-256: {self._vfs.source_hash}"

    def _handle_stub(self, command_name: str, arguments: list[str]) -> str:
        """Возвращает имя и аргументы команды-заглушки."""
        arguments_text = " ".join(arguments) or "(none)"
        return f"{command_name}: arguments: {arguments_text}"

    def _handle_exit(self, arguments: list[str]) -> str:
        """Останавливает REPL, если exit передан без аргументов."""
        if arguments:
            return "exit: too many arguments"
        self._is_running = False
        return ""