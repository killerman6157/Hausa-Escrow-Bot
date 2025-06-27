import os
import random
import string
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
VERIFICATION_GROUP_ID = -1002583803584  # Hausa Escrow Chat ID

# --- ESCROW ACCOUNT DETAILS ---
ESCROW_TRC20_ADDRESS = os.getenv("ESCROW_TRC20_ADDRESS")
ESCROW_NAIRA_BANK = os.getenv("ESCROW_NAIRA_BANK")

# --- Database Configuration ---
DB_NAME = 'escrow_bot.db'

def init_db():
    """Initializes the SQLite database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Create deals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                chat_id INTEGER PRIMARY KEY,
                buyer_id INTEGER,
                buyer_username TEXT,
                buyer_address TEXT,
                seller_id INTEGER,
                seller_username TEXT,
                seller_account TEXT,
                stage TEXT
            )
        ''')
        # Create user_languages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_languages (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'HA'
            )
        ''')
        conn.commit()

def save_deal(deal_data):
    """Saves or updates a deal in the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO deals (chat_id, buyer_id, buyer_username, buyer_address, seller_id, seller_username, seller_account, stage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_data['chat_id'], deal_data['buyer_id'], deal_data['buyer_username'], deal_data['buyer_address'],
            deal_data.get('seller_id'), deal_data.get('seller_username'), deal_data.get('seller_account'), deal_data['stage']
        ))
        conn.commit()

def get_deal(chat_id):
    """Retrieves a deal from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM deals WHERE chat_id = ?', (chat_id,))
        row = cursor.fetchone()
        if row:
            # Map column names to values
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None

def delete_deal(chat_id):
    """Deletes a deal from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM deals WHERE chat_id = ?', (chat_id,))
        conn.commit()

def get_all_deals():
    """Retrieves all deals from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM deals')
        rows = cursor.fetchall()
        deals_dict = {}
        for row in rows:
            columns = [description[0] for description in cursor.description]
            deal_data = dict(zip(columns, row))
            deals_dict[deal_data['chat_id']] = deal_data
        return deals_dict

def save_user_language(user_id, language):
    """Saves or updates a user's language preference."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO user_languages (user_id, language) VALUES (?, ?)', (user_id, language))
        conn.commit()

def get_user_language(user_id):
    """Retrieves a user's language preference, defaulting to Hausa."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM user_languages WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 'HA' # Default to Hausa if not found

# --- Multilingual Messages ---
MESSAGES = {
    "HA": {
        "welcome": "⚜️ Hausa Escrow Bot ⚜️ v.1\n\nBarka da zuwa Hausa Escrow Bot! Wannan bot yana ba da sabis na tsaro (escrow) don cinikayyarka a Telegram. 🔒\n\n💰 *KUDIN ESCROW:*\n- 5% idan kuɗin ya haura $100\n- $5 idan ya ƙasa da $100\n\n🌟 *SABUNTAWA - SHAIDA:*\n✅ CINIKAYYAR DA AKA KAMMALA: 0\n⚖️ RIGIMOMIN DA AKA SASANTA: 0\n\n🛒 Rubuta /buyer address ko /seller account\n📜 Rubuta /menu don ganin dukkan fasaloli\n\n@HausaEscrowBot – Domin ciniki cikin aminci!",
        "start_escrow_button": "🚀 Fara Escrow",
        "how_it_works_button": "📘 Yadda Escrow ke aiki",
        "security_guide_button": "💬 Jagorar Tsaro",
        "contact_admin_button": "📞 Tuntuɓi Admin",
        "create_group_button": "👥 Fara Ciniki (Create Group)",

        "how_it_works_text": "📘 *YADDA ESCROW KE AIKI:*\n"
                             "Wannan tsari yana taimakawa wajen tabbatar da aminci ga mai saye da mai siyarwa.\n\n"
                             "1. *Mai Siyarwa (Seller) Ya Bayar da Bayanai:* Mai siyarwa ya bada cikakken bayani kan abin da yake siyarwa ko sabis da yake bayarwa.\n"
                             "2. *Mai Saye (Buyer) Ya Amince Ya Biya:* Mai saye ya tabbatar zai biya kuɗin, amma bai biya kai tsaye ga mai siyarwa ba.\n"
                             "3. *Admin Ya Tabbatar da Biya zuwa Escrow:* Mai saye zai tura kuɗin zuwa asusun escrow (asusun amana) na bot. Admin zai tabbatar cewa kuɗin sun shiga asusun escrow.\n"
                             "4. *Mai Siyarwa Ya Tura Kayan/Sabis:* Bayan Admin ya tabbatar kuɗin suna escrow, mai siyarwa zai tura abin da aka siyarwa ko ya kammala sabis ɗin.\n"
                             "5. *Mai Saye Ya Tabbatar da Karɓa:* Mai saye zai tabbatar cewa ya karɓi abin da aka siyar masa kuma yana cikin yanayi mai kyau.\n"
                             "6. *Admin Ya Saki Kuɗi:* Bayan mai saye ya tabbatar, Admin zai saki kuɗin daga asusun escrow zuwa asusun mai siyarwa.\n"
                             "7. *An Kammala Ciniki:* An kammala ciniki cikin nasara da aminci ga duka bangarorin biyu.",
        "security_guide_text": "🛡️ *Jagorar Tsaro da Taimako:*\n🔰 [Fara Ciniki](https://t.me/c/2481223102/27)\n👤 [Buyer Guide](https://t.me/c/2481223102/28)\n💼 [Seller Guide](https://t.me/c/2481223102/29)",
        "back_to_main_menu_button": "⬅️ Komawa Babban Menu",

        "start_deal_prompt": "Danna 👥 *Fara Ciniki* domin ƙirƙirar rukuni. Buyer da Seller su shiga, bot zai jagoranta.",
        "create_group_instructions": "🔐 Don fara ciniki, ku ƙirƙiri rukuni mai suna *{title}*, sannan ku saka bot din: @HausaEscrowBot.\nBuyer da Seller su shiga, bot zai jagoranta.",

        "no_deal_or_stage_mismatch": "❗ Babu bayanin ciniki a nan ko kuma an riga an yi wannan matakin.",
        "buyer_paid_confirm": "💸 @{buyer_username} ya tabbatar da tura kuɗi. Admin zai tabbatar da biya.",
        "admin_payment_notification": "🛂 Buyer @{buyer_username} ya ce ya tura kuɗi a group: `{chat_id}`.\n\nBayanan Buyer: `{buyer_address}`\nBayanan Seller: `{seller_account}`\nDa fatan za ka duba escrow account.",
        "funds_received_button": "✅ Kuɗi Sun Shigo",
        "not_received_cancel_button": "❌ Bai Shigo Ba (Soke Ciniki)",

        "buyer_not_paid_cancel": "❌ @{buyer_username} ya ce bai tura kuɗi ba. An soke cinikin.",
        "admin_only_command": "❌ Wannan umarni na admin ne kawai.",
        "admin_payment_confirmed": "✅ Ka tabbatar da biya. An sanar da @{seller_username} ya tura kayan/kuɗi.",
        "admin_notified_seller_delivery": "✅ Admin ya tabbatar da kuɗi sun shigo. @{seller_username}, da fatan za ka aika kayan/kuɗi zuwa ga @{buyer_username}.\nAddress na Buyer: `{buyer_address}`",
        "seller_delivered_button": "✅ Na Tura Kaya/Kudi",
        "seller_not_delivered_dispute_button": "❌ Ban Tura Ba (Rikici)",

        "admin_cancelled_deal_group": "❗ Admin @{admin_username} ya soke cinikin tsakanin @{buyer_username} da @{seller_username}.",
        "admin_cancelled_deal_message": "❗ Ka soke cinikin a group: `{chat_id}`.",
        "no_such_deal": "❗ Babu wannan cinikin.",

        "seller_delivered_awaiting_buyer": "📦 @{seller_username} ya ce ya tura kayan/kuɗi. Ana jiran amsar @{buyer_username}.",
        "buyer_confirm_receipt_prompt": "📦 @{buyer_username}, @{seller_username} ya ce ya tura kayan/kuɗi. Ka tabbatar ka karɓa?",
        "buyer_received_button": "✅ Na Karɓa",
        "buyer_not_received_dispute_button": "❌ Ban Karɓa Ba (Rikici)",

        "dispute_initiated_group": "⚠️ An fara rikici a group `{chat_id}` tsakanin @{buyer_username} da @{seller_username}. Admin zai shigo.",
        "dispute_initiated_admin_seller": "⚠️ Rikici a cikin group: `{chat_id}`. Seller @{seller_username} ya ce bai tura kayan/kuɗi ba. Tuntuɓi @HausaEscrowSupport don sasanci.",
        "dispute_initiated_admin_buyer": "⚠️ Rikici a cikin group: `{chat_id}`. Buyer @{buyer_username} ya ce bai karɓi kayan/kuɗi ba. Tuntuɓi @HausaEscrowSupport don sasanci.",
        "deal_complete_awaiting_admin_release": "🎉 An kammala ciniki tsakanin @{buyer_username} da @{seller_username}! Admin zai saki kuɗi.",
        "admin_release_notification": "✅ Buyer @{buyer_username} ya tabbatar ya karɓa a group: `{chat_id}`. Da fatan za ka saki kuɗi ga @{seller_username}.",
        "release_funds_button": "✅ Tura Kuɗi ga Seller",
        "stop_trade_button": "❌ Tsayar da Ciniki",

        "admin_released_funds": "✅ Ka saki kuɗi ga @{seller_username} a group: `{chat_id}`.",
        "seller_final_confirm_prompt": "🎉 @{seller_username}, an turawa kuɗinka. Ka tabbatar sun shigo?",
        "seller_final_received_button": "✅ Na Karɓa",
        "seller_final_not_received_button": "❌ Ban Karɓa Ba",

        "deal_successfully_completed": "🎉 An kammala ciniki cikin nasara! @{seller_username} ya tabbatar da karɓar kuɗi.",
        "deal_complete_announcement": "✅ DEAL COMPLETE!\n\n📍BUYER: @{buyer_username}\n📍SELLER: @{seller_username}\n🏦 Buyer Address: `{buyer_address}`\n🏦 Seller Account: `{seller_account}`",

        "seller_final_not_received_dispute_group": "⚠️ An fara rikici a group `{chat_id}`. @{seller_username} ya ce bai karɓi kuɗi ba bayan admin ya saki.",
        "seller_final_not_received_dispute_admin": "⚠️ Rikici a cikin group: `{chat_id}`. Seller @{seller_username} ya ce bai karɓi kuɗi ba. Tuntuɓi @HausaEscrowSupport don sasanci.",

        "buyer_address_prompt": "Da fatan ka saka address ɗinka (misali, TRC20 address, ko Bank Account). Misali: `/buyer TRC20_address` ko `/buyer Bank_Account_Number`",
        "buyer_address_received": "✅ Mun karɓi address ɗin Buyer. Seller, da fatan za ka saka account naka ta amfani da `/seller account_details`",

        "seller_account_prompt": "Da fatan ka saka account number da sunanka. Misali: `/seller Opay 9131085651 Bashir Rabiu`",
        "buyer_not_set_address_or_deal_started": "Buyer bai saka address ba tukuna ko kuma an riga an fara ciniki. Buyer, sai ka fara da `/buyer`",
        "seller_details_received_notify_buyer": "✅ An karɓi bayanan seller. @{buyer_username}, da fatan za ka tura kuɗi zuwa ga **asusun escrow**: \n\n💰 *USDT (TRC20):* `{escrow_trc20_address}`\n🏦 *Naira Bank Account:* `{escrow_naira_bank}`\n\nBayan ka tura kuɗin, sai ka danna maɓallin `✅ Na Tura Kuɗi`.",
        "i_sent_funds_button": "✅ Na Tura Kuɗi",
        "i_did_not_send_button": "❌ Ban Tura Ba",

        "current_status": "📊 Status ɗinka a Hausa Escrow: {status}",
        "no_deal_record": "Babu rikodin ciniki a halin yanzu.",
        "you_are_buyer": "Kai ne *buyer* a ciniki a group: `{chat_id}`. Mataki: *{stage}*.",
        "you_are_seller": "Kai ne *seller* a ciniki a group: `{chat_id}`. Mataki: *{stage}*.",

        "deal_cancelled_message": "❗ Ciniki tsakanin @{buyer_username} da @{seller_username} an tsayar dashi.",
        "no_deal_to_cancel": "❗ Babu bayanin ciniki a nan da za a soke.",

        "choose_language": "Please choose your language / Da fatan zaɓi yarenka:",
        "language_set_ha": "An saita yarenka.",
        "language_set_en": "Your language has been set up."
    },
    "EN": {
        "welcome": "⚜️ Hausa Escrow Bot ⚜️ v.1\n\nWelcome to Hausa Escrow Bot! This bot provides secure (escrow) services for your trades on Telegram. 🔒\n\n💰 *ESCROW FEES:*\n- 5% if the amount exceeds $100\n- $5 if it's less than $100\n\n🌟 *UPDATES - PROOF:*\n✅ COMPLETED TRADES: 0\n⚖️ DISPUTES RESOLVED: 0\n\n🛒 Type /buyer address or /seller account\n📜 Type /menu to see all features\n\n@HausaEscrowBot – For secure trading!",
        "start_escrow_button": "🚀 Start Escrow",
        "how_it_works_button": "📘 How Escrow Works",
        "security_guide_button": "💬 Security Guide",
        "contact_admin_button": "📞 Contact Admin",
        "create_group_button": "👥 Create Trade (Create Group)",

        "how_it_works_text": "📘 *HOW ESCROW WORKS:*\n"
                             "This process helps ensure security for both buyer and seller.\n\n"
                             "1. *Seller Provides Details:* The seller provides full details about the item they are selling or the service they are offering.\n"
                             "2. *Buyer Agrees to Pay:* The buyer confirms they will pay the amount, but they do not pay directly to the seller.\n"
                             "3. *Admin Confirms Payment to Escrow:* The buyer sends the funds to the bot's escrow account (trust account). The admin confirms that the funds have entered the escrow account.\n"
                             "4. *Seller Delivers Goods/Service:* After the admin confirms the funds are in escrow, the seller delivers the item or completes the service.\n"
                             "5. *Buyer Confirms Receipt:* The buyer confirms that they have received the item and it is in good condition.\n"
                             "6. *Admin Releases Funds:* After the buyer confirms, the admin releases the funds from the escrow account to the seller's account.\n"
                             "7. *Trade Completed:* The trade is successfully completed securely for both parties.",
        "security_guide_text": "🛡️ *Security and Support Guide:*\n🔰 [Start Trade](https://t.me/c/2481223102/27)\n👤 [Buyer Guide](https://t.me/c/2481223102/28)\n💼 [Seller Guide](https://t.me/c/2481223102/29)",
        "back_to_main_menu_button": "⬅️ Back to Main Menu",

        "start_deal_prompt": "Click 👥 *Create Trade* to create a group. Buyer and Seller should join, the bot will guide.",
        "create_group_instructions": "🔐 To start a trade, create a group named *{title}*, then add the bot: @HausaEscrowBot.\nBuyer and Seller should join, the bot will guide.",

        "no_deal_or_stage_mismatch": "❗ No deal information here or this stage has already passed.",
        "buyer_paid_confirm": "💸 @{buyer_username} has confirmed sending funds. Admin will confirm payment.",
        "admin_payment_notification": "🛂 Buyer @{buyer_username} said they sent funds in group: `{chat_id}`.\n\nBuyer Info: `{buyer_address}`\nSeller Info: `{seller_account}`\nPlease check the escrow account.",
        "funds_received_button": "✅ Funds Received",
        "not_received_cancel_button": "❌ Not Received (Cancel Deal)",

        "buyer_not_paid_cancel": "❌ @{buyer_username} said they did not send funds. The trade has been cancelled.",
        "admin_only_command": "❌ This command is for admin only.",
        "admin_payment_confirmed": "✅ You have confirmed payment. @{seller_username} has been notified to send the goods/funds.",
        "admin_notified_seller_delivery": "✅ Admin has confirmed funds received. @{seller_username}, please send the goods/funds to @{buyer_username}.\nBuyer's Address: `{buyer_address}`",
        "seller_delivered_button": "✅ I Sent Goods/Funds",
        "seller_not_delivered_dispute_button": "❌ I Did Not Send (Dispute)",

        "admin_cancelled_deal_group": "❗ Admin @{admin_username} has cancelled the trade between @{buyer_username} and @{seller_username}.",
        "admin_cancelled_deal_message": "❗ You have cancelled the trade in group: `{chat_id}`.",
        "no_such_deal": "❗ This trade does not exist.",

        "seller_delivered_awaiting_buyer": "📦 @{seller_username} said they sent the goods/funds. Awaiting @{buyer_username}'s response.",
        "buyer_confirm_receipt_prompt": "📦 @{buyer_username}, @{seller_username} said they sent the goods/funds. Did you receive them?",
        "buyer_received_button": "✅ I Received",
        "buyer_not_received_dispute_button": "❌ I Did Not Receive (Dispute)",

        "dispute_initiated_group": "⚠️ A dispute has been initiated in group `{chat_id}` between @{buyer_username} and @{seller_username}. Admin will intervene.",
        "dispute_initiated_admin_seller": "⚠️ Dispute in group: `{chat_id}`. Seller @{seller_username} said they did not send the goods/funds. Contact @HausaEscrowSupport for mediation.",
        "dispute_initiated_admin_buyer": "⚠️ Dispute in group: `{chat_id}`. Buyer @{buyer_username} said they did not receive the goods/funds. Contact @HausaEscrowSupport for mediation.",
        "deal_complete_awaiting_admin_release": "🎉 Trade completed between @{buyer_username} and @{seller_username}! Admin will release funds.",
        "admin_release_notification": "✅ Buyer @{buyer_username} has confirmed receipt in group: `{chat_id}`. Please release funds to @{seller_username}.",
        "release_funds_button": "✅ Release Funds to Seller",
        "stop_trade_button": "❌ Stop Trade",

        "admin_released_funds": "✅ You have released funds to @{seller_username} in group: `{chat_id}`.",
        "seller_final_confirm_prompt": "🎉 @{seller_username}, your funds have been sent. Please confirm receipt?",
        "seller_final_received_button": "✅ I Received",
        "seller_final_not_received_button": "❌ I Did Not Receive",

        "deal_successfully_completed": "🎉 Trade successfully completed! @{seller_username} has confirmed receiving funds.",
        "deal_complete_announcement": "✅ DEAL COMPLETE!\n\n📍BUYER: @{buyer_username}\n📍SELLER: @{seller_username}\n🏦 Buyer Address: `{buyer_address}`\n🏦 Seller Account: `{seller_account}`",

        "seller_final_not_received_dispute_group": "⚠️ A dispute has been initiated in group `{chat_id}`. @{seller_username} said they did not receive funds after admin released.",
        "seller_final_not_received_dispute_admin": "⚠️ Dispute in group: `{chat_id}`. Seller @{seller_username} said they did not receive funds. Contact @HausaEscrowSupport for mediation.",

        "buyer_address_prompt": "Please enter your address (e.g., TRC20 address, or Bank Account). Example: `/buyer TRC20_address` or `/buyer Bank_Account_Number`",
        "buyer_address_received": "✅ Buyer's address received. Seller, please enter your account using `/seller account_details`",

        "seller_account_prompt": "Please enter your account number and name. Example: `/seller Opay 9131085651 Bashir Rabiu`",
        "buyer_not_set_address_or_deal_started": "Buyer has not entered an address yet or the trade has already started. Buyer, please start with `/buyer`",
        "seller_details_received_notify_buyer": "✅ Seller details received. @{buyer_username}, please send funds to the **escrow account**: \n\n💰 *USDT (TRC20):* `{escrow_trc20_address}`\n🏦 *Naira Bank Account:* `{escrow_naira_bank}`\n\nAfter sending the funds, please click the `✅ I Sent Funds` button.",
        "i_sent_funds_button": "✅ I Sent Funds",
        "i_did_not_send_button": "❌ I Did Not Send",

        "current_status": "📊 Your status in Hausa Escrow: {status}",
        "no_deal_record": "No trade record at the moment.",
        "you_are_buyer": "You are the *buyer* in a trade in group: `{chat_id}`. Stage: *{stage}*.",
        "you_are_seller": "You are the *seller* in a trade in group: `{chat_id}`. Stage: *{stage}*.",

        "deal_cancelled_message": "❗ Trade between @{buyer_username} and @{seller_usern
