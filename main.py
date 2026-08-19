import os
import logging
import sqlite3
import asyncio
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============================================================
# CONFIGURATION
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "8677969421:AAFyY_cNRkx-3X3N5TxI7nilY342rh9DtHc")
ADMIN_ID = int(os.getenv("ADMIN_ID", "391294688"))

BUSINESS_NAME = "Ararsa Technology Solutions"
PHONE = "+251 912 688 641"
EMAIL = "ararsa1221@gmail.com"
CBE_ACCOUNT = "10000027656955"
TELEBIRR_PHONE = "+251 912 688 641"

# ============================================================
# LOGGING & DATABASE
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DB_NAME = "technology_bot.db"

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                phone TEXT,
                language TEXT DEFAULT 'or',
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT,
                phone TEXT,
                service TEXT,
                description TEXT,
                status TEXT DEFAULT 'New',
                created_at TEXT
            )
        """)
        conn.commit()

def save_user(user, phone=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users
            (telegram_id, username, first_name, phone, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                phone=COALESCE(excluded.phone, users.phone)
        """, (
            user.id,
            user.username,
            user.first_name,
            phone,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()

def get_user_lang(telegram_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        return row["language"] if row else "or"

def set_user_lang(telegram_id, lang):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id))
        conn.commit()

def save_service_request(telegram_id, name, phone, service, description):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO service_requests
            (telegram_id, name, phone, service, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            telegram_id, name, phone, service, description,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        rid = cursor.lastrowid
        conn.commit()
        return rid

def update_request_status_db(request_id, new_status):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE service_requests SET status = ? WHERE id = ?", (new_status, request_id))
        conn.commit()

# ============================================================
# TRANSLATIONS & MENUS
# ============================================================

TEXTS = {
    "or": {
        "welcome": f"🤖 {BUSINESS_NAME}tti Baga Nagaan Dhuftan!\n\nMaaloo afaan filadhaa:",
        "menu_title": "Manni Maroo Tajaajilaa (Main Menu):",
        "services": "🛠️ Tajaajiloota",
        "products": "🛒 Oomishaalee",
        "req_service": "📋 Tajaajila Gaafachuu",
        "payment": "💳 Kafaltii (Payment)",
        "contact": "📞 Nu Quunnamaa",
        "location": "📍 Bakka Argamaa",
        "about": "ℹ️ Nu Waa'ee",
        "lang_change": "🌐 Afaan Jijjiiri",
        "back": "⬅️ Gara Duraatti",
        "services_desc": "🛠️ TAJAAJILOOTA KEENYA:\n\n1️⃣ Suphaa Kompiitaraa\n2️⃣ Suphaa Pireenterii\n3️⃣ Networking & Cisco\n4️⃣ Tajaajila Software\n5️⃣ Tajaajila VPN\n6️⃣ Deeggarsa Teknoolojii",
        "products_desc": "🛒 OOMISHAALEE:\n\nKompiitara, Monitori, Pireenterii, Ruutarii, Switch fi kkf. Gatii beekuuf nu quunnamaa.",
        "payment_desc": f"💳 IDDOO KAFALTII (PAYMENT):\n\nKafaltii keessan karaa armaan gadiitiin raawwachuu dandeessu:\n\n1️⃣ **Commercial Bank of Ethiopia (CBE):**\nAccount: `{CBE_ACCOUNT}`\nMaqaa: Ararsa Technology Solutions\n\n2️⃣ **Telebirr:**\nLakkoofsa: `{TELEBIRR_PHONE}`\n\nErga kaffaltii raawwattanii booda risiipii (receipt) bot kanaaf ergaa!",
        "contact_desc": f"📞 NU QUUNNAMAA:\n\n🏢 {BUSINESS_NAME}\n📱 Bilbila: {PHONE}\n📧 Email: {EMAIL}",
        "location_desc": f"📍 BAKKA ARGAMA:\n\nBiyya Ethiopia keessatti ni argamna. Lakkoofsa {PHONE} irratti nu bilbilaa.",
        "about_desc": f"ℹ️ WAA'EE KEENYA:\n\n{BUSINESS_NAME} qaamolee dhuunfaaf fi dhaabbataaf furmaata teknoolojii ammayyaa kennicha.",
        "select_lang": "Malli afaanii kam filattu?",
        "lang_set": "Afaan Oromoo milkaa'inaan filatameera! ✅"
    },
    "am": {
        "welcome": f"🤖 {BUSINESS_NAME} - እንኳን ደህና መጡ!\n\nእባክዎ ቋንቋ ይምረጡ:",
        "menu_title": "ዋና ማውጫ (Main Menu):",
        "services": "🛠️ አገልግሎቶች",
        "products": "🛒 እቃዎች/ምርቶች",
        "req_service": "📋 አገልግሎት ይጠይቁ",
        "payment": "💳 የክፍያ መረጃ (Payment)",
        "contact": "📞 ያግኙን",
        "location": "📍 አድራሻችን",
        "about": "ℹ️ ስለ እኛ",
        "lang_change": "🌐 ቋንቋ ቀይር",
        "back": "⬅️ ወደ ዋናው ምናሌ",
        "services_desc": "🛠️ አገልግሎቶቻችን:\n\n1️⃣ የኮምፒዩተር ጥገና\n2️⃣ የፕሪንተር ጥገና\n3️⃣ ኔትወርክ እና ሲስኮ\n4️⃣ ሶፍትዌር አገልግሎት\n5️⃣ ቪፒኤን (VPN) አገልግሎት\n6️⃣ የቴክኒክ ድጋፍ",
        "products_desc": "🛒 ቴክኖሎጂ እቃዎች:\n\nኮምፒዩተሮች፣ ሞኒተሮች፣ ፕሪንተሮች፣ ራውተሮች እና ሌሎችም። ለዋጋ ያግኙን።",
        "payment_desc": f"💳 የክፍያ አካውንቶች:\n\nክፍያዎን በሚከተሉት አካውንቶች መፈጸም ይችላሉ:\n\n1️⃣ **የኢትዮጵያ ንግድ ባንክ (CBE):**\nአካውንት: `{CBE_ACCOUNT}`\nስም: Ararsa Technology Solutions\n\n2️⃣ **ቴሌብር (Telebirr):**\nስልክ: `{TELEBIRR_PHONE}`\n\nክፍያ ከፈጸሙ በኋላ ደረሰኙን (receipt) በዚህ bot ይላኩ!",
        "contact_desc": f"📞 እኛን ለማግኘት:\n\n🏢 {BUSINESS_NAME}\n📱 ስልክ: {PHONE}\n📧 ኢሜይል: {EMAIL}",
        "location_desc": f"📍 አድራሻ:\n\nበኢትዮጵያ ውስጥ እንገኛለን። በ {PHONE} ይደውሉልን።",
        "about_desc": f"ℹ️ ስለ እኛ:\n\n{BUSINESS_NAME} ለግለሰቦች እና ድርጅቶች የቴክኖሎጂ መፍትሄዎችን ይሰጣል።",
        "select_lang": "እባክዎ ቋንቋ ይምረጡ:",
        "lang_set": "አማርኛ በተሳካ ሁኔታ ተመርጧል! ✅"
    },
    "en": {
        "welcome": f"🤖 Welcome to {BUSINESS_NAME}!\n\nPlease select your language:",
        "menu_title": "Main Menu:",
        "services": "🛠️ Services",
        "products": "🛒 Products",
        "req_service": "📋 Request Service",
        "payment": "💳 Payment Info",
        "contact": "📞 Contact Us",
        "location": "📍 Location",
        "about": "ℹ️ About Us",
        "lang_change": "🌐 Change Language",
        "back": "⬅️ Main Menu",
        "services_desc": "🛠️ OUR SERVICES:\n\n1️⃣ Computer Maintenance\n2️⃣ Printer Services\n3️⃣ Networking & Cisco\n4️⃣ Software Services\n5️⃣ VPN Services\n6️⃣ Technical Support",
        "products_desc": "🛒 TECHNOLOGY PRODUCTS:\n\nComputers, Printers, Routers, Switches, and Accessories. Contact us for prices.",
        "payment_desc": f"💳 PAYMENT INFORMATION:\n\nYou can make payments through the following accounts:\n\n1️⃣ **Commercial Bank of Ethiopia (CBE):**\nAccount: `{CBE_ACCOUNT}`\nName: Ararsa Technology Solutions\n\n2️⃣ **Telebirr:**\nPhone: `{TELEBIRR_PHONE}`\n\nPlease send your payment receipt to this bot after payment!",
        "contact_desc": f"📞 CONTACT US:\n\n🏢 {BUSINESS_NAME}\n📱 Phone: {PHONE}\n📧 Email: {EMAIL}",
        "location_desc": f"📍 LOCATION:\n\nAvailable in Ethiopia. Call us at {PHONE}.",
        "about_desc": f"ℹ️ ABOUT US:\n\n{BUSINESS_NAME} provides practical technology solutions for individuals and businesses.",
        "select_lang": "Please select your preferred language:",
        "lang_set": "English language selected successfully! ✅"
    }
}

def get_menu(lang):
    t = TEXTS.get(lang, TEXTS["or"])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["services"], callback_data="services"), InlineKeyboardButton(t["products"], callback_data="products")],
        [InlineKeyboardButton(t["req_service"], callback_data="request_service")],
        [InlineKeyboardButton(t["payment"], callback_data="payment")],
        [InlineKeyboardButton(t["contact"], callback_data="contact"), InlineKeyboardButton(t["location"], callback_data="location")],
        [InlineKeyboardButton(t["about"], callback_data="about"), InlineKeyboardButton(t["lang_change"], callback_data="change_lang")],
    ])

def get_back(lang):
    t = TEXTS.get(lang, TEXTS["or"])
    return InlineKeyboardMarkup([[InlineKeyboardButton(t["back"], callback_data="main_menu")]])

# ============================================================
# STATES & HANDLERS
# ============================================================

PHONE_STATE, DESCRIPTION_STATE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    lang = get_user_lang(user.id)
    
    lang_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏳️ Afaan Oromoo", callback_data="lang_or")],
        [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])
    
    if update.message:
        await update.message.reply_text(TEXTS[lang]["welcome"], reply_markup=lang_keyboard)
    elif update.callback_query:
        await update.callback_query.message.edit_text(TEXTS[lang]["welcome"], reply_markup=lang_keyboard)

async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "lang_or":
        set_user_lang(user_id, "or")
    elif query.data == "lang_am":
        set_user_lang(user_id, "am")
    elif query.data == "lang_en":
        set_user_lang(user_id, "en")
        
    lang = get_user_lang(user_id)
    t = TEXTS[lang]
    await query.edit_message_text(f"{t['lang_set']}\n\n{t['menu_title']}", reply_markup=get_menu(lang))

async def change_lang_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏳️ Afaan Oromoo", callback_data="lang_or")],
        [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])
    await query.edit_message_text("Afaan filadhaa / Language / ቋንቋ ይምረጡ:", reply_markup=lang_keyboard)

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await query.edit_message_text(TEXTS[lang]["services_desc"], reply_markup=get_back(lang), parse_mode="Markdown")

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await query.edit_message_text(TEXTS[lang]["products_desc"], reply_markup=get_back(lang), parse_mode="Markdown")

async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await query.edit_message_text(TEXTS[lang]["payment_desc"], reply_markup=get_back(lang), parse_mode="Markdown")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await query.edit_message_text(TEXTS[lang]["contact_desc"], reply_markup=get_back(lang), parse_mode="Markdown")

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await query.edit_message_text(TEXTS[lang]["location_desc"], reply_markup=get_back(lang), parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    await query.edit_message_text(TEXTS[lang]["about_desc"], reply_markup=get_back(lang), parse_mode="Markdown")

async def request_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    
    services_keyboard = [
        [InlineKeyboardButton("💻 Computer", callback_data="req_computer"), InlineKeyboardButton("🖨️ Printer", callback_data="req_printer")],
        [InlineKeyboardButton("🌐 Network", callback_data="req_network"), InlineKeyboardButton("🔐 VPN", callback_data="req_vpn")],
        [InlineKeyboardButton("🛠️ Other", callback_data="req_other")],
    ]
    await query.edit_message_text("📋 Tajaajila barbaaddu filadhaa / Select service:", reply_markup=InlineKeyboardMarkup(services_keyboard))

async def select_request_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service_map = {
        "req_computer": "Computer Support",
        "req_printer": "Printer Support",
        "req_network": "Network Support",
        "req_vpn": "VPN Service",
        "req_other": "Other Service",
    }
    service = service_map.get(query.data, "Other Service")
    context.user_data["service"] = service
    
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Share Phone Number / Lakkoofsa Bilbilaa", request_contact=True)]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    
    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Selected: **{service}**\n\nLakkoofsa bilbilaa keessan nuuf qoodaa / Share phone number:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return PHONE_STATE

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()
    context.user_data["phone"] = phone
    await update.message.reply_text(
        "📝 Mee rakkoo keessan gabaabaatti barreessaa / Describe your issue:\n\n*(/cancel - Dhiisuuf)*",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return DESCRIPTION_STATE

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text.strip()
    user = update.effective_user
    service = context.user_data.get("service", "Other Service")
    phone = context.user_data.get("phone", "Not provided")
    lang = get_user_lang(user.id)

    request_id = save_service_request(user.id, user.full_name, phone, service, description)

    await update.message.reply_text(
        f"✅ MILKAATEERA / SUCCESS\n\nRequest ID: #{request_id}\nService: {service}\nPhone: {phone}\nDescription: {description}\n\nOgeessonni keenya dafee isin qunnamu.",
        reply_markup=get_menu(lang)
    )

    if ADMIN_ID != 0:
        admin_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 In Progress", callback_data=f"adm_status_{request_id}_In_Progress"), InlineKeyboardButton("✅ Complete", callback_data=f"adm_status_{request_id}_Completed")],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"adm_status_{request_id}_Cancelled")]
        ])
        admin_message = f"🚨 Gaaffii Tajaajilaa Haaraa (#{request_id})\n\n👤 Maamila: {user.full_name}\n☎️ Bilbila: {phone}\n🛠️ Tajaajila: {service}\n📝 Ibsa: {description}"
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=admin_keyboard)
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    lang = get_user_lang(update.effective_user.id)
    await update.message.reply_text("❌ Haqumeera / Cancelled.", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(TEXTS[lang]["menu_title"], reply_markup=get_menu(lang))
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data.startswith("adm_status_"):
        parts = data.split("_")
        req_id = parts[2]
        new_status = "_".join(parts[3:])
        update_request_status_db(req_id, new_status)
        await query.answer(f"Request #{req_id} -> {new_status}!")
        return

    routes = {
        "services": services, "products": products, "payment": payment_info,
        "contact": contact, "location": location, "about": about,
        "change_lang": change_lang_menu
    }
    if data in routes:
        await routes[data](update, context)
    elif data == "main_menu":
        await query.answer()
        lang = get_user_lang(query.from_user.id)
        await query.edit_message_text(TEXTS[lang]["menu_title"], reply_markup=get_menu(lang))

# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    init_database()
    
    application = Application.builder().token(BOT_TOKEN).build()

    service_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(request_service, pattern="^request_service$")],
        states={
            PHONE_STATE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), receive_phone)],
            DESCRIPTION_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel_request)],
        per_user=True,
        per_chat=False,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(service_conversation)
    
    application.add_handler(CallbackQueryHandler(set_language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(select_request_service, pattern="^req_"))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info(f"{BUSINESS_NAME} Bot Starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()