"""Точка входа в эмулятор оболочки."""

from src.application import ShellApplication


def main() -> None:
    """Создаёт и запускает приложение."""
    ShellApplication().run()


if __name__ == "__main__":
    main()
