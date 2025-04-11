from typing import List, Tuple
import librosa
import numpy as np
import soundfile as sf
import os

def change_pitch(audio_path: str, pitch_shift: int) -> np.ndarray:
    y, sr = librosa.load(audio_path, sr=None)
    y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=pitch_shift)
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

def process_audio_file(audio_path: str, output_dir: str, pitch_shift: int) -> str:
    audio_data, sr = change_pitch(audio_path, pitch_shift)
    output_path = os.path.join(output_dir, 'output_pitch_shifted.mp3')
    sf.write(output_path, audio_data, sr)
    return output_path