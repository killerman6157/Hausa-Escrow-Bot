import os
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()  # Load variables from .env

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

bot = telebot.TeleBot(API_TOKEN)

user_state = {}
banned_users = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id in banned_users:
        bot.send_message(message.chat.id, "🚫 Ka haramtawa daga amfani da bot.")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🛒 Fara Escrow Deal"))
    bot.send_message(
        message.chat.id,
        "Barka da zuwa **Hausa Escrow Bot**!
Danna ƙasa don fara ma'amala:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ... (rest of handlers remain unchanged, using API_TOKEN, ADMIN_ID, LOG_CHANNEL_ID)

bot.polling()
