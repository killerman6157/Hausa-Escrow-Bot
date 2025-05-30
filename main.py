
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = "@HausaEscrowSupport"
ADMIN_ID = os.getenv("ADMIN_ID")

# Store deal state
deal_state = {
    "buyer_wallet": None,
    "seller_account": None,
    "status": "idle"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[
        KeyboardButton("/startdeal"), 
        KeyboardButton("/track")
    ], [
        KeyboardButton("/howitworks"), 
        KeyboardButton("📞 Tuntuɓi Admin")
    ]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 *Barka da zuwa Hausa Escrow Bot!*

"
        "🔐 Wannan bot yana kare kuɗinka da kayanka har sai an tabbatar da juna.
"
        "⚠️ Kada ka tura kuɗi kai tsaye. Yi amfani da bot domin amana da tsaro.

"
        "Zaɓi daga cikin zaɓuɓɓuka ko rubuta umarni:
"
        "/startdeal - Fara sabuwar ciniki
"
        "/track - Duba matsayin ciniki
"
        "/howitworks - Yadda escrow ke aiki
"
        "/confirm - Buyer ya tabbatar da biya
"
        "/received - Buyer ya tabbatar da karɓar kaya
"
        "/dispute - Idan matsala ta taso",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def how_it_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 *YADDA BOT ƊIN HAUSA ESCROW KE AIKI:*

"
        "1️⃣ Buyer da Seller su ƙirƙiri group, su ƙara bot
"
        "2️⃣ Buyer: `/buyer <wallet address>`
"
        "3️⃣ Seller: `/seller <bank name account number - sunan mai asusu>`
"
        "4️⃣ Buyer ya tura kuɗi zuwa admin, sannan ya rubuta `/confirm`
"
        "5️⃣ Admin ya tabbatar da biyan kuɗi, sai ya sanar da Seller ya tura kaya
"
        "6️⃣ Buyer ya rubuta `/received` idan ya karɓi kaya
"
        "7️⃣ Admin zai tura kuɗi zuwa Seller. Ciniki ya kammala lafiya.

"
        "📞 *Tuntuɓar admin kai tsaye:* @{ADMIN_USERNAME}",
        parse_mode="Markdown"
    )

async def startdeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deal_state["buyer_wallet"] = None
    deal_state["seller_account"] = None
    deal_state["status"] = "awaiting_info"
    await update.message.reply_text("✅ An fara sabuwar ciniki. Buyer da Seller su saka bayanansu.")

async def buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        deal_state["buyer_wallet"] = ' '.join(context.args)
        await update.message.reply_text("✅ An karɓi wallet address na Buyer. Jira Seller ya saka asusun sa.")
        deal_state["status"] = "awaiting_seller"
    else:
        await update.message.reply_text("❗ Rubuta kamar haka: /buyer <wallet address>")

async def seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        deal_state["seller_account"] = ' '.join(context.args)
        await update.message.reply_text("✅ An karɓi account na Seller. Jira Buyer ya tura kuɗi ya danna /confirm.")
        deal_state["status"] = "awaiting_payment"
    else:
        await update.message.reply_text("❗ Rubuta kamar haka: /seller Opay 1234567890 - Sunanka")

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if deal_state["status"] == "awaiting_payment":
        deal_state["status"] = "awaiting_delivery"
        await update.message.reply_text(
            "💰 Buyer ya tabbatar da biyan kuɗi.
"
            "Admin zai tabbatar sannan ya sanar da Seller da ya tura kaya ko crypto."
        )
    else:
        await update.message.reply_text("⛔ Ba'a kai ga matakin biyan kuɗi ba.")

async def received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if deal_state["status"] == "awaiting_delivery":
        deal_state["status"] = "completed"
        await update.message.reply_text(
            "📦 Buyer ya karɓi kaya. Ana jiran admin ya tura kuɗi zuwa Seller.
"
            "🤝 Ciniki zai kammala nan ba da jimawa ba."
        )
    else:
        await update.message.reply_text("⛔ Ba'a kai matakin karɓar kaya ba.")

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📍 *Matsayin Ciniki:*
"
        f"🔹 Buyer Info: {'✅' if deal_state['buyer_wallet'] else '⏳'}
"
        f"🔹 Seller Info: {'✅' if deal_state['seller_account'] else '⏳'}
"
        f"💰 Payment: {'✅' if deal_state['status'] in ['awaiting_delivery', 'completed'] else '⏳'}
"
        f"📦 Delivery: {'✅' if deal_state['status'] == 'completed' else '⏳'}
"
        f"🔒 Status: {deal_state['status'].replace('_', ' ').title()}",
        parse_mode="Markdown"
    )

async def dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"⚠️ Idan ka samu matsala, tuntuɓi admin: {ADMIN_USERNAME}")

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📞 Don tuntuɓar admin kai tsaye:
👉 {ADMIN_USERNAME}")

async def error_handler(update: object, context: CallbackContext):
    logger.error("Exception while handling update:", exc_info=context.error)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("howitworks", how_it_works))
app.add_handler(CommandHandler("startdeal", startdeal))
app.add_handler(CommandHandler("buyer", buyer))
app.add_handler(CommandHandler("seller", seller))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("received", received))
app.add_handler(CommandHandler("track", track))
app.add_handler(CommandHandler("dispute", dispute))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Tuntuɓi Admin"), contact_admin))
app.add_error_handler(error_handler)
app.run_polling()
