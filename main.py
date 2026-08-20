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

# Logii httpx akka hin baay'anne hir'isuu
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.environ.get("BOT_TOKEN")

# Dummy Server Render Port scan akka darbuuf
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Dummy HTTP server listening on port {port}")
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Akkam {user.mention_html()}!\n\nBotii Ararsa Technology Solutions tiin Baga Nagaan Dhufte. Tajaajila filachuuf /help fayyadami."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tajaajiloota keenya dhihaatan dhihootti asirratti ni argatta!")

def main() -> None:
    if not TOKEN:
        logger.error("BOT_TOKEN Environment Variable keessatti hin argamne!")
        return

    # Background thread irratti dummy server kaasuu
    threading.Thread(target=run_dummy_server, daemon=True).start()

    logger.info("Ararsa Technology Solutions Bot Starting...")
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    main()
