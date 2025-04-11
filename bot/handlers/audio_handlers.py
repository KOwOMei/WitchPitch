from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from .services.audio_processing import process_audio, generate_pitch_variants

async def start_audio_processing(message: types.Message):
    await message.reply("Пожалуйста, отправьте аудиофайл для обработки.")

async def handle_audio(message: types.Message, state: FSMContext):
    if message.audio:
        audio_file = await message.audio.get_file()
        await audio_file.download(destination_file="user_audio.ogg")
        
        pitch_variants = generate_pitch_variants("user_audio.ogg")
        await message.reply("Выберите вариант звучания:", reply_markup=pitch_variants)
        
        await state.set_state("waiting_for_pitch_selection")
    else:
        await message.reply("Пожалуйста, отправьте аудиофайл.")

async def process_pitch_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_pitch = callback_query.data
    audio_file_path = await process_audio("user_audio.ogg", selected_pitch)
    
    await callback_query.answer("Обработка завершена! Отправляю аудиофайл...")
    await callback_query.message.answer_audio(audio=open(audio_file_path, 'rb'))
    
    await state.finish()

def register_audio_handlers(dp: Dispatcher):
    dp.register_message_handler(start_audio_processing, commands=['start'], state="*")
    dp.register_message_handler(handle_audio, content_types=types.ContentType.AUDIO, state="*")
    dp.register_callback_query_handler(process_pitch_selection, state="waiting_for_pitch_selection")