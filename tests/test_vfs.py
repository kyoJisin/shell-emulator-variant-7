"""Тесты виртуальной файловой системы."""

import hashlib
import unittest

from src.vfs import VfsError, VirtualFileSystem


VFS_XML = b"""\
<vfs name="test">
  <directory name="/">
    <file name="hello.txt">Hello</file>
    <file name="data.bin" encoding="base64">AAECAwQ=</file>
    <directory name="docs">
      <file name="readme.txt">Read me</file>
    </directory>
  </directory>
</vfs>
"""


class VirtualFileSystemTests(unittest.TestCase):
    """Проверяет загрузку и поиск в XML-VFS."""

    def setUp(self) -> None:
        """Создаёт VFS из тестовых XML-данных."""
        self.vfs = VirtualFileSystem.from_xml_bytes(VFS_XML)

    def test_name_is_read_from_xml(self) -> None:
        """Имя VFS извлекается из корневого элемента."""
        self.assertEqual(self.vfs.name, "test")

    def test_source_hash_matches_xml_data(self) -> None:
        """SHA-256 рассчитывается по исходным XML-байтам."""
        expected_hash = hashlib.sha256(VFS_XML).hexdigest()
        self.assertEqual(self.vfs.source_hash, expected_hash)

    def test_text_file_is_loaded_as_utf8_bytes(self) -> None:
        """Текстовое содержимое файла хранится в UTF-8."""
        node = self.vfs.get_node("/hello.txt")
        self.assertEqual(node.content, b"Hello")

    def test_base64_file_is_decoded(self) -> None:
        """Base64-содержимое преобразуется в исходные байты."""
        node = self.vfs.get_node("/data.bin")
        expected_content = bytes([0, 1, 2, 3, 4])
        self.assertEqual(node.content, expected_content)

    def test_relative_path_is_resolved(self) -> None:
        """Относительный путь разрешается из текущего каталога."""
        node = self.vfs.get_node("readme.txt", "/docs")
        self.assertEqual(node.content, b"Read me")

    def test_missing_path_raises_vfs_error(self) -> None:
        """Несуществующий путь вызывает VfsError."""
        with self.assertRaises(VfsError):
            self.vfs.get_node("/missing.txt")

    def test_invalid_root_tag_raises_vfs_error(self) -> None:
        """Некорректный корневой элемент отклоняется."""
        with self.assertRaises(VfsError):
            VirtualFileSystem.from_xml_bytes(b"<invalid/>")

    def test_unsupported_encoding_raises_vfs_error(self) -> None:
        """Неизвестная кодировка содержимого отклоняется."""
        xml_data = b"""\
<vfs name="test">
  <directory name="/">
    <file name="item" encoding="hex">00</file>
  </directory>
</vfs>
"""
        with self.assertRaises(VfsError):
            VirtualFileSystem.from_xml_bytes(xml_data)