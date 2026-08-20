import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Conversation States
LANGUAGE, MAIN_MENU, REQ_NAME, REQ_PHONE, REQ_SERVICE, REQ_LOCATION, REQ_DESC, REQ_PHOTO = range(8)

# Texts Multi-Language
TEXTS = {
    "OM": {
        "welcome": "🚀 Simatee dhuftan Ararsa Technology Solutions!\nMootummaa fi Dhaabbilee dhuunfaaf tajaajila teeknoolojii saafisaa fi qulqullina qabu ni kennina.",
        "lang_select": "Moochaa Afaan keessanii filadhaa:",
        "main_menu": "🏠 **Menu Guddaa**\nFiltannoowwan asii gadii irraa dooraddaa:",
        "btn_services": "💻 Tajaajiloota",
        "btn_products": "🛒 Meeshaalee",
        "btn_request": "📋 Tajaajila Gaafachuuf",
        "btn_quote": "💰 Gatii Gaafachuuf",
        "btn_contact": "📞 Nu Quunnamaa",
        "btn_location": "📍 Bakka Nu Argamtan",
        "btn_lang": "🌍 Afaan Jijjiiruuf",
        "services_list": "💻 **Tajaajiloota Nu Kenninu:**\n\n1. 🖨 Computer & Printer Maintenance\n2. 🌐 Network & Wi-Fi Setup\n3. 📹 CCTV Camera Installation\n4. 🔐 VPN & Security Solutions\n5. 💻 Software & System Setup",
        "products_list": "🛒 **Meeshaalee Gurguraa:**\n\n• Kompitiitara (Laptops & Desktops)\n• Piriinteroota & Toners\n• Network Routers & Switches\n• CCTV Cameras & DVRs\n\nDetail qabuuf nu quunnamaa!",
        "contact_info": "📞 **Ararsa Technology Solutions**\n\n📱 Bilbila: 0912688641\n📧 Email: ararsa1221@gmail.com\n📍 Teessoo: Dodola, Ethiopia",
        "location_info": "📍 **Teessoo Keenya:**\nArarsa Technology Solutions\nDodola, Oromia, Ethiopia.",
        "req_start": "📋 **Tajaajila Gaafachuuf Formii kana guutaa.**\n\nMaqaa keessan guutuu galchaa:",
        "req_phone": "Bilbila keessan galchaa (fkn: 0912345678):",
        "req_service": "Tajaajila maaltu isin barbaachisa?",
        "req_location": "Teessoo keessan (Bakka jirtan) galchaa:",
        "req_desc": "Rakkoo ykn waan isin barbaachisu bal'inaan ibsaa:",
        "req_photo": "Fakkii (Photo) rakkoo sanaa yoo qabaattan ergaa (Yoo hin qabne 'Skip' tuqaa):",
        "req_complete": "✅ Gaaffiin keessan sirriitti ergameera! Haala saafisaan isin quunnamna.",
        "skip": "Skip ➡️"
    },
    "AM": {
        "welcome": "🚀 ወደ Ararsa Technology Solutions እንኳን ደህና መጡ!\nፈጣን እና አስተማማኝ የቴክኖሎጂ አገልግሎቶች እንሰጣለን።",
        "lang_select": "እባክዎን ቋንቋ ይምረጡ:",
        "main_menu": "🏠 **ዋና ማውጫ**\nከታች ከተዘረዘሩት ይምረጡ:",
        "btn_services": "💻 አገልግሎቶች",
        "btn_products": "🛒 ምርቶች",
        "btn_request": "📋 አገልግሎት ለመጠየቅ",
        "btn_quote": "💰 ዋጋ ለመጠየቅ",
        "btn_contact": "📞 ያግኙን",
        "btn_location": "📍 አድራሻችን",
        "btn_lang": "🌍 ቋንቋ ለመቀየር",
        "services_list": "💻 **የምንሰጣቸው አገልግሎቶች:**\n\n1. 🖨 Computer & Printer Maintenance\n2. 🌐 Network & Wi-Fi Setup\n3. 📹 CCTV Camera Installation\n4. 🔐 VPN & Security Solutions\n5. 💻 Software & System Setup",
        "products_list": "🛒 **የሚሸጡ ዕቃዎች:**\n\n• ኮምፒውተሮች (Laptops & Desktops)\n• ፕሪንተሮች እና ቶነሮች\n• የኔትወርክ እቃዎች\n• CCTV ካሜራዎች\n\nለበለጠ መረጃ ያግኙን!",
        "contact_info": "📞 **Ararsa Technology Solutions**\n\n📱 ስልክ: 0912688641\n📧 ኢሜይል: ararsa1221@gmail.com\n📍 አድራሻ: ዶዶላ, ኢትዮጵያ",
        "location_info": "📍 **አድራሻችን:**\nArarsa Technology Solutions\nዶዶላ (Dodola), ኢትዮጵያ።",
        "req_start": "📋 **አገልግሎት ለመጠየቅ እባክዎን ፎርሙን ይሙሉ::**\n\nሙሉ ስምዎን ያስገቡ:",
        "req_phone": "የስልክ ቁጥርዎን ያስገቡ (ምሳሌ: 0912345678):",
        "req_service": "ምን ዓይነት አገልግሎት ይፈልጋሉ?",
        "req_location": "አድራሻዎን (ያሉበትን ቦታ) ያስገቡ:",
        "req_desc": "የሚፈልጉትን ወይም ያጋጠመውን ችግር በአጭሩ ያብራሩ:",
        "req_photo": "የችግሩን ፎቶ ካለዎት ይላኩ (ከሌለ 'Skip' የሚለውን ይጫኑ):",
        "req_complete": "✅ ጥያቄዎ በተሳካ ሁኔታ ተልኳል! በቅርብ ጊዜ እናገኝዎታለን።",
        "skip": "Skip ➡️"
    },
    "EN": {
        "welcome": "🚀 Welcome to Ararsa Technology Solutions!\nProviding fast & reliable professional IT solutions.",
        "lang_select": "Please select your language:",
        "main_menu": "🏠 **Main Menu**\nPlease select an option below:",
        "btn_services": "💻 Services",
        "btn_products": "🛒 Products",
        "btn_request": "📋 Request Service",
        "btn_quote": "💰 Get a Quote",
        "btn_contact": "📞 Contact Us",
        "btn_location": "📍 Our Location",
        "btn_lang": "🌍 Change Language",
        "services_list": "💻 **Our Professional Services:**\n\n1. 🖨 Computer & Printer Maintenance\n2. 🌐 Network & Wi-Fi Installation\n3. 📹 CCTV Security Systems\n4. 🔐 VPN & Cyber Security\n5. 💻 Software & System Setup",
        "products_list": "🛒 **Products Available:**\n\n• Laptops & Desktops\n• Printers & Toners\n• Networking Hardware\n• CCTV Cameras & DVRS\n\nContact us for details & pricing!",
        "contact_info": "📞 **Ararsa Technology Solutions**\n\n📱 Phone: 0912688641\n📧 Email: ararsa1221@gmail.com\n📍 Location: Dodola, Ethiopia",
        "location_info": "📍 **Our Location:**\nArarsa Technology Solutions\nDodola, Oromia, Ethiopia.",
        "req_start": "📋 **Service Request Form**\n\nPlease enter your Full Name:",
        "req_phone": "Enter your Phone Number (e.g. 0912345678):",
        "req_service": "Which service do you require?",
        "req_location": "Enter your location / address:",
        "req_desc": "Describe your issue or requirements:",
        "req_photo": "Upload a photo of the issue if available (or tap 'Skip'):",
        "req_complete": "✅ Your request has been sent successfully! We will contact you shortly.",
        "skip": "Skip ➡️"
    }
}

def get_menu_keyboard(lang):
    t = TEXTS[lang]
    keyboard = [
        [t["btn_services"], t["btn_products"]],
        [t["btn_request"], t["btn_quote"]],
        [t["btn_contact"], t["btn_location"]],
        [t["btn_lang"]]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🇪🇹 Afaan Oromo", "🇪🇹 Amharic"], ["🇬🇧 English"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose Language / Afaan Filadhaa / ቋንቋ ይምረጡ:", reply_markup=reply_markup)
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Oromo" in text:
        lang = "OM"
    elif "Amharic" in text:
        lang = "AM"
    else:
        lang = "EN"
    
    context.user_data["lang"] = lang
    t = TEXTS[lang]
    await update.message.reply_text(t["welcome"])
    await update.message.reply_text(t["main_menu"], reply_markup=get_menu_keyboard(lang), parse_mode="Markdown")
    return MAIN_MENU

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lang = context.user_data.get("lang", "OM")
    t = TEXTS[lang]

    if text in [TEXTS["OM"]["btn_services"], TEXTS["AM"]["btn_services"], TEXTS["EN"]["btn_services"]]:
        await update.message.reply_text(t["services_list"], parse_mode="Markdown")
    elif text in [TEXTS["OM"]["btn_products"], TEXTS["AM"]["btn_products"], TEXTS["EN"]["btn_products"]]:
        await update.message.reply_text(t["products_list"], parse_mode="Markdown")
    elif text in [TEXTS["OM"]["btn_contact"], TEXTS["AM"]["btn_contact"], TEXTS["EN"]["btn_contact"]]:
        await update.message.reply_text(t["contact_info"], parse_mode="Markdown")
    elif text in [TEXTS["OM"]["btn_location"], TEXTS["AM"]["btn_location"], TEXTS["EN"]["btn_location"]]:
        await update.message.reply_text(t["location_info"], parse_mode="Markdown")
    elif text in [TEXTS["OM"]["btn_lang"], TEXTS["AM"]["btn_lang"], TEXTS["EN"]["btn_lang"]]:
        return await start(update, context)
    elif text in [TEXTS["OM"]["btn_request"], TEXTS["AM"]["btn_request"], TEXTS["EN"]["btn_request"], TEXTS["OM"]["btn_quote"], TEXTS["AM"]["btn_quote"], TEXTS["EN"]["btn_quote"]]:
        await update.message.reply_text(t["req_start"], reply_markup=ReplyKeyboardRemove())
        return REQ_NAME
    return MAIN_MENU

async def req_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["req_name"] = update.message.text
    lang = context.user_data.get("lang", "OM")
    await update.message.reply_text(TEXTS[lang]["req_phone"])
    return REQ_PHONE

async def req_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["req_phone"] = update.message.text
    lang = context.user_data.get("lang", "OM")
    await update.message.reply_text(TEXTS[lang]["req_service"])
    return REQ_SERVICE

async def req_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["req_service"] = update.message.text
    lang = context.user_data.get("lang", "OM")
    await update.message.reply_text(TEXTS[lang]["req_location"])
    return REQ_LOCATION

async def req_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["req_location"] = update.message.text
    lang = context.user_data.get("lang", "OM")
    await update.message.reply_text(TEXTS[lang]["req_desc"])
    return REQ_DESC

async def req_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["req_desc"] = update.message.text
    lang = context.user_data.get("lang", "OM")
    kb = ReplyKeyboardMarkup([[TEXTS[lang]["skip"]]], resize_keyboard=True)
    await update.message.reply_text(TEXTS[lang]["req_photo"], reply_markup=kb)
    return REQ_PHOTO

async def send_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_id=None):
    lang = context.user_data.get("lang", "OM")
    user = update.message.from_user
    
    summary = (
        f"🚨 **NEW CUSTOMER REQUEST** 🚨\n\n"
        f"👤 **Name:** {context.user_data.get('req_name')}\n"
        f"📱 **Phone:** {context.user_data.get('req_phone')}\n"
        f"🛠 **Service:** {context.user_data.get('req_service')}\n"
        f"📍 **Location:** {context.user_data.get('req_location')}\n"
        f"📝 **Description:** {context.user_data.get('req_desc')}\n"
        f"👤 **Telegram User:** @{user.username if user.username else user.first_name} (ID: {user.id})"
    )
    
    if ADMIN_ID != 0:
        try:
            if photo_id:
                await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=summary, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=summary, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send to admin: {e}")

    await update.message.reply_text(
        TEXTS[lang]["req_complete"],
        reply_markup=get_menu_keyboard(lang)
    )
    return MAIN_MENU

async def req_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id if update.message.photo else None
    return await send_to_admin(update, context, photo_id)

async def req_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await send_to_admin(update, context, None)

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable is missing!")
        return

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            REQ_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, req_name)],
            REQ_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, req_phone)],
            REQ_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, req_service)],
            REQ_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, req_location)],
            REQ_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, req_desc)],
            REQ_PHOTO: [
                MessageHandler(filters.PHOTO, req_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, req_skip_photo)
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)

    if WEBHOOK_URL:
        webhook_path = f"/{TOKEN}"
        full_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"
        port = int(os.environ.get("PORT", 10000))
        
        logger.info(f"Setting webhook to: {full_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TOKEN,
            webhook_url=full_url
        )
    else:
        logger.info("Starting long polling...")
        app.run_polling()

if __name__ == "__main__":
    main()
