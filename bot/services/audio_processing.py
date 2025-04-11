from typing import List, Tuple, Optional
import librosa
import numpy as np
import soundfile as sf
import os
import logging

def change_pitch(audio_path: str, pitch_shift: int) -> Optional[Tuple[np.ndarray, int]]:
    try:
        logging.info(f"Загрузка файла: {audio_path}")
        y, sr = librosa.load(audio_path, sr=None)
        logging.info(f"Файл загружен. sr={sr}, shape={y.shape}")

        logging.info(f"Применение pitch shift: n_steps={pitch_shift}")
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
        logging.info(f"Pitch shift применен. Новая shape={y_shifted.shape}")

        return y_shifted, sr
    except Exception as e:
        # Логируем ошибку, возникшую при загрузке или обработке
        logging.exception(f"Ошибка в change_pitch для файла {audio_path}: {e}")
        return None # Возвращаем None при ошибке


def generate_pitch_variants(audio_path: str) -> List[Tuple[np.ndarray, int]]:
    pitch_shifts = [-4, -3, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 3, 4]
    variants = []
    
    for shift in pitch_shifts:
        result = change_pitch(audio_path, shift)
        if result: # Проверяем, что change_pitch не вернул None
            variants.append(result)
    
    return variants

def save_audio_segment(audio_data: np.ndarray, sr: int, output_path: str, duration: float = 30.0) -> None:
    max_samples = int(sr * duration)
    audio_segment = audio_data[:max_samples]
    sf.write(output_path, audio_segment, sr)

async def process_audio_file(audio_path: str, pitch_shift: int, output_dir: str = "temp") -> Optional[str]:
    """Обработка полного аудиофайла с изменением тональности"""
    import asyncio

    # Создаем директорию для вывода, если её нет
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Не удалось создать директорию {output_dir}: {e}")
        return None

    # Выполняем тяжелую операцию в отдельном потоке
    def process():
        try:
            # Изменяем тональность
            logging.info(f"Вызов change_pitch для {audio_path} с shift={pitch_shift}...")
            result = change_pitch(audio_path, pitch_shift)
            logging.info(f"Результат change_pitch для {audio_path}: {'Успех' if result else 'Ошибка'}")

            if result is None: # Проверяем результат change_pitch
                logging.error(f"Функция change_pitch вернула None для {audio_path}")
                return None

            y_shifted, sr = result
            # Определяем путь для сохранения
            output_filename = f"processed_{os.path.basename(audio_path).split('.')[0]}_{pitch_shift}.mp3"
            output_path = os.path.join(output_dir, output_filename)
            logging.info(f"Путь для сохранения: {output_path}")

            # Сохраняем аудиофайл
            sf.write(output_path, y_shifted, sr)
            logging.info(f"Файл успешно сохранен: {output_path}")
            return output_path
        except Exception as e:
            # Логируем любую ошибку, возникшую внутри потока
            logging.exception(f"Ошибка внутри потока process для файла {audio_path}: {e}")
            return None

    # Запускаем в пуле потоков, чтобы не блокировать основной цикл событий
    try:
        result_path = await asyncio.get_event_loop().run_in_executor(None, process)
        return result_path
    except Exception as e:
        # Логируем ошибку, если что-то пошло не так с самим run_in_executor
        logging.exception(f"Ошибка при выполнении run_in_executor: {e}")
        return None