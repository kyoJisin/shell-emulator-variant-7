# Shell emulator, variant 7

A Python CLI emulator of a UNIX-like shell created for the configuration
management practical assignment, variant 7. The project currently includes
stages 1 and 2.

## Requirements

- Windows 10 or newer
- Python 3.10 or newer

No third-party packages are required.

## Start

From the repository root, run one of the commands:

```powershell
python -m src.main
.\run.bat
```

The prompt uses the current operating system account and host name:

```text
username@hostname:~$
```

## Stage 1

- Interactive REPL
- Commands `ls` and `cd` as stubs
- Command `exit`
- Expansion of environment variables in `$NAME`, `${NAME}`, and `%NAME%`
  formats

## Stage 2

The emulator accepts these optional parameters:

```powershell
python -m src.main --vfs path\to\vfs.xml --script path\to\script.txt
```

- `--vfs` reserves a path to the VFS XML file for the next stage.
- `--script` executes commands from a UTF-8 text file.
- Startup prints all received parameter values for debugging.
- The script prints each command with the prompt, keeps going after an error,
  and stops after a valid `exit` command.

Run the stage 2 demonstration on Windows:

```powershell
.\examples\run_stage2.bat
```

The example includes a deliberately unknown command and `exit extra` to show
error handling.

## Tests

```powershell
python -m unittest discover -s tests -v
```
