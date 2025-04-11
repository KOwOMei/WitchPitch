from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_pitch_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text=f"Тон {shift}", callback_data=str(shift))
        for shift in [-4, -2, 0, 2, 4]
    ]
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text="Пользовательский тон", callback_data="custom_pitch"))  
    return keyboard

def create_custom_pitch_keyboard():
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Введите точное значение", callback_data="custom_pitch")
    keyboard.add(button)
    
    return keyboard