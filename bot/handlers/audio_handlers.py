from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from bot.services.audio_processing import process_audio_file
from bot.keyboards.inline_keyboards import get_pitch_keyboard
import logging
import os

# Функция-фильтр для проверки, является ли callback_data числом
def is_float_or_int(callback_data: str) -> bool:
    try:
        float(callback_data)
        return True
    except ValueError:
        return False

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

# Новая функция для обработки запроса пользовательского тона
async def handle_custom_pitch_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Пожалуйста, введите желаемое значение тональности (например, -1.5 или 3):")
    await state.set_state("waiting_for_custom_pitch_input") # Новое состояние

# Новая функция для обработки введенного пользовательского тона
async def process_custom_pitch_input(message: types.Message, state: FSMContext):
    try:
        custom_pitch = float(message.text)
        # Здесь можно добавить проверку на допустимый диапазон, если нужно
        # Например: if not -12 <= custom_pitch <= 12: raise ValueError("Недопустимый диапазон")

        await message.reply(f"Принято значение: {custom_pitch}. Начинаю обработку...")

        # Получаем путь к файлу из состояния
        user_data = await state.get_data()
        audio_path = user_data.get('audio_path')

        if not audio_path or not os.path.exists(audio_path):
            logging.error(f"Аудиофайл не найден в состоянии или по пути: {audio_path}")
            await message.reply("Ошибка: не найден исходный аудиофайл. Пожалуйста, отправьте его снова.")
            await state.finish()
            return

        # Запускаем обработку (аналогично process_pitch_selection)
        status_message = await message.answer("Обработка аудио...")
        try:
            audio_file_path = await process_audio_file(audio_path, custom_pitch, f"user_{message.from_user.id}/temp") # Используем подпапку temp
            logging.info(f"Готовый файл: {audio_file_path}")
        except Exception as e:
            logging.exception(f"Ошибка обработки custom pitch: {e}")
            await message.answer(f"Не удалось обработать: {e}")
            await state.finish()
            return

        # Отправляем результат
        try:
            await status_message.edit_text("Отправляю обработанный файл...")
            with open(audio_file_path, 'rb') as audio:
                await message.answer_audio(
                    audio=types.InputFile(audio_file_path),
                    caption=f"Изменение тональности: {custom_pitch}"
                )
        except Exception as e:
            logging.exception(f"Ошибка отправки custom pitch: {e}")
            await message.answer(f"Не удалось отправить файл: {e}")

        await state.finish()

    except ValueError:
        await message.reply("Неверный формат. Пожалуйста, введите число (например, -1.5 или 3).")
    except Exception as e:
        logging.exception(f"Критическая ошибка в process_custom_pitch_input: {e}")
        await message.answer("Произошла непредвиденная ошибка при обработке вашего значения.")
        await state.finish()

def register_audio_handlers(dp: Dispatcher):
    dp.register_message_handler(handle_audio, content_types=types.ContentType.AUDIO, state="*")

    # Обработчик для числовых кнопок (включая float и отрицательные)
    dp.register_callback_query_handler(
        process_pitch_selection,
        lambda c: is_float_or_int(c.data), # Используем новую функцию-фильтр
        state="waiting_for_pitch_selection"
    )

    # Обработчик для кнопки "Пользовательский тон"
    dp.register_callback_query_handler(
        handle_custom_pitch_request,
        lambda c: c.data == "custom_pitch",
        state="waiting_for_pitch_selection"
    )

    # Обработчик для ввода пользовательского значения
    dp.register_message_handler(
        process_custom_pitch_input,
        state="waiting_for_custom_pitch_input"
    )