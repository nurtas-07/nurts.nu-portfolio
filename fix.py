import sys

file_path = "c:\\Users\\Admin\\Desktop\\nurtas-portfolio-bot\\handlers.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(", reply_markup=build_back_keyboard()", "")
content = content.replace("from keyboards import build_back_keyboard, build_hackathon_menu, build_main_menu", "from keyboards import build_hackathon_menu, build_main_menu")
content = content.replace('HACKATHON_BACK_BUTTON = "⬅️ Назад в меню"\n\n', "")
content = content.replace('HACKATHON_BACK_BUTTON = "⬅️ Назад в меню"\n', "")

logic_to_remove = """        if text == HACKATHON_BACK_BUTTON:
            bot.send_message(message.chat.id, "Главное меню:", reply_markup=build_main_menu())
            return

"""
content = content.replace(logic_to_remove, "")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
