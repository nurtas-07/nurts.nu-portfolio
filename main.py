import sys

import telebot
from telebot.apihelper import ApiTelegramException

from config import load_config
from content_loader import load_content, load_hackathons, load_startups
from handlers import register_handlers


def build_profile_context(content: dict) -> str:
    parts = []
    for key, value in content.items():
        if key == "achievements":
            parts.append("Достижения: " + "; ".join(str(item) for item in value))
            continue
        if isinstance(value, list):
            parts.append(key + ": " + "; ".join(str(item) for item in value))
            continue
        parts.append(f"{key}: {value}")
    return "\n".join(parts)


def main() -> None:
    config = load_config(sys.argv[1:])
    print("Запуск Telegram-бота портфолио...")

    if not config["BOT_TOKEN"]:
        print(
            "BOT_TOKEN не задан. Для запуска реального Telegram-бота добавьте BOT_TOKEN в .env или передайте --token=...\n"
            "Но если вам нужно просто установить библиотеки и запустить код, дополнительных действий не требуется."
        )
        content = load_content()
        load_hackathons()
        load_startups()
        print("Контент успешно загружен. Программа завершила работу без подключения к Telegram.")
        return

    bot = telebot.TeleBot(config["BOT_TOKEN"], parse_mode=None)
    if config["DEBUG"]:
        def debug_listener(messages):
            for update in messages:
                print("DEBUG update:", update)
        bot.set_update_listener(debug_listener)

    content = load_content()
    hackathons = load_hackathons()
    startups = load_startups()
    profile_context = build_profile_context(content)

    register_handlers(bot, content, hackathons, startups, profile_context, debug=config["DEBUG"])

    if config["MODE"] != "polling":
        print(f"Режим {config['MODE']} не поддерживается. Переключаюсь на polling.")

    bot.remove_webhook()
    try:
        bot.infinity_polling(skip_pending=True)
    except ApiTelegramException as exc:
        if hasattr(exc, 'error_code') and exc.error_code == 409:
            print(
                "Ошибка 409: конфликт Telegram getUpdates. Убедитесь, что другой бот с этим токеном не запущен, и запустите снова."
            )
        else:
            print(f"Telegram API error: {exc}")
    except Exception as exc:
        print(f"Unexpected polling error: {exc}")


if __name__ == "__main__":
    main()
