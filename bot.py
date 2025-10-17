import telebot
from telebot import types
import re
import os
import json

TOKEN = "7971738148:AAHzMoMs0Zve7p5mce_nizxD98EWnh5Dpsk"
CHANNEL_ID = "@NIS_TG"

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "lesson_schedules.json"

# --- Загружаем/сохраняем базу расписаний ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lesson_schedules = json.load(f)
else:
    lesson_schedules = {}

def save_schedules():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(lesson_schedules, f, ensure_ascii=False, indent=4)

# --- Обработка новых постов в канале ---
@bot.channel_post_handler(content_types=['document'])
def handle_new_schedule(message):
    if message.chat.username == CHANNEL_ID.lstrip("@"):
        file_name = message.document.file_name
        match = re.search(r"(\d{1,2})\s*қазан", file_name.lower())
        if match:
            day = int(match.group(1))
            date_str = f"{day:02d}.10.2025"
            file_id = message.document.file_id
            lesson_schedules[date_str] = file_id
            save_schedules()
            print(f"[✅] Добавлено расписание уроков на {date_str}")
        else:
            print(f"[⚠️] Файл не содержит дату: {file_name}")

# --- Главное меню ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📅 Расписание"))
    bot.send_message(message.chat.id,
                     "Привет! Я NISHELP 🤖\nВыбери, что тебе нужно:",
                     reply_markup=markup)

# --- Подменю "Расписание" ---
@bot.message_handler(func=lambda m: m.text == "📅 Расписание")
def show_schedule_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📘 Расписание СОР"))
    markup.add(types.KeyboardButton("📗 Расписание СОЧ"))
    markup.add(types.KeyboardButton("📙 Расписание уроков"))
    markup.add(types.KeyboardButton("🔙 Назад"), types.KeyboardButton("🏠 Главное меню"))
    bot.send_message(message.chat.id, "Выбери тип расписания:", reply_markup=markup)

# --- Подменю "Расписание уроков" ---
@bot.message_handler(func=lambda m: m.text == "📙 Расписание уроков")
def show_lessons_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    days = [
        "🗓 20.10.2025 — Понедельник",
        "🗓 21.10.2025 — Вторник",
        "🗓 22.10.2025 — Среда",
        "🗓 23.10.2025 — Четверг",
        "🗓 24.10.2025 — Пятница",
        "🗓 25.10.2025 — Суббота"
    ]
    for d in days:
        markup.add(types.KeyboardButton(d))
    markup.add(types.KeyboardButton("🔙 Назад"), types.KeyboardButton("🏠 Главное меню"))
    bot.send_message(message.chat.id, "Выбери день недели:", reply_markup=markup)

# --- Отправляем нужное расписание ---
@bot.message_handler(func=lambda m: "🗓" in m.text)
def send_day_schedule(message):
    date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", message.text)
    if date_match:
        date_str = date_match.group(1)
        if date_str in lesson_schedules:
            bot.send_document(message.chat.id, lesson_schedules[date_str],
                              caption=f"📅 Расписание уроков на {date_str}")
        else:
            bot.send_message(message.chat.id, f"❌ Расписание на {date_str} не найдено.")
    else:
        bot.send_message(message.chat.id, "Ошибка при определении даты.")

# --- СОР и СОЧ подменю (оставляем без изменений) ---
@bot.message_handler(func=lambda m: m.text == "📘 Расписание СОР")
def show_sor_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 5):
        markup.add(types.KeyboardButton(f"📘 {i}-четверть"))
    markup.add(types.KeyboardButton("🔙 Назад"), types.KeyboardButton("🏠 Главное меню"))
    bot.send_message(message.chat.id, "Выбери четверть для СОР:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📗 Расписание СОЧ")
def show_soch_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(1, 5):
        markup.add(types.KeyboardButton(f"📗 {i}-четверть"))
    markup.add(types.KeyboardButton("🔙 Назад"), types.KeyboardButton("🏠 Главное меню"))
    bot.send_message(message.chat.id, "Выбери четверть для СОЧ:", reply_markup=markup)

# --- Кнопки "Назад" и "Главное меню" ---
@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back_to_main(message):
    show_schedule_menu(message)

@bot.message_handler(func=lambda m: m.text == "🏠 Главное меню")
def go_home(message):
    start(message)

print("✅ Бот запущен и автоматически отслеживает канал @NIS_TG")
bot.polling(none_stop=True)

