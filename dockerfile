FROM python:3.9-slim

# Установка ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Запуск бота
CMD ["python", "main.py"]