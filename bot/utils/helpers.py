def validate_pitch_input(user_input):
    try:
        pitch_value = float(user_input)
        if pitch_value < -4 or pitch_value > 4:
            return False
        return True
    except ValueError:
        return False

def format_response_message(pitch_options):
    response = "Выберите один из следующих вариантов изменения тона:\n"
    for index, option in enumerate(pitch_options):
        response += f"{index + 1}: {option} полутонов\n"
    return response

def create_audio_preview_message(pitch_value):
    return f"Вы выбрали изменение тона на {pitch_value} полутонов. Вот ваш предварительный фрагмент!"