from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_pitch_selection_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    pitch_options = [-4, -2, 0, 2, 4]
    
    for option in pitch_options:
        button = InlineKeyboardButton(text=f"Pitch {option}", callback_data=f"pitch_{option}")
        keyboard.add(button)
    
    return keyboard

def create_custom_pitch_keyboard():
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Введите точное значение", callback_data="custom_pitch")
    keyboard.add(button)
    
    return keyboard