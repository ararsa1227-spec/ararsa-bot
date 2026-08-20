import logging
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token Environment Variable irraa dubbisuu
TOKEN = os.environ.get("BOT_TOKEN", "8677969421:AAFyY_cNRkx-3X3N5TxI7nilY342rh9DtHc")

# Render port akka argatuuf Web Server dummy uumuu
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Dummy HTTP server listening on port {port}")
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /start nagaan dhaama."""
    user = update.effective_user
    await update.message.reply_html(
        f"Akkam {user.mention_html()}!\n\nBotii Ararsa Technology Solutions tiin Baga Garasitti Nagaan Dhufte. Tajaajila barbaaddu filachuuf /help fayyadami."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /help qajeelfama dhiheessa."""
    await update.message.reply_text("Tajaajiloota keenya dhihaatan dhihootti asirratti ni argatta!")

def main() -> None:
    """Bot sana qindoomina eegaluu."""
    # Web server backend irra hojjechiisuu
    threading.Thread(target=run_dummy_server, daemon=True).start()

    logger.info("Ararsa Technology Solutions Bot eegalaa jira...")
    
    # Application uumuu
    application = Application.builder().token(TOKEN).build()

    # Handlers galmeessuu
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Polling eegaluu
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    main()
