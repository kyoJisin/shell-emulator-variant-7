"""Тесты основных команд эмулятора оболочки."""

import unittest

from src.commands import CommandExecutor
from src.vfs import VfsError, VirtualFileSystem


VFS_XML = b"""\
<vfs name="commands">
  <directory name="/">
    <file name="hello.txt">Hello\nWorld\nPython\nShell</file>
    <file name="remove.txt">Delete me</file>
    <directory name="docs">
      <file name="readme.txt">First\nSecond\nThird</file>
      <directory name="nested">
        <file name="item.txt">Nested item</file>
      </directory>
    </directory>
  </directory>
</vfs>
"""


class CommandExecutorTests(unittest.TestCase):
    """Проверяет команды, работающие с VFS."""

    def setUp(self) -> None:
        """Создаёт исполнитель с тестовой VFS."""
        vfs = VirtualFileSystem.from_xml_bytes(VFS_XML)
        self.executor = CommandExecutor(vfs)

    def test_ls_lists_root_directory(self) -> None:
        """ls выводит элементы корневого каталога."""
        expected = "docs  hello.txt  remove.txt"
        self.assertEqual(self.executor.ls([]), expected)

    def test_ls_lists_file_name(self) -> None:
        """ls для файла выводит его имя."""
        self.assertEqual(self.executor.ls(["hello.txt"]), "hello.txt")

    def test_ls_returns_error_for_missing_path(self) -> None:
        """ls сообщает об отсутствующем пути."""
        output = self.executor.ls(["missing"])
        self.assertTrue(output.startswith("ls: путь не найден:"))

    def test_cd_changes_current_directory(self) -> None:
        """cd меняет текущий каталог."""
        output = self.executor.cd(["docs"])
        self.assertEqual(output, "")
        self.assertEqual(self.executor.current_path, "/docs")

    def test_cd_parent_directory(self) -> None:
        """cd .. возвращает в родительский каталог."""
        self.executor.cd(["docs"])
        self.executor.cd([".."])
        self.assertEqual(self.executor.current_path, "/")

    def test_cd_rejects_file(self) -> None:
        """cd не переходит в файл."""
        output = self.executor.cd(["hello.txt"])
        self.assertEqual(output, "cd: не каталог: /hello.txt")

    def test_rev_reverses_each_line(self) -> None:
        """rev меняет порядок символов отдельно в каждой строке."""
        output = self.executor.rev(["hello.txt"])
        self.assertEqual(output, "olleH\ndlroW\nnohtyP\nllehS")

    def test_uname_returns_emulator_name(self) -> None:
        """uname выводит имя эмулятора."""
        self.assertEqual(self.executor.uname([]), "Shell Emulator")

    def test_uname_all_returns_details(self) -> None:
        """uname -a выводит расширенные сведения."""
        output = self.executor.uname(["-a"])
        self.assertEqual(output, "Shell Emulator Windows Python")

    def test_head_uses_default_line_count(self) -> None:
        """head без параметров количества выводит первые строки."""
        output = self.executor.head(["hello.txt"])
        self.assertEqual(output, "Hello\nWorld\nPython\nShell")

    def test_head_uses_requested_line_count(self) -> None:
        """head -n выводит заданное количество строк."""
        output = self.executor.head(["-n", "2", "hello.txt"])
        self.assertEqual(output, "Hello\nWorld")

    def test_head_rejects_invalid_count(self) -> None:
        """head отклоняет нечисловое количество строк."""
        output = self.executor.head(["-n", "many", "hello.txt"])
        self.assertEqual(output, "head: неверное число строк")

    def test_rm_removes_file_from_memory(self) -> None:
        """rm удаляет файл только из текущей VFS в памяти."""
        output = self.executor.rm(["remove.txt"])
        self.assertEqual(output, "")
        with self.assertRaises(VfsError):
            self.executor._vfs.get_node("/remove.txt")

    def test_rm_rejects_directory_without_recursive_flag(self) -> None:
        """rm запрещает удалять каталог без параметра -r."""
        output = self.executor.rm(["docs"])
        expected = "rm: это каталог: /docs; используйте -r"
        self.assertEqual(output, expected)

    def test_rm_recursively_removes_directory(self) -> None:
        """rm -r удаляет каталог со всем его содержимым."""
        output = self.executor.rm(["-r", "docs"])
        self.assertEqual(output, "")
        with self.assertRaises(VfsError):
            self.executor._vfs.get_node("/docs")

    def test_rm_rejects_root_directory(self) -> None:
        """rm -r не позволяет удалить корень VFS."""
        output = self.executor.rm(["-r", "/"])
        self.assertEqual(output, "rm: нельзя выполнить операцию для корня VFS")

    def test_rm_rejects_current_directory(self) -> None:
        """rm не удаляет каталог, являющийся текущим."""
        self.executor.cd(["docs"])
        output = self.executor.rm(["-r", "/docs"])
        expected = "rm: нельзя удалить текущий каталог или его родителя"
        self.assertEqual(output, expected)

    def test_chown_changes_node_owner_in_memory(self) -> None:
        """chown меняет владельца файла только в памяти."""
        output = self.executor.chown(["student", "hello.txt"])
        self.assertEqual(output, "")
        node = self.executor._vfs.get_node("/hello.txt")
        self.assertEqual(node.owner, "student")

    def test_chown_rejects_wrong_argument_count(self) -> None:
        """chown требует имя владельца и путь."""
        output = self.executor.chown(["student"])
        self.assertEqual(output, "chown: требуется владелец и путь")

    def test_chown_rejects_missing_path(self) -> None:
        """chown сообщает об отсутствующем пути."""
        output = self.executor.chown(["student", "missing.txt"])
        self.assertTrue(output.startswith("chown: путь не найден:"))