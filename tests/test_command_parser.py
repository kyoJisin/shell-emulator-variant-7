"""Тесты разбора строк команд."""

import os
import unittest

from src.command_parser import expand_environment_variables, parse_command


class CommandParserTests(unittest.TestCase):
    """Проверяет синтаксический разбор команд."""

    def test_parse_command_splits_name_and_arguments(self) -> None:
        """Команда и аргументы разделяются корректно."""
        command, arguments = parse_command("ls folder file.txt")
        self.assertEqual(command, "ls")
        self.assertEqual(arguments, ["folder", "file.txt"])

    def test_parse_command_returns_empty_values_for_blank_line(self) -> None:
        """Пустая строка не образует команду."""
        command, arguments = parse_command("   ")
        self.assertEqual(command, "")
        self.assertEqual(arguments, [])

    def test_expand_environment_variables_supports_posix_syntax(self) -> None:
        """Переменная в синтаксисе $NAME раскрывается."""
        variable_name = "SHELL_TEST_VARIABLE"
        original_value = os.environ.get(variable_name)
        os.environ[variable_name] = "expanded"
        try:
            result = expand_environment_variables(f"${variable_name}")
        finally:
            self._restore_variable(variable_name, original_value)
        self.assertEqual(result, "expanded")

    def _restore_variable(
        self,
        variable_name: str,
        original_value: str | None,
    ) -> None:
        """Восстанавливает состояние тестовой переменной окружения."""
        if original_value is None:
            del os.environ[variable_name]
            return
        os.environ[variable_name] = original_value
