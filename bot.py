import telebot
from telebot import types
import threading
import time
from datetime import datetime

# --- НАСТРОЙКИ ---
API_TOKEN = '7971738148:AAHzMoMs0Zve7p5mce_nizxD98EWnh5Dpsk'
ADMIN_ID = 8394974203

bot = telebot.TeleBot(API_TOKEN)

# --- ГЛАВНОЕ МЕНЮ ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_schedule = types.KeyboardButton("📅 Расписание")
    btn_materials = types.KeyboardButton("📚 Учебные материалы")
    btn_reminder = types.KeyboardButton("⏰ Напоминалка")
    btn_summary = types.KeyboardButton("📝 ИИ-Конспект")
    btn_feedback = types.KeyboardButton("💬 Обратная связь")
    markup.add(btn_schedule, btn_materials)
    markup.add(btn_reminder, btn_summary)
    markup.add(btn_feedback)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = "(ВСЁ ЕЩЕ В РАЗРАБОТКЕ) Привет! Я EduHelpBot. Выбери нужный раздел 👇"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# --- МОДУЛЬ: РАСПИСАНИЕ ---
@bot.message_handler(func=lambda message: message.text == "📅 Расписание")
def send_schedule_info(message):
    img_url = "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/53/55/25/535525a8-6ff1-c310-f8b7-ef09fbda9530/Placeholder.mill/1200x630wa.jpg"
    caption = (
        "📍 Используй приложение **EduPage**:\n\n"
        "🔗 [Android](https://play.google.com/store/apps/details?id=air.org.edupage)\n"
        "🔗 [iOS](https://apps.apple.com/ru/app/edupage/id569428005)"
    )
    bot.send_photo(message.chat.id, img_url, caption=caption, parse_mode="Markdown")

# --- МОДУЛЬ: УЧЕБНЫЕ МАТЕРИАЛЫ ---
@bot.message_handler(func=lambda message: message.text == "📚 Учебные материалы")
def send_materials_info(message):
    caption = (
        "📍 Учебные материалы в **NIS Online**:\n\n"
        "🔗 [Android](https://play.google.com/store/apps/details?id=kz.nis.cep.nisonline)\n"
        "🔗 [iOS](https://apps.apple.com/kz/app/nis-online/id6447827174)"
    )
    bot.send_message(message.chat.id, caption, parse_mode="Markdown")

# --- МОДУЛЬ: НАПОМИНАЛКА ---
@bot.message_handler(func=lambda message: message.text == "⏰ Напоминалка")
def reminder_start(message):
    msg = bot.send_message(
        message.chat.id,
        "📝 Введите напоминание в формате:\n\n"
        "Текст | ДД.ММ.ГГГГ ЧЧ:ММ\n\n"
        "📌 Пример:\n"
        "СОР по математике | 25.12.2025 15:30"
    )
    bot.register_next_step_handler(msg, process_reminder)

def process_reminder(message):
    try:
        text, date_str = message.text.split("|")
        text = text.strip()
        date_str = date_str.strip()

        reminder_time = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        now = datetime.now()

        if reminder_time <= now:
            bot.send_message(message.chat.id, "❌ Это время уже прошло.")
            return

        delay = (reminder_time - now).total_seconds()

        threading.Thread(
            target=send_reminder,
            args=(message.chat.id, text, delay),
            daemon=True
        ).start()

        bot.send_message(
            message.chat.id,
            f"✅ Напоминание установлено!\n\n"
            f"🕒 {date_str}\n"
            f"📌 {text}"
        )

    except Exception:
        bot.send_message(
            message.chat.id,
            "❌ Ошибка формата.\n\nИспользуй:\nТекст | ДД.ММ.ГГГГ ЧЧ:ММ"
        )

def send_reminder(chat_id, text, delay):
    time.sleep(delay)
    bot.send_message(
        chat_id,
        f"⏰ **НАПОМИНАНИЕ**\n\n{text}",
        parse_mode="Markdown"
    )

# --- МОДУЛЬ: ИИ-КОНСПЕКТ ---
@bot.message_handler(func=lambda message: message.text == "📝 ИИ-Конспект")
def summary_start(message):
    msg = bot.send_message(message.chat.id, "ТЕХНИЧЕСКИЕ НЕПОЛАДКИ")
    bot.register_next_step_handler(msg, process_summary)

# --- МОДУЛЬ: ОБРАТНАЯ СВЯЗЬ ---
@bot.message_handler(func=lambda message: message.text == "💬 Обратная связь")
def feedback_start(message):
    msg = bot.send_message(message.chat.id, "Напиши сообщение создателю.")
    bot.register_next_step_handler(msg, send_to_admin)

def send_to_admin(message):
    try:
        bot.send_message(
            ADMIN_ID,
            f"📩 Сообщение от @{message.from_user.username}:\n\n{message.text}"
        )
        bot.send_message(message.chat.id, "✅ Сообщение отправлено.")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка отправки.")

# --- ЗАПУСК ---
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
