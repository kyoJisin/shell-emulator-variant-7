"""Тесты обработки команд приложения."""

import unittest

from src.application import ShellApplication
from src.vfs import VirtualFileSystem


VFS_XML = b"""\
<vfs name="test-vfs">
  <directory name="/">
    <file name="hello.txt">Hello</file>
  </directory>
</vfs>
"""


class ShellApplicationTests(unittest.TestCase):
    """Проверяет обработчики команд REPL."""

    def setUp(self) -> None:
        """Создаёт независимое приложение для каждого теста."""
        self.application = ShellApplication()

    def test_unknown_command_returns_error(self) -> None:
        """Неизвестная команда возвращает понятную ошибку."""
        output = self.application.execute("unknown")
        self.assertEqual(output, "command not found: unknown")

    def test_exit_with_arguments_returns_error(self) -> None:
        """Команда exit не принимает аргументы."""
        output = self.application.execute("exit now")
        self.assertEqual(output, "exit: too many arguments")

    def test_vfs_info_without_vfs_returns_error(self) -> None:
        """Команда сообщает об отсутствии загруженной VFS."""
        output = self.application.execute("vfs-info")
        self.assertEqual(output, "vfs-info: VFS не загружена")

    def test_vfs_info_returns_name_and_hash(self) -> None:
        """Команда выводит имя и SHA-256 загруженной VFS."""
        vfs = VirtualFileSystem.from_xml_bytes(VFS_XML)
        application = ShellApplication(vfs)
        output = application.execute("vfs-info")
        self.assertIn("VFS: test-vfs", output)
        self.assertIn("SHA-256:", output)

    def test_ls_without_vfs_returns_error(self) -> None:
        """Команда ls требует загруженную VFS."""
        output = self.application.execute("ls")
        self.assertEqual(output, "ls: VFS не загружена")

    def test_uname_runs_without_vfs(self) -> None:
        """Команда uname работает без VFS."""
        output = self.application.execute("uname")
        self.assertEqual(output, "Shell Emulator")