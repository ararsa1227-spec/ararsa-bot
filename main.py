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

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token Environment Variable irraa
TOKEN = os.environ.get("BOT_TOKEN", "8677969421:AAFyY_cNRkx-3X3N5TxI7nilY342rh9DtHc")

# ID Telegram keetii kan ergaan fayyadamaa itti forward ta'u
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "123456789"))  # ID kee galchi

# Dummy Web Server (Render Port binding)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Command /start
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

# Language selection callback
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    lang = query.data
    context.user_data['lang'] = lang
    
    if lang == 'lang_om':
        msg = "Afaan Oromoo filattaniittu! Ergaa, fakkii ykn suuraa kamiyyuu asitti erguu dandeessu. Kallattiidhaan gara keenyatti ni darba."
    elif lang == 'lang_am':
        msg = "አማርኛ መርጠዋል! ማንኛውንም መልእክት፣ ምስል ወይም ቪዲዮ እዚህ መላክ ይችላሉ። በቀጥታ ወደ እኛ ይደርሳል።"
    else:
        msg = "You selected English! You can send any message, image, or file here. It will be forwarded directly to us."
        
    await query.edit_message_text(text=msg)

# Forward user messages to Admin
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_lang = context.user_data.get('lang', 'lang_om')
    
    # Message gara Admin (sitti) forward gochuu
    try:
        await update.message.forward(chat_id=ADMIN_CHAT_ID)
        
        # Deebii fayyadamaaf deebisuu
        if user_lang == 'lang_om':
            response = "Ergaan keessan sirriitti dhiyaateera. Galatoomaa!"
        elif user_lang == 'lang_am':
            response = "መልእክትዎ በትክክል ደርሷል። አመሰግናለሁ!"
        else:
            response = "Your message has been received successfully. Thank you!"
            
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")

def main() -> None:
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_admin))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    main()
