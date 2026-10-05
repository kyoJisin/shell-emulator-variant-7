"""Интерактивный цикл и обработка команд эмулятора оболочки."""

from collections.abc import Callable
import getpass
import socket

from src.command_parser import parse_command
from src.commands import CommandExecutor
from src.vfs import VirtualFileSystem


CommandHandler = Callable[[str, list[str]], str]


class ShellApplication:
    """Интерактивный эмулятор UNIX-подобной оболочки."""

    def __init__(self, vfs: VirtualFileSystem | None = None) -> None:
        """Инициализирует обработчики команд и состояние приложения."""
        self._is_running = True
        self._vfs = vfs
        self._executor = CommandExecutor(vfs) if vfs else None
        self._handlers: dict[str, CommandHandler] = {
            "ls": self._handle_ls,
            "cd": self._handle_cd,
            "rev": self._handle_rev,
            "uname": self._handle_uname,
            "head": self._handle_head,
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
        """Создаёт приглашение из данных ОС и текущего каталога VFS."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        current_path = self._current_path()
        return f"{username}@{hostname}:{current_path}$ "

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

    def _current_path(self) -> str:
        """Возвращает текущий путь VFS или домашний символ без VFS."""
        if self._executor is None:
            return "~"
        return self._executor.current_path

    def _handle_ls(self, _: str, arguments: list[str]) -> str:
        """Выполняет ls или сообщает, что VFS не загружена."""
        if self._executor is None:
            return "ls: VFS не загружена"
        return self._executor.ls(arguments)

    def _handle_cd(self, _: str, arguments: list[str]) -> str:
        """Выполняет cd или сообщает, что VFS не загружена."""
        if self._executor is None:
            return "cd: VFS не загружена"
        return self._executor.cd(arguments)

    def _handle_rev(self, _: str, arguments: list[str]) -> str:
        """Выполняет rev или сообщает, что VFS не загружена."""
        if self._executor is None:
            return "rev: VFS не загружена"
        return self._executor.rev(arguments)

    def _handle_uname(self, _: str, arguments: list[str]) -> str:
        """Выполняет uname без требования загруженной VFS."""
        if self._executor is None:
            if not arguments:
                return "Shell Emulator"
            if arguments == ["-a"]:
                return "Shell Emulator Windows Python"
            return "uname: неподдерживаемый параметр"
        return self._executor.uname(arguments)

    def _handle_head(self, _: str, arguments: list[str]) -> str:
        """Выполняет head или сообщает, что VFS не загружена."""
        if self._executor is None:
            return "head: VFS не загружена"
        return self._executor.head(arguments)

    def _handle_vfs_info(self, _: str, arguments: list[str]) -> str:
        """Выводит имя и SHA-256 загруженной VFS."""
        if arguments:
            return "vfs-info: команда не принимает аргументы"
        if self._vfs is None:
            return "vfs-info: VFS не загружена"
        return f"VFS: {self._vfs.name}\nSHA-256: {self._vfs.source_hash}"

    def _handle_exit(self, arguments: list[str]) -> str:
        """Останавливает REPL, если exit передан без аргументов."""
        if arguments:
            return "exit: too many arguments"
        self._is_running = False
        return ""