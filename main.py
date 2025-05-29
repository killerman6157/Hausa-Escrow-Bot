import os
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Load environment variables from .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(API_TOKEN)

user_state = {}
banned_users = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id in banned_users:
        bot.send_message(message.chat.id, "🚫 An hana ka amfani da bot.")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🛒 Fara Escrow Deal"))
    bot.send_message(
        message.chat.id,
        "Barka da zuwa **Hausa Escrow Bot**!\nDanna ƙasa don fara ma'amala:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🛒 Fara Escrow Deal")
def start_deal(message):
    user_state[message.chat.id] = {'step': 'awaiting_seller'}
    bot.send_message(message.chat.id, "✍️ Mataki na 1: Shigar da **@username** na seller.")

@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id]['step'] == 'awaiting_seller')
def ask_payment(message):
    user_state[message.chat.id]['seller'] = message.text
    user_state[message.chat.id]['step'] = 'awaiting_proof'
    info = (
        f"🔐 Escrow Deal Da Aka Fara!\n"
        f"Seller: {message.text}\n\n"
        f"Buyer zai biya admin account:\n"
        f"🏦 GTBank: 0909854431 - Bashir Rabiu\n\n"
        "Bayan biya, danna **💸 Na biya Admin**"
    )
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("💸 Na biya Admin"))
    bot.send_message(message.chat.id, info, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"📥 Sabon deal - Buyer @{message.from_user.username} da seller {message.text}")

@bot.message_handler(func=lambda m: m.text == "💸 Na biya Admin")
def confirm_payment_by_buyer(message):
    bot.send_message(ADMIN_ID,
        f"⚠️ Buyer @{message.from_user.username} ya ce ya biya. Yi /confirm_{message.chat.id}"
    )
    bot.send_message(message.chat.id, "✅ Mun sanar da admin, don Allah jira tabbatarwa.")

@bot.message_handler(func=lambda m: m.text.startswith("/confirm_"))
def admin_confirm(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split("_")[1])
        bot.send_message(user_id,
            "✅ Admin ya tabbatar biyan ka.\n"
            "Sai seller ya turo kaya.\n"
            "Danna **✅ Na karɓa** idan ka samu kaya.",
            parse_mode="Markdown"
        )
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("✅ Na karɓa"))
        bot.send_message(user_id, "Danna lokacin karɓa:", reply_markup=markup)
        seller = user_state.get(user_id, {}).get('seller', 'Unknown')
        bot.send_message(ADMIN_ID, f"📦 Sanar seller {seller} ya turo kaya ga buyer.")
    except:
        bot.send_message(message.chat.id, "❌ Kuskure a /confirm command.")

@bot.message_handler(func=lambda m: m.text == "✅ Na karɓa")
def item_received(message):
    bot.send_message(ADMIN_ID,
        f"✅ Buyer @{message.from_user.username} ya tabbatar da karɓar kaya.\n"
        "Yi release na kudin ga seller."
    )
    bot.send_message(message.chat.id, "🎉 Mun gode! Admin zai saki kudin seller yanzu.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.split()[1])
        banned_users.add(uid)
        bot.send_message(message.chat.id, f"🚫 An haramta user {uid}.")
    except:
        bot.send_message(message.chat.id, "Amfani: /ban USER_ID")

bot.polling()
