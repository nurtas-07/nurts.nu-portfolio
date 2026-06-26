from typing import Dict
import os
import requests
from pathlib import Path

import telebot
from telebot.types import InputMediaPhoto

# AI integration removed per user request
from keyboards import build_hackathon_menu, build_main_menu
from validators import extract_hackathon_slug, is_valid_question

# removed pending_questions and AI question flow

MAIN_BUTTONS = {
    "Обо мне": "about",
    "Цель": "goal",
    "Как я начал": "how_i_started",
    "Ментор": "mentor",
    "Путь A→B": "point_a_to_b",
    "Хобби": "hobbies",
    "Лучшие работы": "best_works",
    "GitHub": "github_link",
    "🏆 Достижения": "achievements",
    "🔥 Вайб хакатонов": "hackathons",
    "💡 Мои стартапы": "startups",
}


def _format_best_works(best_works):
    if not isinstance(best_works, list):
        return str(best_works)
    lines = []
    for item in best_works:
        title = item.get("title", "Без названия")
        description = item.get("description", "")
        link = item.get("link", "")
        # Only include link text if it looks like an external URL
        if isinstance(link, str) and link.startswith("http"):
            lines.append(f"• {title}: {description}\n  {link}")
        else:
            lines.append(f"• {title}: {description}")
    return "\n\n".join(lines)


def _resolve_path(p: str) -> str:
    """Return an absolute path for a photo path `p`. Try as given, then relative to project root."""
    if not p:
        raise FileNotFoundError("Empty path")
    if os.path.isabs(p) and os.path.exists(p):
        return p
    # Try project root relative
    base = Path(__file__).resolve().parent
    cand = (base / p).resolve()
    if cand.exists():
        return str(cand)
    # Also try one level up (if paths reference from project root differently)
    cand2 = (base.parent / p).resolve()
    if cand2.exists():
        return str(cand2)
    # Last attempt: return original so open will raise FileNotFoundError
    return p


def _build_profile_text(key: str, content: dict) -> str:
    if key == "best_works":
        return _format_best_works(content.get("best_works", []))
    return str(content.get(key, "Пока нет данных для этого раздела."))


def _send_section(bot, chat_id, key, content):
    # For best_works, send media when available instead of printing local paths
    if key == "best_works":
        works = content.get("best_works", [])
        if not works:
            bot.send_message(chat_id, "Пока нет лучших работ.")
            return

        for item in works:
            title = item.get("title", "Без названия")
            description = item.get("description", "")
            caption_lines = [f"*{title}*", description]
            link = item.get("link", "")
            if isinstance(link, str) and link.startswith("http"):
                caption_lines.append(link)
            caption = "\n\n".join(line for line in caption_lines if line)

            photos = item.get("photos") or item.get("photo") or []
            try:
                if isinstance(photos, str):
                    photos = [photos]
                if photos:
                    if len(photos) == 1:
                        p0 = _resolve_path(photos[0])
                        with open(p0, "rb") as pf:
                            bot.send_photo(chat_id, pf, caption=caption, parse_mode=None, timeout=60)
                    else:
                        files = []
                        media = []
                        for p in photos:
                            ppath = _resolve_path(p)
                            try:
                                f = open(ppath, "rb")
                                files.append(f)
                                media.append(InputMediaPhoto(f))
                            except FileNotFoundError:
                                print(f"Best work photo not found: {ppath}")
                        if media:
                            try:
                                bot.send_media_group(chat_id, media, timeout=60)
                                bot.send_message(chat_id, caption)
                            finally:
                                for f in files:
                                    try:
                                        f.close()
                                    except Exception:
                                        pass
                        else:
                            bot.send_message(chat_id, caption)
                else:
                    bot.send_message(chat_id, caption)
            except FileNotFoundError:
                bot.send_message(chat_id, caption + "\n(Фото не найдены)")
            except Exception as exc:
                bot.send_message(chat_id, "Произошла ошибка при отправке работы.")
                print(f"Error sending best work: {exc}")
        return

    text = _build_profile_text(key, content)
    bot.send_message(chat_id, text)


def _send_achievements(bot, chat_id, content):
    achievements = content.get("achievements", [])
    if not achievements:
        bot.send_message(chat_id, "Пока нет доступных достижений.")
        return
    formatted = "\n".join(f"{item}" for item in achievements)
    bot.send_message(chat_id, formatted)


def _send_startups(bot, chat_id, startups):
    """Send list of startups with links and photos if available."""
    if not startups:
        bot.send_message(chat_id, "Пока нет доступных стартапов.")
        return
    
    for slug, item in startups.items():
        title = item.get("title", "Без названия")
        description = item.get("description", "")
        link = item.get("link", "")
        
        caption_lines = [f"*{title}*", description]
        if isinstance(link, str) and link.startswith("http"):
            caption_lines.append(link)
        caption = "\n\n".join(line for line in caption_lines if line)
        
        photos = item.get("photos", [])
        try:
            if isinstance(photos, str):
                photos = [photos]
            if photos:
                if len(photos) == 1:
                    ppath = _resolve_path(photos[0])
                    with open(ppath, "rb") as pf:
                        bot.send_photo(chat_id, pf, caption=caption, parse_mode=None, timeout=60)
                else:
                    files = []
                    media = []
                    for p in photos:
                        try:
                            ppath = _resolve_path(p)
                            f = open(ppath, "rb")
                            files.append(f)
                            media.append(InputMediaPhoto(f))
                        except FileNotFoundError:
                            print(f"Startup photo not found: {p}")
                    if media:
                        try:
                            bot.send_media_group(chat_id, media, timeout=60)
                            bot.send_message(chat_id, caption)
                        finally:
                            for f in files:
                                try:
                                    f.close()
                                except Exception:
                                    pass
                    else:
                        bot.send_message(chat_id, caption)
            else:
                bot.send_message(chat_id, caption)
        except Exception as exc:
            bot.send_message(chat_id, "Произошла ошибка при отправке стартапа.")
            print(f"Error sending startup: {exc}")


def _send_hackathon_detail(bot, chat_id, hackathons, slug):
    item = hackathons.get(slug)
    if not item:
        bot.send_message(chat_id, "Хакатон не найден. Попробуйте выбрать другой.")
        return

    caption_lines = [item.get("story", "")]
    if item.get("instagram"):
        caption_lines.append(f"Instagram: {item['instagram']}")
    caption = "\n\n".join(line for line in caption_lines if line)
    photos = item.get("photos", [])
    if not photos:
        bot.send_message(chat_id, caption or "Нет описания для этого хакатона.")
        return

    try:
        if len(photos) == 1:
            p0 = _resolve_path(photos[0])
            with open(p0, "rb") as photo_file:
                bot.send_photo(chat_id, photo_file, caption=caption, timeout=60)
            return

        files = []
        media = []
        for photo in photos:
            ppath = _resolve_path(photo)
            try:
                f = open(ppath, "rb")
                files.append(f)
                media.append(InputMediaPhoto(f))
            except FileNotFoundError:
                print(f"Hackathon photo not found: {ppath}")

        if media:
            try:
                bot.send_media_group(chat_id, media, timeout=60)
                bot.send_message(chat_id, caption)
            finally:
                for f in files:
                    try:
                        f.close()
                    except Exception:
                        pass
    except FileNotFoundError:
        bot.send_message(
            chat_id,
            "Не удалось найти файл фото хакатона. Пожалуйста, проверьте данные в hackathons.json."
        )
    except telebot.apihelper.ApiException as exc:
        bot.send_message(chat_id, "Произошла ошибка при отправке фото. Попробуйте позже.")
        print(f"Telegram API error while sending hackathon photos: {exc}")
    except requests.exceptions.RequestException as exc:
        bot.send_message(chat_id, "Произошла ошибка соединения при загрузке фото (превышено время ожидания). Попробуйте позже.")
        print(f"Network error in hackathon detail: {exc}")
    except Exception as exc:
        bot.send_message(chat_id, "Произошла внутренняя ошибка при отображении хакатона.")
        print(f"Unexpected error in hackathon detail: {exc}")


def _find_hackathon_slug_by_title(title: str, hackathons: dict) -> str | None:
    normalized = title.strip().lower()
    for slug, data in hackathons.items():
        if data.get("title", "").strip().lower() == normalized:
            return slug
    return None


def register_handlers(bot, content, hackathons, startups, profile_context, debug=False):
    @bot.message_handler(commands=["start"])
    def handle_start(message):
        greeting = (
            "Привет! Это портфолио-бот Нуртаса. Выберите раздел меню, чтобы узнать больше обо мне, моих проектах и достижениях."
        )
        bot.send_message(message.chat.id, greeting, reply_markup=build_main_menu())

    @bot.message_handler(commands=["hack"])
    def handle_hack_command(message):
        slug = extract_hackathon_slug(message.text or "")
        if not slug:
            bot.send_message(
                message.chat.id,
                "Команда должна выглядеть так: /hack <slug>. Например: /hack just_build_it"
            )
            return
        _send_hackathon_detail(bot, message.chat.id, hackathons, slug)

    # AI question flow removed — bot no longer answers arbitrary questions

    @bot.message_handler(func=lambda msg: msg.text is not None)
    def handle_text_commands(message):
        text = message.text.strip()

        if text in MAIN_BUTTONS:
            action = MAIN_BUTTONS[text]
            if action == "achievements":
                _send_achievements(bot, message.chat.id, content)
                return
            if action == "hackathons":
                bot.send_message(message.chat.id, "Выберите хакатон:", reply_markup=build_hackathon_menu(hackathons))
                return
            if action == "startups":
                _send_startups(bot, message.chat.id, startups)
                return
            # AI question action removed
            _send_section(bot, message.chat.id, action, content)
            return

        slug = _find_hackathon_slug_by_title(text, hackathons)
        if slug:
            _send_hackathon_detail(bot, message.chat.id, hackathons, slug)
            return

        bot.send_message(
            message.chat.id,
            "Я не понял это сообщение. Выберите раздел в меню либо нажмите /start.",
            reply_markup=build_main_menu(),
        )

    if debug:
        def log_updates(messages):
            for update in messages:
                print("DEBUG update:", update)
        bot.set_update_listener(log_updates)

    return bot
