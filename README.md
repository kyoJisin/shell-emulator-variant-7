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
  --script examples\scripts\stage4.txt
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
| `exit` | Завершает работу эмулятора |

Команды `ls`, `cd`, `rev` и `head` работают только при передаче `--vfs`.

## Примеры

Этап 3:

```powershell
.\examples\run_stage3_files.bat
```

Этап 4:

```powershell
.\examples\run_stage4.bat
```

Интерактивная проверка:

```powershell
python -m src.main --vfs examples\vfs_files.xml
```

После запуска можно ввести:

```text
ls
cd docs
head readme.txt
rev readme.txt
uname -a
exit
```

## Тесты

Для запуска всех тестов:

```powershell
python -m unittest discover -s tests -v
```