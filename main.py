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
VERIFICATION_GROUP_ID = -1002583803584  # Hausa Escrow Chat ID[span_0](end_span)

# --- ESCROW ACCOUNT DETAILS ---
[span_1](start_span)ESCROW_TRC20_ADDRESS = os.getenv("ESCROW_TRC20_ADDRESS") #[span_1](end_span)
[span_2](start_span)ESCROW_NAIRA_BANK = os.getenv("ESCROW_NAIRA_BANK") #[span_2](end_span)

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
        "welcome": "⚜️ Hausa Escrow Bot ⚜️ v.1\n\nBarka da zuwa Hausa Escrow Bot! Wannan bot yana ba da sabis na tsaro (escrow) don cinikayyarka a Telegram. [span_3](start_span)🔒\n\n💰 *KUDIN ESCROW:*\n- 5% idan kuɗin ya haura $100\n- $5 idan ya ƙasa da $100\n\n🌟 *SABUNTAWA - SHAIDA:*\n✅ CINIKAYYAR DA AKA KAMMALA: 0\n⚖️ RIGIMOMIN DA AKA SASANTA: 0\n\n🛒 Rubuta /buyer address ko /seller account\n📜 Rubuta /menu don ganin dukkan fasaloli\n\n@HausaEscrowBot – Domin ciniki cikin aminci!", #[span_3](end_span)
        [span_4](start_span)"start_escrow_button": "🚀 Fara Escrow", #[span_4](end_span)
        [span_5](start_span)"how_it_works_button": "📘 Yadda Escrow ke aiki", #[span_5](end_span)
        [span_6](start_span)"terms_of_use_button": "📜 Ka'idojin Amfani", #[span_6](end_span)
        [span_7](start_span)"security_guide_button": "💬 Jagorar Tsaro", #[span_7](end_span)
        [span_8](start_span)"contact_admin_button": "📞 Tuntuɓi Admin", #[span_8](end_span)
        [span_9](start_span)"create_group_button": "👥 Fara Ciniki (Create Group)", #[span_9](end_span)

        [span_10](start_span)"how_it_works_text": "📘 *YADDA ESCROW KE AIKI:*\n1. Mai sayarwa ya bayar da bayani\n2. Mai siya ya amince ya biya\n3. Admin ya tabbatar da biya\n4. Mai sayarwa ya tura kaya\n5. Buyer ya tabbatar\n6. Admin ya saki kuɗi\n7. Ciniki ya ƙare cikin nasara", #[span_10](end_span)
        [span_11](start_span)"terms_of_use_text": "📜 *Ka'idojin Amfani:*\n🔰 [Fara Ciniki](https://t.me/c/2481223102/27)\n👤 [Buyer Guide](https://t.me/c/2481223102/28)\n💼 [Seller Guide](https://t.me/c/2481223102/29)", #[span_11](end_span)
        [span_12](start_span)"security_guide_text": "🛡️ *Jagorar Tsaro da Taimako:*\n🔰 [Fara Ciniki](https://t.me/c/2481223102/27)\n👤 [Buyer Guide](https://t.me/c/2481223102/28)\n💼 [Seller Guide](https://t.me/c/2481223102/29)\n⚠️ [Admin Verification](https://t.me/HausaEscrow/31)\n⚠️ [Escrow Address](https://t.me/HausaEscrow/32)", #[span_12](end_span)
        [span_13](start_span)"start_deal_prompt": "Danna 👥 *Fara Ciniki* domin ƙirƙirar rukuni. Buyer da Seller su shiga, bot zai jagoranta.", #[span_13](end_span)
        [span_14](start_span)"create_group_instructions": "🔐 Don fara ciniki, ku ƙirƙiri rukuni mai suna *{title}*, sannan ku saka bot din: @HausaEscrowBot.\nBuyer da Seller su shiga, bot zai jagoranta.", #[span_14](end_span)

        [span_15](start_span)"no_deal_or_stage_mismatch": "❗ Babu bayanin ciniki a nan ko kuma an riga an yi wannan matakin.", #[span_15](end_span)
        [span_16](start_span)"buyer_paid_confirm": "💸 @{buyer_username} ya tabbatar da tura kuɗi. Admin zai tabbatar da biya.", #[span_16](end_span)
        [span_17](start_span)"admin_payment_notification": "🛂 Buyer @{buyer_username} ya ce ya tura kuɗi a group: `{chat_id}`.\n\nBayanan Buyer: `{buyer_address}`\nBayanan Seller: `{seller_account}`\nDa fatan za ka duba escrow account.", #[span_17](end_span)
        [span_18](start_span)"funds_received_button": "✅ Kuɗi Sun Shigo", #[span_18](end_span)
        [span_19](start_span)"not_received_cancel_button": "❌ Bai Shigo Ba (Soke Ciniki)", #[span_19](end_span)

        [span_20](start_span)"buyer_not_paid_cancel": "❌ @{buyer_username} ya ce bai tura kuɗi ba. An soke cinikin.", #[span_20](end_span)
        [span_21](start_span)"admin_only_command": "❌ Wannan umarni na admin ne kawai.", #[span_21](end_span)
        [span_22](start_span)"admin_payment_confirmed": "✅ Ka tabbatar da biya. An sanar da @{seller_username} ya tura kayan/kuɗi.", #[span_22](end_span)
        [span_23](start_span)"admin_notified_seller_delivery": "✅ Admin ya tabbatar da kuɗi sun shigo. @{seller_username}, da fatan za ka aika kayan/kuɗi zuwa ga @{buyer_username}.\nAddress na Buyer: `{buyer_address}`", #[span_23](end_span)
        [span_24](start_span)"seller_delivered_button": "✅ Na Tura Kaya/Kudi", #[span_24](end_span)
        [span_25](start_span)"seller_not_delivered_dispute_button": "❌ Ban Tura Ba (Rikici)", #[span_25](end_span)

        [span_26](start_span)"admin_cancelled_deal_group": "❗ Admin @{admin_username} ya soke cinikin tsakanin @{buyer_username} da @{seller_username}.", #[span_26](end_span)
        [span_27](start_span)"admin_cancelled_deal_message": "❗ Ka soke cinikin a group: `{chat_id}`.", #[span_27](end_span)
        [span_28](start_span)"no_such_deal": "❗ Babu wannan cinikin.", #[span_28](end_span)

        [span_29](start_span)"seller_delivered_awaiting_buyer": "📦 @{seller_username} ya ce ya tura kayan/kuɗi. Ana jiran amsar @{buyer_username}.", #[span_29](end_span)
        [span_30](start_span)"buyer_confirm_receipt_prompt": "📦 @{buyer_username}, @{seller_username} ya ce ya tura kayan/kuɗi. Ka tabbatar ka karɓa?", #[span_30](end_span)
        [span_31](start_span)"buyer_received_button": "✅ Na Karɓa", #[span_31](end_span)
        [span_32](start_span)"buyer_not_received_dispute_button": "❌ Ban Karɓa Ba (Rikici)", #[span_32](end_span)

        [span_33](start_span)"dispute_initiated_group": "⚠️ An fara rikici a group `{chat_id}` tsakanin @{buyer_username} da @{seller_username}. Admin zai shigo.", #[span_33](end_span)
        [span_34](start_span)"dispute_initiated_admin_seller": "⚠️ Rikici a cikin group: `{chat_id}`. Seller @{seller_username} ya ce bai tura kayan/kuɗi ba. Tuntuɓi @HausaEscrowSupport don sasanci.", #[span_34](end_span)
        [span_35](start_span)"dispute_initiated_admin_buyer": "⚠️ Rikici a cikin group: `{chat_id}`. Buyer @{buyer_username} ya ce bai karɓi kayan/kuɗi ba. Tuntuɓi @HausaEscrowSupport don sasanci.", #[span_35](end_span)
        [span_36](start_span)"deal_complete_awaiting_admin_release": "🎉 An kammala ciniki tsakanin @{buyer_username} da @{seller_username}! Admin zai saki kuɗi.", #[span_36](end_span)
        [span_37](start_span)"admin_release_notification": "✅ Buyer @{buyer_username} ya tabbatar ya karɓa a group: `{chat_id}`. Da fatan za ka saki kuɗi ga @{seller_username}.", #[span_37](end_span)
        [span_38](start_span)"release_funds_button": "✅ Tura Kuɗi ga Seller", #[span_38](end_span)
        [span_39](start_span)"stop_trade_button": "❌ Tsayar da Ciniki", #[span_39](end_span)

        [span_40](start_span)"admin_released_funds": "✅ Ka saki kuɗi ga @{seller_username} a group: `{chat_id}`.", #[span_40](end_span)
        [span_41](start_span)"seller_final_confirm_prompt": "🎉 @{seller_username}, an turawa kuɗinka. Ka tabbatar sun shigo?", #[span_41](end_span)
        [span_42](start_span)"seller_final_received_button": "✅ Na Karɓa", #[span_42](end_span)
        [span_43](start_span)"seller_final_not_received_button": "❌ Ban Karɓa Ba", #[span_43](end_span)

        [span_44](start_span)"deal_successfully_completed": "🎉 An kammala ciniki cikin nasara! @{seller_username} ya tabbatar da karɓar kuɗi.", #[span_44](end_span)
        [span_45](start_span)"deal_complete_announcement": "✅ DEAL COMPLETE!\n\n📍BUYER: @{buyer_username}\n📍SELLER: @{seller_username}\n🏦 Buyer Address: `{buyer_address}`\n🏦 Seller Account: `{seller_account}`", #[span_45](end_span)

        [span_46](start_span)"seller_final_not_received_dispute_group": "⚠️ An fara rikici a group `{chat_id}`. @{seller_username} ya ce bai karɓi kuɗi ba bayan admin ya saki.", #[span_46](end_span)
        [span_47](start_span)"seller_final_not_received_dispute_admin": "⚠️ Rikici a cikin group: `{chat_id}`. Seller @{seller_username} ya ce bai karɓi kuɗi ba. Tuntuɓi @HausaEscrowSupport don sasanci.", #[span_47](end_span)

        [span_48](start_span)"buyer_address_prompt": "Da fatan ka saka address ɗinka (misali, TRC20 address, ko Bank Account). Misali: `/buyer TRC20_address` ko `/buyer Bank_Account_Number`", #[span_48](end_span)
        [span_49](start_span)"buyer_address_received": "✅ Mun karɓi address ɗin Buyer. Seller, da fatan za ka saka account naka ta amfani da `/seller account_details`", #[span_49](end_span)

        [span_50](start_span)"seller_account_prompt": "Da fatan ka saka account number da sunanka. Misali: `/seller Opay 9131085651 Bashir Rabiu`", #[span_50](end_span)
        [span_51](start_span)"buyer_not_set_address_or_deal_started": "Buyer bai saka address ba tukuna ko kuma an riga an fara ciniki. Buyer, sai ka fara da `/buyer`", #[span_51](end_span)
        [span_52](start_span)"seller_details_received_notify_buyer": "✅ An karɓi bayanan seller. @{buyer_username}, da fatan za ka tura kuɗi zuwa ga **asusun escrow**: \n\n💰 *USDT (TRC20):* `{escrow_trc20_address}`\n🏦 *Naira Bank Account:* `{escrow_naira_bank}`\n\nBayan ka tura kuɗin, sai ka danna maɓallin `✅ Na Tura Kuɗi`.", #[span_52](end_span)
        [span_53](start_span)"i_sent_funds_button": "✅ Na Tura Kuɗi", #[span_53](end_span)
        [span_54](start_span)"i_did_not_send_button": "❌ Ban Tura Ba", #[span_54](end_span)

        [span_55](start_span)"current_status": "📊 Status ɗinka a Hausa Escrow: {status}", #[span_55](end_span)
        [span_56](start_span)"no_deal_record": "Babu rikodin ciniki a halin yanzu.", #[span_56](end_span)
        [span_57](start_span)"you_are_buyer": "Kai ne *buyer* a ciniki a group: `{chat_id}`. Mataki: *{stage}*.", #[span_57](end_span)
        [span_58](start_span)"you_are_seller": "Kai ne *seller* a ciniki a group: `{chat_id}`. Mataki: *{stage}*.", #[span_58](end_span)

        [span_59](start_span)"deal_cancelled_message": "❗ Ciniki tsakanin @{buyer_username} da @{seller_username} an tsayar dashi.", #[span_59](end_span)
        [span_60](start_span)"no_deal_to_cancel": "❗ Babu bayanin ciniki a nan da za a soke.", #[span_60](end_span)

        "choose_language": "Please choose your language / Da fatan zaɓi yarenka:",
        "language_set_ha": "An saita yarenka zuwa Hausa.",
        "language_set_en": "Your language has been set to English."
    },
    "EN": {
        [span_61](start_span)"welcome": "⚜️ Hausa Escrow Bot ⚜️ v.1\n\nWelcome to Hausa Escrow Bot! This bot provides secure (escrow) services for your trades on Telegram. 🔒\n\n💰 *ESCROW FEES:*\n- 5% if the amount exceeds $100\n- $5 if it's less than $100\n\n🌟 *UPDATES - PROOF:*\n✅ COMPLETED TRADES: 0\n⚖️ DISPUTES RESOLVED: 0\n\n🛒 Type /buyer address or /seller account\n📜 Type /menu to see all features\n\n@HausaEscrowBot – For secure trading!", #[span_61](end_span)
        [span_62](start_span)"start_escrow_button": "🚀 Start Escrow", #[span_62](end_span)
        [span_63](start_span)"how_it_works_button": "📘 How Escrow Works", #[span_63](end_span)
        [span_64](start_span)"terms_of_use_button": "📜 Terms of Use", #[span_64](end_span)
        [span_65](start_span)"security_guide_button": "💬 Security Guide", #[span_65](end_span)
        [span_66](start_span)"contact_admin_button": "📞 Contact Admin", #[span_66](end_span)
        [span_67](start_span)"create_group_button": "👥 Create Trade (Create Group)", #[span_67](end_span)

        [span_68](start_span)"how_it_works_text": "📘 *HOW ESCROW WORKS:*\n1. Seller provides details\n2. Buyer agrees to pay\n3. Admin confirms payment\n4. Seller sends goods\n5. Buyer confirms receipt\n6. Admin releases funds\n7. Trade successfully completed", #[span_68](end_span)
        [span_69](start_span)"terms_of_use_text": "📜 *Terms of Use:*\n🔰 [Start Trade](https://t.me/c/2481223102/27)\n👤 [Buyer Guide](https://t.me/c/2481223102/28)\n💼 [Seller Guide](https://t.me/c/2481223102/29)", #[span_69](end_span)
        [span_70](start_span)"security_guide_text": "🛡️ *Security and Support Guide:*\n🔰 [Start Trade](https://t.me/c/2481223102/27)\n👤 [Buyer Guide](https://t.me/c/2481223102/28)\n💼 [Seller Guide](https://t.me/c/2481223102/29)\n⚠️ [Admin Verification](https://t.me/HausaEscrow/31)\n⚠️ [Escrow Address](https://t.me/HausaEscrow/32)", #[span_70](end_span)
        [span_71](start_span)"start_deal_prompt": "Click 👥 *Create Trade* to create a group. Buyer and Seller should join, the bot will guide.", #[span_71](end_span)
        [span_72](start_span)"create_group_instructions": "🔐 To start a trade, create a group named *{title}*, then add the bot: @HausaEscrowBot.\nBuyer and Seller should join, the bot will guide.", #[span_72](end_span)

        [span_73](start_span)"no_deal_or_stage_mismatch": "❗ No deal information here or this stage has already passed.", #[span_73](end_span)
        [span_74](start_span)"buyer_paid_confirm": "💸 @{buyer_username} has confirmed sending funds. Admin will confirm payment.", #[span_74](end_span)
        [span_75](start_span)"admin_payment_notification": "🛂 Buyer @{buyer_username} said they sent funds in group: `{chat_id}`.\n\nBuyer Info: `{buyer_address}`\nSeller Info: `{seller_account}`\nPlease check the escrow account.", #[span_75](end_span)
        [span_76](start_span)"funds_received_button": "✅ Funds Received", #[span_76](end_span)
        [span_77](start_span)"not_received_cancel_button": "❌ Not Received (Cancel Deal)", #[span_77](end_span)

        [span_78](start_span)"buyer_not_paid_cancel": "❌ @{buyer_username} said they did not send funds. The trade has been cancelled.", #[span_78](end_span)
        [span_79](start_span)"admin_only_command": "❌ This command is for admin only.", #[span_79](end_span)
        [span_80](start_span)"admin_payment_confirmed": "✅ You have confirmed payment. @{seller_username} has been notified to send the goods/funds.", #[span_80](end_span)
        [span_81](start_span)"admin_notified_seller_delivery": "✅ Admin has confirmed funds received. @{seller_username}, please send the goods/funds to @{buyer_username}.\nBuyer's Address: `{buyer_address}`", #[span_81](end_span)
        [span_82](start_span)"seller_delivered_button": "✅ I Sent Goods/Funds", #[span_82](end_span)
        [span_83](start_span)"seller_not_delivered_dispute_button": "❌ I Did Not Send (Dispute)", #[span_83](end_span)

        [span_84](start_span)"admin_cancelled_deal_group": "❗ Admin @{admin_username} has cancelled the trade between @{buyer_username} and @{seller_username}.", #[span_84](end_span)
        [span_85](start_span)"admin_cancelled_deal_message": "❗ You have cancelled the trade in group: `{chat_id}`.", #[span_85](end_span)
        [span_86](start_span)"no_such_deal": "❗ This trade does not exist.", #[span_86](end_span)

        [span_87](start_span)"seller_delivered_awaiting_buyer": "📦 @{seller_username} said they sent the goods/funds. Awaiting @{buyer_username}'s response.", #[span_87](end_span)
        [span_88](start_span)"buyer_confirm_receipt_prompt": "📦 @{buyer_username}, @{seller_username} said they sent the goods/funds. Did you receive them?", #[span_88](end_span)
        [span_89](start_span)"buyer_received_button": "✅ I Received", #[span_89](end_span)
        [span_90](start_span)"buyer_not_received_dispute_button": "❌ I Did Not Receive (Dispute)", #[span_90](end_span)

        [span_91](start_span)"dispute_initiated_group": "⚠️ A dispute has been initiated in group `{chat_id}` between @{buyer_username} and @{seller_username}. Admin will intervene.", #[span_91](end_span)
        [span_92](start_span)"dispute_initiated_admin_seller": "⚠️ Dispute in group: `{chat_id}`. Seller @{seller_username} said they did not send the goods/funds. Contact @HausaEscrowSupport for mediation.", #[span_92](end_span)
        [span_93](start_span)"dispute_initiated_admin_buyer": "⚠️ Dispute in group: `{chat_id}`. Buyer @{buyer_username} said they did not receive the goods/funds. Contact @HausaEscrowSupport for mediation.", #[span_93](end_span)
        [span_94](start_span)"deal_complete_awaiting_admin_release": "🎉 Trade completed between @{buyer_username} and @{seller_username}! Admin will release funds.", #[span_94](end_span)
        [span_95](start_span)"admin_release_notification": "✅ Buyer @{buyer_username} has confirmed receipt in group: `{chat_id}`. Please release funds to @{seller_username}.", #[span_95](end_span)
        [span_96](st
