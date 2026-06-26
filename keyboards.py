from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def build_main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.add(
        KeyboardButton("Обо мне"),
        KeyboardButton("Цель"),
        KeyboardButton("Как я начал"),
    )
    keyboard.add(
        KeyboardButton("Ментор"),
        KeyboardButton("Путь A→B"),
        KeyboardButton("Хобби"),
    )
    keyboard.add(
        KeyboardButton("Лучшие работы"),
        KeyboardButton("GitHub"),
        KeyboardButton("🏆 Достижения"),
    )
    keyboard.add(
        KeyboardButton("🔥 Вайб хакатонов"),
        KeyboardButton("💡 Мои стартапы"),
    )
    return keyboard


def build_hackathon_menu(hackathons: dict) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for slug, data in hackathons.items():
        title = data.get("title", slug.replace("_", " ").title())
        keyboard.add(KeyboardButton(title))
    return keyboard
