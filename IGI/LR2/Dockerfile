# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем скрипт и библиотеки
COPY . .

# Указываем команду для запуска скрипта
ENTRYPOINT ["python", "script.py"]
