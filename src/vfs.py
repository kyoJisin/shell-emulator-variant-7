"""Виртуальная файловая система, загружаемая из XML."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import PurePosixPath
import xml.etree.ElementTree as element_tree


ROOT_PATH = PurePosixPath("/")


class VfsError(ValueError):
    """Ошибка работы с виртуальной файловой системой."""


@dataclass
class VfsNode:
    """Узел виртуальной файловой системы."""

    name: str
    is_directory: bool
    content: bytes = b""
    owner: str = "root"
    children: dict[str, "VfsNode"] = field(default_factory=dict)

    def add_child(self, child: "VfsNode") -> None:
        """Добавляет дочерний узел в каталог."""
        if not self.is_directory:
            raise VfsError("нельзя добавить узел в файл")
        if child.name in self.children:
            raise VfsError(f"повторяющееся имя: {child.name}")
        self.children[child.name] = child


class VirtualFileSystem:
    """VFS, полностью хранящаяся в памяти процесса."""

    def __init__(self, name: str, source_data: bytes, root: VfsNode) -> None:
        """Создаёт загруженную VFS."""
        self.name = name
        self._source_hash = sha256(source_data).hexdigest()
        self.root = root

    @property
    def source_hash(self) -> str:
        """Возвращает SHA-256 исходного XML-файла."""
        return self._source_hash

    @classmethod
    def from_xml_file(cls, file_path: str) -> "VirtualFileSystem":
        """Загружает VFS из XML, не распаковывая данные на диск."""
        try:
            with open(file_path, "rb") as source_file:
                source_data = source_file.read()
        except OSError as error:
            raise VfsError(f"не удалось прочитать VFS: {error}") from error
        return cls.from_xml_bytes(source_data)

    @classmethod
    def from_xml_bytes(cls, source_data: bytes) -> "VirtualFileSystem":
        """Создаёт VFS из байтов XML-документа."""
        try:
            document = element_tree.fromstring(source_data)
        except element_tree.ParseError as error:
            raise VfsError(f"некорректный XML VFS: {error}") from error
        if document.tag != "vfs":
            raise VfsError("корневой тег должен быть <vfs>")
        name = document.get("name")
        if not name:
            raise VfsError("не задан атрибут name у <vfs>")
        root_items = list(document)
        if len(root_items) != 1:
            raise VfsError("VFS должна содержать один корневой каталог")
        root = _parse_node(root_items[0], is_root=True)
        if not root.is_directory:
            raise VfsError("корень VFS должен быть каталогом")
        return cls(name, source_data, root)

    def get_node(self, path: str, current_path: str = "/") -> VfsNode:
        """Возвращает узел по абсолютному или относительному пути."""
        normalized_path = self.normalize_path(path, current_path)
        node = self.root
        for part in normalized_path.parts[1:]:
            if not node.is_directory:
                raise VfsError(f"не каталог: {node.name}")
            try:
                node = node.children[part]
            except KeyError as error:
                message = f"путь не найден: {normalized_path}"
                raise VfsError(message) from error
        return node

    def normalize_path(self, path: str, current_path: str = "/") -> PurePosixPath:
        """Нормализует путь относительно текущего каталога."""
        raw_path = PurePosixPath(path)
        base_path = ROOT_PATH if raw_path.is_absolute() else PurePosixPath(
            current_path
        )
        parts: list[str] = []
        for part in (base_path / raw_path).parts:
            if part in ("", "/"):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            if part != ".":
                parts.append(part)
        return ROOT_PATH.joinpath(*parts)


def _parse_node(
    element: element_tree.Element,
    is_root: bool = False,
) -> VfsNode:
    """Преобразует XML-элемент в узел VFS."""
    if element.tag not in {"directory", "file"}:
        raise VfsError(f"неподдерживаемый элемент: {element.tag}")
    name = "" if is_root else element.get("name", "")
    if not is_root and not name:
        raise VfsError(f"у <{element.tag}> нет имени")
    if "/" in name or name in {".", ".."}:
        raise VfsError(f"некорректное имя: {name}")
    is_directory = element.tag == "directory"
    node = VfsNode(
        name=name,
        is_directory=is_directory,
        owner=element.get("owner", "root"),
    )
    if is_directory:
        for child in element:
            node.add_child(_parse_node(child))
        return node
    encoding = element.get("encoding", "text")
    node.content = _parse_content(element.text or "", encoding)
    return node


def _parse_content(value: str, encoding: str) -> bytes:
    """Декодирует текстовое либо base64-содержимое файла."""
    if encoding == "text":
        return value.encode("utf-8")
    if encoding == "base64":
        try:
            return base64.b64decode(value.encode("ascii"), validate=True)
        except ValueError as error:
            raise VfsError("некорректные base64-данные") from error
    raise VfsError(f"неподдерживаемая кодировка: {encoding}")