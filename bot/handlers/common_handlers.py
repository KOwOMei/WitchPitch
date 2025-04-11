from aiogram import types
from aiogram.dispatcher import Dispatcher

def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])

async def start_command(message: types.Message):
    await message.answer("Привет! Я PitchWitch — твоя ведьма тона. Отправь мне аудиофайл, и я помогу тебе изменить его тональность!")

async def help_command(message: types.Message):
    await message.answer("Я могу помочь тебе изменить тональность аудиофайлов. Просто отправь мне аудиофайл и следуй инструкциям!")