import asyncio
import os
import logging
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher import filters
from bot.services.audio_processing import process_audio_file
from bot.keyboards.inline_keyboards import get_pitch_keyboard

# Функция-фильтр для проверки, является ли callback_data числом
def is_float_or_int(callback_data: str) -> bool:
    try:
        float(callback_data)
        return True
    except ValueError:
        return False

# Функция для безопасного удаления файла
def safe_remove_file(file_path: str | None):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info(f"Файл успешно удален: {file_path}")
        except OSError as e:
            logging.error(f"Не удалось удалить файл {file_path}: {e}")
    elif file_path:
        logging.warning(f"Попытка удалить несуществующий файл: {file_path}")

async def handle_audio(message: types.Message, state: FSMContext):
    try:
        if message.audio:
            await message.reply("Обработка аудиофайла...")
            logging.info(f"Получен аудиофайл: {message.audio.file_id}")
            
            user_id = message.from_user.id
            user_folder = f"user_{user_id}"
            os.makedirs(user_folder, exist_ok=True)
            audio_path = os.path.join(user_folder, f"{message.audio.file_name}.ogg")
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
    original_audio_path = None
    processed_audio_path = None
    try:
        selected_pitch = float(callback_query.data) # Используем float для единообразия
        await callback_query.answer(f"Обрабатываю с тональностью {selected_pitch}...")

        # Получаем путь к исходному файлу из состояния
        user_data = await state.get_data()
        original_audio_path = user_data.get('audio_path')

        if not original_audio_path or not os.path.exists(original_audio_path):
            logging.error(f"Исходный аудиофайл не найден в состоянии или по пути: {original_audio_path}")
            await callback_query.message.answer("Ошибка: не найден исходный аудиофайл. Пожалуйста, отправьте его снова.")
            await state.finish()
            return

        status_message = await callback_query.message.answer("Начинаю обработку аудио...")

        try:
            # Определяем папку для временных файлов пользователя
            user_id = callback_query.from_user.id
            temp_output_dir = os.path.join(os.path.dirname(original_audio_path), "temp") # Папка temp внутри папки пользователя

            processed_audio_path = await process_audio_file(original_audio_path, selected_pitch, temp_output_dir)
            logging.info(f"Готовый файл: {processed_audio_path}")
        except Exception as e:
            logging.exception(f"Ошибка обработки: {e}")
            await callback_query.message.answer(f"Не удалось обработать: {e}")
            await state.finish()
            return # Не удаляем файлы, если обработка не удалась

        if not processed_audio_path:
             await status_message.edit_text("Не удалось обработать аудио.")
             await state.finish()
             # Не удаляем исходный файл, если обработка не удалась
             return

        # Отправляем результат
        try:
            await status_message.edit_text("Отправляю обработанный файл...")
            with open(processed_audio_path, 'rb') as audio:
                await callback_query.message.answer_audio(
                    audio=types.InputFile(processed_audio_path), # Можно передать путь напрямую
                    caption=f"Изменение тональности: {selected_pitch}"
                )
            logging.info(f"Файл {processed_audio_path} успешно отправлен пользователю {user_id}")
        except Exception as e:
            logging.exception(f"Ошибка отправки: {e}")
            await callback_query.message.answer(f"Не удалось отправить файл: {e}")
            # Файлы все равно удаляем ниже, т.к. они уже созданы

        await state.finish()

    except ValueError:
         await callback_query.answer("Ошибка: неверное значение тональности.")
    except Exception as e:
        logging.exception(f"Критическая ошибка в process_pitch_selection: {e}")
        await callback_query.message.answer("Произошла непредвиденная ошибка")
        await state.finish()
    finally:
        # Очистка файлов после завершения (успешного или с ошибкой отправки)
        logging.info("Начало очистки временных файлов...")
        safe_remove_file(processed_audio_path) # Удаляем обработанный файл
        safe_remove_file(original_audio_path)  # Удаляем исходный файл
        logging.info("Очистка временных файлов завершена.")

async def handle_custom_pitch_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer("Пожалуйста, введите желаемое значение тональности (например, -1.5 или 3):")
    await state.set_state("waiting_for_custom_pitch_input") # Новое состояние

async def process_custom_pitch_input(message: types.Message, state: FSMContext):
    original_audio_path = None
    processed_audio_path = None
    try:
        custom_pitch = float(message.text)
        # Здесь можно добавить проверку на допустимый диапазон, если нужно

        await message.reply(f"Принято значение: {custom_pitch}. Начинаю обработку...")

        # Получаем путь к файлу из состояния
        user_data = await state.get_data()
        original_audio_path = user_data.get('audio_path')

        if not original_audio_path or not os.path.exists(original_audio_path):
            logging.error(f"Аудиофайл не найден в состоянии или по пути: {original_audio_path}")
            await message.reply("Ошибка: не найден исходный аудиофайл. Пожалуйста, отправьте его снова.")
            await state.finish()
            return

        status_message = await message.answer("Обработка аудио...")
        try:
            # Определяем папку для временных файлов пользователя
            user_id = message.from_user.id
            temp_output_dir = os.path.join(os.path.dirname(original_audio_path), "temp") # Папка temp внутри папки пользователя

            processed_audio_path = await process_audio_file(original_audio_path, custom_pitch, temp_output_dir)
            logging.info(f"Готовый файл: {processed_audio_path}")
        except Exception as e:
            logging.exception(f"Ошибка обработки custom pitch: {e}")
            await message.answer(f"Не удалось обработать: {e}")
            await state.finish()
            return # Не удаляем файлы

        if not processed_audio_path:
             await status_message.edit_text("Не удалось обработать аудио.")
             await state.finish()
             # Не удаляем исходный файл
             return

        # Отправляем результат
        try:
            await status_message.edit_text("Отправляю обработанный файл...")
            with open(processed_audio_path, 'rb') as audio:
                await message.answer_audio(
                    audio=types.InputFile(processed_audio_path),
                    caption=f"Изменение тональности: {custom_pitch}"
                )
            logging.info(f"Файл {processed_audio_path} успешно отправлен пользователю {user_id}")
        except Exception as e:
            logging.exception(f"Ошибка отправки custom pitch: {e}")
            await message.answer(f"Не удалось отправить файл: {e}")
            # Файлы все равно удаляем ниже

        await state.finish()

    except ValueError:
        await message.reply("Неверный формат. Пожалуйста, введите число (например, -1.5 или 3).")
        # Не завершаем состояние, чтобы пользователь мог попробовать снова
    except Exception as e:
        logging.exception(f"Критическая ошибка в process_custom_pitch_input: {e}")
        await message.answer("Произошла непредвиденная ошибка при обработке вашего значения.")
        await state.finish() # Завершаем состояние при критической ошибке
    finally:
        # Очистка файлов после завершения (успешного или с ошибкой отправки)
        # Не очищаем, если была ошибка ValueError, чтобы пользователь мог исправить ввод
        if await state.get_state() is None: # Проверяем, что состояние завершено
             logging.info("Начало очистки временных файлов (custom)...")
             safe_remove_file(processed_audio_path) # Удаляем обработанный файл
             safe_remove_file(original_audio_path)  # Удаляем исходный файл
             logging.info("Очистка временных файлов (custom) завершена.")

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