from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from bot.services.audio_processing import process_audio_file
from bot.keyboards.inline_keyboards import get_pitch_keyboard
import logging
import os

async def handle_audio(message: types.Message, state: FSMContext):
    try:
        if message.audio:
            await message.reply("Обработка аудиофайла...")
            logging.info(f"Получен аудиофайл: {message.audio.file_id}")
            
            user_id = message.from_user.id
            user_folder = f"user_{user_id}"
            os.makedirs(user_folder, exist_ok=True)
            audio_path = os.path.join(user_folder, "audio.ogg")
            await message.audio.download(destination_file=audio_path)

            await state.update_data(audio_path=audio_path)
            
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
        # Детальное логирование
        logging.info(f"Получен callback: {callback_query.data}")
        
        selected_pitch = int(callback_query.data)
        await callback_query.answer(f"Обрабатываю с тональностью {selected_pitch}...")
        
        # Получение пути к аудиофайлу из состояния
        data = await state.get_data()
        audio_path = data.get('audio_path', "user_audio.ogg")
        
        # Проверка файла
        if not os.path.exists(audio_path):
            logging.error(f"Файл {audio_path} не найден")
            await callback_query.message.answer("Ошибка: файл не найден")
            await state.finish()
            return
        
        # Оповещение пользователя перед длительной операцией
        status_message = await callback_query.message.answer("Начинаю обработку аудио...")
        
        try:
            audio_file_path = await process_audio_file(audio_path, selected_pitch, "temp")
            logging.info(f"Готовый файл: {audio_file_path}")
        except Exception as e:
            logging.exception(f"Ошибка обработки: {e}")
            await callback_query.message.answer(f"Не удалось обработать: {e}")
            await state.finish()
            return
            
        # Отправляем результат
        try:
            await status_message.edit_text("Отправляю обработанный файл...")
            with open(audio_file_path, 'rb') as audio:
                await callback_query.message.answer_audio(
                    audio=types.InputFile(audio_file_path),
                    caption=f"Изменение тональности: {selected_pitch}"
                )
        except Exception as e:
            logging.exception(f"Ошибка отправки: {e}")
            await callback_query.message.answer(f"Не удалось отправить файл: {e}")
        
        await state.finish()
    except Exception as e:
        logging.exception(f"Критическая ошибка: {e}")
        await callback_query.message.answer("Произошла непредвиденная ошибка")
        await state.finish()

def register_audio_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_audio, content_types=types.ContentType.AUDIO, state="*")
    dp.register_callback_query_handler(process_pitch_selection, lambda c: c.data.isdigit(), state="waiting_for_pitch_selection")