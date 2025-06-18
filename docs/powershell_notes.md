# Особенности работы с PowerShell и Docker

## Проблемы с PSReadLine

При выполнении длительных команд в PowerShell через Docker может возникать ошибка PSReadLine. Это особенно заметно при:
- Выполнении команд с большим выводом
- Длительных операциях (например, загрузка моделей)
- Командах с интерактивным выводом

### Решения:

1. Использовать флаг `-T` для отключения TTY:
```powershell
docker compose exec -T container_name command
```

2. Перенаправлять вывод в файл:
```powershell
docker compose exec container_name command > output.log
```

3. Использовать `cmd.exe` вместо PowerShell для критичных команд:
```cmd
cmd /c "docker compose exec container_name command"
```

## Особенности выполнения команд

1. **Длинные команды**: PowerShell может некорректно обрабатывать длинные команды. Рекомендуется:
   - Разбивать команды на несколько строк
   - Использовать переменные для длинных частей
   - Использовать `-T` флаг

2. **Фоновые процессы**: Для запуска процессов в фоне:
   - Использовать `Start-Process`
   - Добавлять `&` в конце команды
   - Использовать `-NoNewWindow` для скрытия окна

3. **Передача параметров**: При передаче параметров в команды Docker:
   - Использовать одинарные кавычки для строк
   - Экранировать специальные символы
   - Использовать `$env:` для переменных окружения

## Рекомендации

1. Для длительных операций:
```powershell
docker compose exec -T container_name command
```

2. Для интерактивных команд:
```powershell
docker compose exec container_name command
```

3. Для отладки:
```powershell
$VerbosePreference = "Continue"
docker compose exec container_name command
```

4. Для сохранения вывода:
```powershell
docker compose exec container_name command | Tee-Object -FilePath output.log
```

## Типичные проблемы и решения

1. **Ошибка PSReadLine**:
   - Использовать `-T` флаг
   - Переключиться на cmd.exe
   - Сохранять вывод в файл

2. **Проблемы с кодировкой**:
   - Установить `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`
   - Использовать `chcp 65001` для UTF-8

3. **Проблемы с правами**:
   - Запускать PowerShell от администратора
   - Проверять политики выполнения `Get-ExecutionPolicy`

4. **Проблемы с путями**:
   - Использовать `$PWD` для текущего пути
   - Нормализовать пути через `[System.IO.Path]::GetFullPath()` 