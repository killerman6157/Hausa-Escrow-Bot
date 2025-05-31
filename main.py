import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# ✅ Load variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# ✅ Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Deal memory (temporary)
deal_state = {
    "buyer_wallet": None,
    "seller_account": None,
    "status": "idle"
}

# 🟢 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        [KeyboardButton("/startdeal"), KeyboardButton("/track")],
        [KeyboardButton("/howitworks"), KeyboardButton("📞 Tuntuɓi Admin")]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 *Barka da zuwa Hausa Escrow Bot!*\n\n"
        "🔐 Muna kare kuɗinka da kayanka har sai an tabbatar da juna.\n"
        "⚠️ Kada ka tura kuɗi kai tsaye. Yi amfani da bot domin amana da tsaro.\n\n"
        "/startdeal - Fara sabuwar ciniki\n"
        "/track - Duba matsayin ciniki\n"
        "/howitworks - Yadda escrow ke aiki\n"
        "/confirm - Buyer ya tabbatar da biya\n"
        "/received - Buyer ya tabbatar da karɓar kaya\n"
        "/dispute - Idan matsala ta taso",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# 🟢 /startdeal
async def startdeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_state.update({
        "buyer_wallet": None,
        "seller_account": None,
        "status": "awaiting_info"
    })
    await update.message.reply_text("✅ An fara sabuwar ciniki. Buyer da Seller su saka bayanansu daidai.")

# 🟢 /buyer <wallet>
async def buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        deal_state["buyer_wallet"] = ' '.join(context.args)
        deal_state["status"] = "awaiting_seller"
        await update.message.reply_text("✅ An karɓi wallet address na Buyer. Jira Seller ya saka bayanansa.")
    else:
        await update.message.reply_text("❗ Rubuta kamar haka: /buyer <wallet address>")

# 🟢 /seller <bank + account>
async def seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        deal_state["seller_account"] = ' '.join(context.args)
        deal_state["status"] = "awaiting_payment"
        await update.message.reply_text(
            "✅ An karɓi account na Seller.\n\n"
            "📌 Buyer: Da fatan ka tura kuɗi zuwa:\n"
            "🏦 Opay - 9131085651 - Bashir Rabiu\n"
            "💠 TRC20 Wallet: `TRjqMH6ckyNVaCBXNDkKitq1phCV1YSugg`\n\n"
            "🟢 Bayan ka tura, rubuta: /confirm",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❗ Rubuta kamar haka: /seller Opay 1234567890 - Sunanka")

# 🟢 /confirm
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if deal_state["status"] == "awaiting_payment":
        deal_state["status"] = "awaiting_delivery"
        await update.message.reply_text("💰 Buyer ya tabbatar da biyan kuɗi. Admin zai tabbatar sannan ya sanar da Seller.")
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text="📥 Buyer ya ce ya tura kuɗi. A duba sannan a sanar da Seller da ya tura kaya."
            )
    else:
        await update.message.reply_text("⛔ Ba'a kai matakin biyan kuɗi ba.")

# 🟢 /received
async def received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if deal_state["status"] == "awaiting_delivery":
        deal_state["status"] = "completed"
        await update.message.reply_text("📦 Buyer ya tabbatar da karɓar kaya. Admin zai tura kuɗi zuwa Seller.")
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text="✅ Buyer ya karɓi kaya. Don Allah a tura kuɗi zuwa Seller yanzu."
            )
    else:
        await update.message.reply_text("⛔ Ba'a kai matakin karɓar kaya ba.")

# 🟢 /howitworks
async def how_it_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *YADDA BOT ƊIN ESCROW KE AIKI:*\n\n"
        "1️⃣ Buyer da Seller su ƙirƙiri group, su ƙara bot\n"
        "2️⃣ Buyer: `/buyer <wallet address>`\n"
        "3️⃣ Seller: `/seller <bank account>`\n"
        "4️⃣ Buyer ya tura kuɗi zuwa Escrow, sannan ya rubuta `/confirm`\n"
        "5️⃣ Admin ya tabbatar, ya sanar da Seller da ya tura kaya\n"
        "6️⃣ Buyer ya rubuta `/received` idan ya karɓa\n"
        "7️⃣ Admin zai tura kuɗi zuwa Seller.\n\n"
        "🏦 Escrow Account: Opay 9131085651 - Bashir Rabiu\n"
        "💠 Wallet: TRjqMH6ckyNVaCBXNDkKitq1phCV1YSugg",
        parse_mode="Markdown"
    )

# 🟢 /track
async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📍 *Matsayin Ciniki:*\n"
        f"🔹 Buyer Info: {'✅' if deal_state['buyer_wallet'] else '⏳'}\n"
        f"🔹 Seller Info: {'✅' if deal_state['seller_account'] else '⏳'}\n"
        f"💰 Payment: {'✅' if deal_state['status'] in ['awaiting_delivery', 'completed'] else '⏳'}\n"
        f"📦 Delivery: {'✅' if deal_state['status'] == 'completed' else '⏳'}\n"
        f"🔒 Status: {deal_state['status'].replace('_', ' ').title()}",
        parse_mode="Markdown"
    )

# 🟢 /dispute
async def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ An samu matsala. Don Allah a tuntuɓi admin kai tsaye.")

# 🟢 📞 Tuntuɓi Admin (button)
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📞 Tuntuɓar admin kai tsaye:\n👉 {ADMIN_ID}")

# 🛑 Error Handler
async def error_handler(update: object, context: CallbackContext):
    logger.error("Exception while handling update:", exc_info=context.error)

# ✅ Application Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startdeal", startdeal))
app.add_handler(CommandHandler("buyer", buyer))
app.add_handler(CommandHandler("seller", seller))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("received", received))
app.add_handler(CommandHandler("howitworks", how_it_works))
app.add_handler(CommandHandler("track", track))
app.add_handler(CommandHandler("dispute", dispute))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Tuntuɓi Admin"), contact_admin))
app.add_error_handler(error_handler)

# 🔁 Run bot
app.run_polling()
