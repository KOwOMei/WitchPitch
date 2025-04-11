from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from bot.services.audio_processing import process_audio_file
from bot.keyboards.inline_keyboards import get_pitch_keyboard
import logging

async def start_audio_processing(message: types.Message):
    await message.reply("Пожалуйста, отправьте аудиофайл для обработки.")

async def handle_audio(message: types.Message, state: FSMContext):
    try:
        if message.audio:
            await message.reply("Обработка аудиофайла...")
            logging.info(f"Получен аудиофайл: {message.audio.file_id}")
            
            audio_file = await message.audio.get_file()
            await audio_file.download(destination_file="user_audio.ogg")
            
            # Используем клавиатуру вместо результата generate_pitch_variants
            keyboard = get_pitch_keyboard()
            await message.reply("Выберите вариант звучания:", reply_markup=keyboard)
            
            await state.set_state("waiting_for_pitch_selection")
        else:
            await message.reply("Пожалуйста, отправьте аудиофайл.")
    except Exception as e:
        logging.error(f"Ошибка при обработке аудио: {e}")
        await message.reply(f"Произошла ошибка при обработке аудио: {e}")
        
async def process_pitch_selection(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        selected_pitch = int(callback_query.data)  # Преобразуем строку в число
        await callback_query.answer(f"Обрабатываю аудио с тональностью {selected_pitch}...")
        
        # Убираем await, если функция не асинхронная
        audio_file_path = process_audio_file("user_audio.ogg", selected_pitch, "temp")
        
        await callback_query.message.reply("Обработка завершена! Отправляю аудиофайл...")
        with open(audio_file_path, 'rb') as audio:
            await callback_query.message.answer_audio(audio=audio)
        
        await state.finish()
    except Exception as e:
        logging.error(f"Ошибка при обработке выбора тональности: {e}")
        await callback_query.message.reply(f"Произошла ошибка: {e}")
        
def register_audio_handlers(dp: Dispatcher):
    dp.register_message_handler(start_audio_processing, commands=['start'], state="*")
    dp.register_message_handler(handle_audio, content_types=types.ContentType.AUDIO, state="*")
    dp.register_callback_query_handler(process_pitch_selection, state="waiting_for_pitch_selection")