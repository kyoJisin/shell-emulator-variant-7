# Эмулятор оболочки ОС, вариант 7

Консольный эмулятор UNIX-подобной оболочки на Python для практической работы
по конфигурационному управлению. Программа запускается на Windows и работает
с виртуальной файловой системой, загружаемой из XML.

## Требования

- Windows 10 или новее
- Python 3.10 или новее
- Git for Windows

Сторонние библиотеки не используются.

## Запуск

Откройте терминал в корне репозитория и выполните:

```powershell
python -m src.main
```

Либо запустите:

```powershell
.\run.bat
```

Для запуска с виртуальной файловой системой:

```powershell
python -m src.main --vfs examples\vfs_files.xml
```

Для выполнения стартового сценария:

```powershell
python -m src.main --vfs examples\vfs_files.xml `
  --script examples\scripts\stage5.txt
```

## Параметры

- `--vfs` — путь к XML-файлу VFS.
- `--script` — путь к UTF-8 текстовому сценарию команд.

При запуске выводятся переданные параметры. Ошибка в одной строке сценария не
останавливает выполнение последующих команд.

## XML-VFS

VFS загружается в память из XML. Программа не распаковывает и не изменяет
исходный XML-файл на физическом диске.

```xml
<vfs name="files">
  <directory name="/" owner="root">
    <file name="hello.txt">Привет из VFS</file>
    <file name="data.bin" encoding="base64">AAECAwQ=</file>
    <directory name="docs">
      <file name="readme.txt">Документация</file>
    </directory>
  </directory>
</vfs>
```

Поддерживаются:

- `<directory>` — каталог;
- `<file>` — текстовый UTF-8 файл;
- `<file encoding="base64">` — двоичный файл в Base64;
- `owner` — владелец узла, по умолчанию `root`.

## Команды

| Команда | Описание |
|---|---|
| `vfs-info` | Выводит имя VFS и SHA-256 исходного XML |
| `ls [путь]` | Выводит содержимое каталога или имя файла |
| `cd [путь]` | Переходит в каталог VFS; без пути переходит в `/` |
| `rev путь` | Переворачивает символы каждой строки текстового файла |
| `uname` | Выводит `Shell Emulator` |
| `uname -a` | Выводит расширенные данные об эмуляторе |
| `head путь` | Выводит первые 10 строк текстового файла |
| `head -n N путь` | Выводит первые `N` строк файла |
| `rm путь` | Удаляет файл из VFS в памяти |
| `rm -r путь` | Рекурсивно удаляет каталог из VFS в памяти |
| `chown владелец путь` | Изменяет владельца файла или каталога в памяти |
| `exit` | Завершает работу эмулятора |

Команды `ls`, `cd`, `rev`, `head`, `rm` и `chown` работают только при
передаче параметра `--vfs`.

Команды `rm` и `chown` не меняют XML-файл. После нового запуска VFS заново
создаётся из исходного XML, поэтому удалённые файлы и исходные владельцы
восстанавливаются.

## Примеры

Этап 1:

```powershell
.\examples\run_stage1.bat
```

Этап 2:

```powershell
.\examples\run_stage2.bat
```

Этап 3:

```powershell
.\examples\run_stage3_files.bat
```

Этап 4:

```powershell
.\examples\run_stage4.bat
```

Этап 5:

```powershell
.\examples\run_stage5.bat
```

Интерактивная проверка:

```powershell
python -m src.main --vfs examples\vfs_files.xml
```

После запуска можно ввести:

```text
ls
chown student hello.txt
rm hello.txt
ls
exit
```

## Тесты

Для запуска всех тестов:

```powershell
python -m unittest discover -s tests -v
```

## Проверка этапов

| Этап | Файл или сценарий | Что проверяется |
|---|---|---|
| Этап 1 | `examples/run_stage1.bat` | Запуск REPL, команда `exit` и обработка неизвестной команды |
| Этап 1 | `tests/test_command_parser.py` | Дополнительные тесты синтаксического разбора и переменных окружения |
| Этап 2 | `examples/run_stage2.bat` | Параметры и стартовый сценарий |
| Этап 3 | `tests/test_vfs.py` | XML, SHA-256, Base64 и пути VFS |
| Этап 3 | `examples/run_stage3_files.bat` | Загрузка VFS и `vfs-info` |
| Этап 4 | `tests/test_commands.py` | `ls`, `cd`, `rev`, `uname` и `head` |
| Этап 4 | `examples/run_stage4.bat` | Сценарий основных команд |
| Этап 5 | `tests/test_commands.py` | `rm`, `rm -r`, `chown` и ошибки |
| Этап 5 | `examples/run_stage5.bat` | Изменения VFS только в памяти |