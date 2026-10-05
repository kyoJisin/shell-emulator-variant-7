# Эмулятор UNIX-подобной оболочки

Практическая работа по дисциплине «Конфигурационное управление». Вариант 7.

## Общее описание

Приложение эмулирует часть поведения UNIX-подобной командной оболочки. На
первом этапе реализован консольный REPL с обработкой базовых команд.

## Функции и настройки

- REPL с приглашением `username@hostname:~$`;
- раскрытие переменных окружения Windows (`%NAME%`) и POSIX (`$NAME`);
- команды-заглушки `ls` и `cd`;
- команда `exit`;
- сообщения для неизвестных команд, ошибок разбора и неверных аргументов.

## Сборка и тесты

Требуется Python 3.10 или новее. Внешние зависимости не нужны.

```bat
run.bat
python -m unittest discover -s tests -v
```

## Примеры использования

```text
user@computer:~$ ls documents
ls: arguments: documents
user@computer:~$ cd %USERPROFILE%
cd: arguments: C:\Users\user
user@computer:~$ unknown
command not found: unknown
user@computer:~$ exit
```
