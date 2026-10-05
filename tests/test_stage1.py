"""Тесты требований первого этапа эмулятора оболочки."""

import os
import unittest

from src.application import ShellApplication
from src.command_parser import expand_environment_variables, parse_command


class StageOneTests(unittest.TestCase):
    """Проверяет требования этапа 1: REPL и парсер команд."""

    def setUp(self) -> None:
        """Создаёт приложение для каждого тестового случая."""
        self.application = ShellApplication()

    def test_empty_line_produces_no_command(self) -> None:
        """Пустой ввод не создаёт команду."""
        command_name, arguments = parse_command("   ")
        self.assertEqual(command_name, "")
        self.assertEqual(arguments, [])

    def test_command_name_and_arguments_are_parsed(self) -> None:
        """Парсер разделяет имя команды и аргументы."""
        command_name, arguments = parse_command("ls documents file.txt")
        self.assertEqual(command_name, "ls")
        self.assertEqual(arguments, ["documents", "file.txt"])

    def test_posix_environment_variable_is_expanded(self) -> None:
        """Переменная окружения формата $NAME раскрывается."""
        variable_name = "STAGE_ONE_VARIABLE"
        original_value = os.environ.get(variable_name)
        os.environ[variable_name] = "expanded-value"
        try:
            result = expand_environment_variables(f"${variable_name}")
        finally:
            self._restore_variable(variable_name, original_value)
        self.assertEqual(result, "expanded-value")

    def test_exit_stops_application(self) -> None:
        """exit без аргументов завершает приложение."""
        output = self.application.execute("exit")
        self.assertEqual(output, "")
        self.assertFalse(self.application._is_running)

    def test_exit_with_arguments_returns_error(self) -> None:
        """exit с аргументами возвращает ошибку."""
        output = self.application.execute("exit now")
        self.assertEqual(output, "exit: too many arguments")

    def test_unknown_command_returns_error(self) -> None:
        """Неизвестная команда возвращает понятную ошибку."""
        output = self.application.execute("unknown-command")
        expected = "command not found: unknown-command"
        self.assertEqual(output, expected)
    def _restore_variable(
        self,
        variable_name: str,
        original_value: str | None,
    ) -> None:
        """Восстанавливает исходное значение переменной окружения."""
        if original_value is None:
            del os.environ[variable_name]
            return
        os.environ[variable_name] = original_value