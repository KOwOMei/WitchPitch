from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_pitch_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text=f"Тон {shift}", callback_data=str(shift))
        for shift in [-4, -3, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 3, 4]
    ]
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton(text="Пользовательский тон", callback_data="custom_pitch"))  
    return keyboard

def create_custom_pitch_keyboard():
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Введите точное значение", callback_data="custom_pitch")
    keyboard.add(button)
    
    return keyboard