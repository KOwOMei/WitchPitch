# PitchWitch - Telegram Бот для "музыкальной магии"

PitchWitch is a Telegram bot that transforms ordinary audio files into magical melodies. It allows users to change the pitch of any audio recordings (voice messages, music, etc.) with just a few clicks.

## Features

- Accepts audio files from users.
- Generates 5 preview options with different pitch shifts: from low to high (-4, -2, 0, +2, +4).
- Allows users to select any of the suggested options or enter a specific value manually.
- Sends a short fragment (15-30 seconds) with the selected effect for preview.
- After user confirmation, returns the full audio file with the modified pitch in .mp3 format.

## Advantages

- User-friendly interface with selection buttons.
- Fast and high-quality processing.
- Support for manual pitch input.
- Suitable for musicians, meme creators, bloggers, and audio enthusiasts.

## Installation

1. Склонируйте репозиторий: 
   ```
   git clone https://github.com/yourusername/pitchwitch-bot.git
   ```
2. Перейдите в директорию проекта:
   ```
   cd pitchwitch-bot
   ```
3. Установите нужные зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Настройте свои переменные окружения, переименовав `.env.example` в `.env` и заполнив необходимые значения.

## Использование

1. Запустите бота:
   ```
   python main.py
   ```
2. Взаимодействуйте с ботом в Telegram, отправляя аудиофайлы и выбирая варианты изменения высоты.

## Участие

Участие сторонних программистов приветствуется! Спокойно отправляйте pull request или открывайте issue для исправления ошибок.

## Лицензия

This project is licensed under the MIT License. See the LICENSE file for details.

PitchWitch - your pitch witch. Transform sound into spells!