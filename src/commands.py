"""Основные команды эмулятора UNIX-подобной оболочки."""

from pathlib import PurePosixPath

from src.vfs import VfsError, VfsNode, VirtualFileSystem


DEFAULT_HEAD_LINES = 10
EMULATOR_NAME = "Shell Emulator"
EMULATOR_DETAILS = "Shell Emulator Windows Python"


class CommandExecutor:
    """Выполняет команды, работающие с виртуальной файловой системой."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        """Создаёт исполнитель команд для переданной VFS."""
        self._vfs = vfs
        self.current_path = "/"

    def ls(self, arguments: list[str]) -> str:
        """Выводит содержимое текущего или указанного каталога."""
        if len(arguments) > 1:
            return "ls: слишком много аргументов"
        target_path = arguments[0] if arguments else "."
        try:
            node = self._get_node(target_path)
        except VfsError as error:
            return f"ls: {error}"
        if not node.is_directory:
            return node.name
        return "  ".join(sorted(node.children))

    def cd(self, arguments: list[str]) -> str:
        """Переходит в каталог виртуальной файловой системы."""
        if len(arguments) > 1:
            return "cd: слишком много аргументов"
        target_path = arguments[0] if arguments else "/"
        try:
            normalized_path = self._normalize_path(target_path)
            node = self._vfs.get_node(str(normalized_path))
        except VfsError as error:
            return f"cd: {error}"
        if not node.is_directory:
            return f"cd: не каталог: {normalized_path}"
        self.current_path = str(normalized_path)
        return ""

    def rev(self, arguments: list[str]) -> str:
        """Переворачивает символы в каждой строке текстового файла."""
        if len(arguments) != 1:
            return "rev: требуется один путь к файлу"
        try:
            content = self._read_text_file(arguments[0])
        except VfsError as error:
            return f"rev: {error}"
        return "\n".join(line[::-1] for line in content.splitlines())

    def uname(self, arguments: list[str]) -> str:
        """Выводит имя эмулятора или расширенные сведения."""
        if not arguments:
            return EMULATOR_NAME
        if arguments == ["-a"]:
            return EMULATOR_DETAILS
        return "uname: неподдерживаемый параметр"

    def head(self, arguments: list[str]) -> str:
        """Выводит первые строки текстового файла."""
        line_count, file_path = self._parse_head_arguments(arguments)
        if file_path is None:
            return "head: требуется путь к файлу"
        if line_count is None:
            return "head: неверное число строк"
        try:
            content = self._read_text_file(file_path)
        except VfsError as error:
            return f"head: {error}"
        return "\n".join(content.splitlines()[:line_count])

    def _parse_head_arguments(
        self,
        arguments: list[str],
    ) -> tuple[int | None, str | None]:
        """Разбирает аргументы команды head."""
        if len(arguments) == 1:
            return DEFAULT_HEAD_LINES, arguments[0]
        if len(arguments) != 3:
            return None, None
        if arguments[0] not in {"-n", "--lines"}:
            return None, None
        try:
            line_count = int(arguments[1])
        except ValueError:
            return None, arguments[2]
        if line_count < 0:
            return None, arguments[2]
        return line_count, arguments[2]

    def _get_node(self, path: str) -> VfsNode:
        """Возвращает узел относительно текущего каталога."""
        return self._vfs.get_node(path, self.current_path)

    def _normalize_path(self, path: str) -> PurePosixPath:
        """Возвращает абсолютный нормализованный путь VFS."""
        return self._vfs.normalize_path(path, self.current_path)

    def _read_text_file(self, path: str) -> str:
        """Читает текстовый файл VFS в кодировке UTF-8."""
        node = self._get_node(path)
        if node.is_directory:
            raise VfsError(f"это каталог: {path}")
        try:
            return node.content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise VfsError(f"не текстовый файл: {path}") from error