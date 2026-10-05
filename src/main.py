"""Command-line entry point for the shell emulator."""

import argparse
from pathlib import Path

from src.application import ShellApplication


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description="UNIX-like shell emulator")
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        help="path to a virtual file system XML file",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="path to a startup command script",
    )
    return parser


def print_parameters(vfs_path: str | None, script_path: str | None) -> None:
    """Print the supplied configuration for debugging."""
    print("Configuration:")
    print(f"  vfs: {vfs_path or '(not set)'}")
    print(f"  script: {script_path or '(not set)'}")


def validate_file(path_value: str | None, option_name: str) -> bool:
    """Check that a supplied option points to an existing file."""
    if path_value is None:
        return True
    if Path(path_value).is_file():
        return True
    print(f"error: {option_name} file not found: {path_value}")
    return False


def main() -> None:
    """Configure and start the shell emulator."""
    arguments = build_parser().parse_args()
    print_parameters(arguments.vfs, arguments.script)
    vfs_valid = validate_file(arguments.vfs, "--vfs")
    script_valid = validate_file(arguments.script, "--script")
    if not vfs_valid or not script_valid:
        return
    application = ShellApplication()
    if arguments.script:
        application.run_script(arguments.script)
    else:
        application.run()


if __name__ == "__main__":
    main()
