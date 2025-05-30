
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
ADMIN_USERNAME = "@HausaEscrowSupport"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[
        KeyboardButton("/howitworks"),
        KeyboardButton("📞 Tuntuɓi Admin")
    ]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 *Hausa Escrow Bot*\n\n"
        "Zabi daya daga cikin zaɓuɓɓuka ko ka rubuta umarni:\n\n"
        "/howitworks - Yadda bot ɗin ke aiki\n"
        "/buyer <wallet address>\n"
        "/seller <bank details>\n"
        "/confirm - Buyer ya tabbatar\n"
        "/dispute - Idan matsala ta taso",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def how_it_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *YADDA BOT ƊIN KE AIKI*\n\n"
        "1️⃣ Buyer da Seller su kirkiro group su ƙara bot\n"
        "2️⃣ Buyer: /buyer WalletAddress\n"
        "    Seller: /seller BankName AccountNumber – Sunan mai asusu\n"
        "3️⃣ Buyer ya tura kuɗi zuwa admin (escrow)\n"
        "4️⃣ Admin ya tabbatar, seller ya tura kaya/crypto\n"
        "5️⃣ Buyer ya tabbatar da karɓa da /confirm\n"
        "6️⃣ Admin ya tura kuɗi zuwa seller\n"
        "7️⃣ Idan matsala ta faru, a rubuta /dispute",
        parse_mode="Markdown"
    )

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📞 Don tuntuɓar admin kai tsaye:\n👉 {ADMIN_USERNAME}")

async def buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_data['buyer_wallet'] = ' '.join(context.args)
        await update.message.reply_text(f"✅ Buyer wallet address ɗinka: {user_data['buyer_wallet']}")
    else:
        await update.message.reply_text("❗ Don Allah saka wallet address: /buyer <wallet-address>")

async def seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_data['seller_account'] = ' '.join(context.args)
        await update.message.reply_text(f"✅ Seller account ɗinka: {user_data['seller_account']}")
    else:
        await update.message.reply_text("❗ Don Allah saka bayanan asusun: /seller <bank info>")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Buyer ya tabbatar. Ana jiran admin ya tabbatar da ciniki.")

async def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⚠️ An shiga matsala. Tuntuɓi admin: {ADMIN_USERNAME}")

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("howitworks", how_it_works))
app.add_handler(CommandHandler("buyer", buyer))
app.add_handler(CommandHandler("seller", seller))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("dispute", dispute))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Tuntuɓi Admin"), contact_admin))
app.run_polling()
