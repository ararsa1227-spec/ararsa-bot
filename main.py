import logging
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "8677969421:AAEPVkcW9BY-5xjRQdZeAK8ESRbgIF07XYQ")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "123456789"))

# Dummy Web Server Render Port Binding
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Text Dictionary Afaan Sadaniif
TEXTS = {
    'lang_om': {
        'selected': "Afaan Oromoo milkaa'inaansheewwan filatameera! ✅\n\n**Manni Maroo Tajaajilaa (Main Menu):**",
        'btn_services': "🛠️ Tajaajiloota",
        'btn_products': "🛒 Oomishaalee",
        'btn_request': "📋 Tajaajila Gaafachuu",
        'btn_payment': "💳 Kafaltii (Payment)",
        'btn_contact': "📞 Nu Quunnamaa",
        'btn_location': "📍 Bakka Argamaa",
        'btn_about': "ℹ️ Waa'ee Keenya",
        'btn_lang': "🌐 Afaan Jijjiiri",
        'msg_received': "Ergaan keessan sirriitti dhiyaateera. Galatoomaa!",
    },
    'lang_am': {
        'selected': "አማርኛ በጥሩ ሁኔታ ተመርጧል! ✅\n\n**ዋና ማውጫ (Main Menu):**",
        'btn_services': "🛠️ አገልግሎቶች",
        'btn_products': "🛒 ምርቶች",
        'btn_request': "📋 አገልግሎት ለመጠየቅ",
        'btn_payment': "💳 ክፍያ (Payment)",
        'btn_contact': "📞 እኛን ለማነጋገር",
        'btn_location': "📍 አድራሻችን",
        'btn_about': "ℹ️ ስለ እኛ",
        'btn_lang': "🌐 ቋንቋ ለመለወጥ",
        'msg_received': "መልእክትዎ በትክክል ደርሷል። አመሰግናለሁ!",
    },
    'lang_en': {
        'selected': "English has been successfully selected! ✅\n\n**Main Menu:**",
        'btn_services': "🛠️ Services",
        'btn_products': "🛒 Products",
        'btn_request': "📋 Request Service",
        'btn_payment': "💳 Payment",
        'btn_contact': "📞 Contact Us",
        'btn_location': "📍 Location",
        'btn_about': "ℹ️ About Us",
        'btn_lang': "🌐 Change Language",
        'msg_received': "Your message has been received successfully. Thank you!",
    }
}

def get_main_menu_keyboard(lang_code):
    t = TEXTS.get(lang_code, TEXTS['lang_om'])
    keyboard = [
        [
            InlineKeyboardButton(t['btn_services'], callback_data='menu_services'),
            InlineKeyboardButton(t['btn_products'], callback_data='menu_products')
        ],
        [InlineKeyboardButton(t['btn_request'], callback_data='menu_request')],
        [InlineKeyboardButton(t['btn_payment'], callback_data='menu_payment')],
        [
            InlineKeyboardButton(t['btn_contact'], callback_data='menu_contact'),
            InlineKeyboardButton(t['btn_location'], callback_data='menu_location')
        ],
        [
            InlineKeyboardButton(t['btn_about'], callback_data='menu_about'),
            InlineKeyboardButton(t['btn_lang'], callback_data='menu_changelang')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🏳️ Afaan Oromoo", callback_data='lang_om')],
        [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data='lang_am')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🤖 Ararsa Technology Solutionstti Baga Nagaan Dhuftan!\n\n"
        "Maaloo afaan filadhaa / Please select a language / እባክዎን ቋንቋ ይምረጡ:"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    lang = query.data
    context.user_data['lang'] = lang
    
    t = TEXTS.get(lang, TEXTS['lang_om'])
    reply_markup = get_main_menu_keyboard(lang)
    
    await query.edit_message_text(text=t['selected'], reply_markup=reply_markup, parse_mode='Markdown')

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu_changelang':
        await start(update, context)

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_lang = context.user_data.get('lang', 'lang_om')
    t = TEXTS.get(user_lang, TEXTS['lang_om'])
    
    try:
        await update.message.forward(chat_id=ADMIN_CHAT_ID)
        await update.message.reply_text(t['msg_received'])
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")

def main() -> None:
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(menu_callback_handler, pattern='^menu_'))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_admin))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    main()
