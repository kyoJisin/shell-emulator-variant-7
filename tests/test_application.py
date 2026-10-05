"""Тесты обработки команд приложения."""

import unittest

from src.application import ShellApplication


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

    def test_stub_command_returns_arguments(self) -> None:
        """Команда-заглушка выводит полученные аргументы."""
        output = self.application.execute("ls documents")
        self.assertEqual(output, "ls: arguments: documents")

    def test_cd_stub_returns_command_name(self) -> None:
        """Заглушка cd выводит имя команды."""
        output = self.application.execute("cd folder")
        self.assertEqual(output, "cd: arguments: folder")
