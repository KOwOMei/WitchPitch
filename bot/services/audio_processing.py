from typing import List, Tuple
import librosa
import numpy as np
import soundfile as sf
import os

def change_pitch(audio_path: str, pitch_shift: int) -> Tuple[np.ndarray, int]:
    y, sr = librosa.load(audio_path, sr=None)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)
    return y_shifted, sr

def generate_pitch_variants(audio_path: str) -> List[Tuple[np.ndarray, int]]:
    pitch_shifts = [-4, -2, 0, 2, 4]
    variants = []
    
    for shift in pitch_shifts:
        variant, sr = change_pitch(audio_path, shift)
        variants.append((variant, sr))
    
    return variants

def save_audio_segment(audio_data: np.ndarray, sr: int, output_path: str, duration: float = 30.0) -> None:
    max_samples = int(sr * duration)
    audio_segment = audio_data[:max_samples]
    sf.write(output_path, audio_segment, sr)

def process_audio_file(audio_path: str, pitch_shift: int, output_dir: str = "temp") -> str:
    """Обработка полного аудиофайла с изменением тональности"""
    import os
    
    # Создаем директорию для вывода, если её нет
    os.makedirs(output_dir, exist_ok=True)
    
    # Изменяем тональность
    y_shifted, sr = change_pitch(audio_path, pitch_shift)
    
    # Определяем путь для сохранения
    output_path = os.path.join(output_dir, f"processed_audio_{pitch_shift}.mp3")
    
    # Сохраняем аудиофайл
    sf.write(output_path, y_shifted, sr)
    
    return output_path