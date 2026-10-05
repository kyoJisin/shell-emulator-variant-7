"""Точка входа командной строки эмулятора оболочки."""

import argparse
from pathlib import Path

from src.application import ShellApplication
from src.vfs import VfsError, VirtualFileSystem


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор UNIX-подобной оболочки"
    )
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        help="путь к XML-файлу виртуальной файловой системы",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="путь к стартовому сценарию команд",
    )
    return parser


def print_parameters(vfs_path: str | None, script_path: str | None) -> None:
    """Выводит переданные параметры для отладки."""
    print("Configuration:")
    print(f"  vfs: {vfs_path or '(not set)'}")
    print(f"  script: {script_path or '(not set)'}")


def validate_file(path_value: str | None, option_name: str) -> bool:
    """Проверяет, что параметр указывает на существующий файл."""
    if path_value is None:
        return True
    if Path(path_value).is_file():
        return True
    print(f"error: {option_name} file not found: {path_value}")
    return False


def load_vfs(vfs_path: str | None) -> VirtualFileSystem | None:
    """Загружает VFS из XML и выводит ошибку при некорректных данных."""
    if vfs_path is None:
        return None
    try:
        return VirtualFileSystem.from_xml_file(vfs_path)
    except VfsError as error:
        print(f"error: {error}")
        return None


def main() -> None:
    """Настраивает и запускает эмулятор оболочки."""
    arguments = build_parser().parse_args()
    print_parameters(arguments.vfs, arguments.script)
    vfs_valid = validate_file(arguments.vfs, "--vfs")
    script_valid = validate_file(arguments.script, "--script")
    if not vfs_valid or not script_valid:
        return
    vfs = load_vfs(arguments.vfs)
    if arguments.vfs and vfs is None:
        return
    application = ShellApplication(vfs)
    if arguments.script:
        application.run_script(arguments.script)
    else:
        application.run()


if __name__ == "__main__":
    main()