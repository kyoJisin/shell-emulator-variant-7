"""Разбор пользовательского ввода и раскрытие переменных окружения."""

import os
import re
import shlex

_POSIX_VARIABLE_PATTERN = re.compile(
    r"\$(?:\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)\}|"
    r"(?P<plain>[A-Za-z_][A-Za-z0-9_]*))"
)


def parse_command(line: str) -> tuple[str, list[str]]:
    """Возвращает команду и аргументы из введённой строки."""
    expanded_line = expand_environment_variables(line.strip())
    if not expanded_line:
        return "", []
    parts = shlex.split(expanded_line, posix=False)
    return parts[0].lower(), parts[1:]


def expand_environment_variables(value: str) -> str:
    """Раскрывает переменные окружения в форматах Windows и POSIX."""
    windows_expanded = os.path.expandvars(value)
    return _POSIX_VARIABLE_PATTERN.sub(_replace_posix_variable, windows_expanded)


def _replace_posix_variable(match: re.Match[str]) -> str:
    """Подставляет значение одной POSIX-переменной окружения."""
    variable_name = match.group("braced") or match.group("plain")
    return os.environ.get(variable_name, match.group(0))
