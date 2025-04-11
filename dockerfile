FROM python:3.9-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Запуск бота
CMD ["python", "main.py"]