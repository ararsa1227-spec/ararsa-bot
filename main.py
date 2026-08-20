import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token Environment Variable irraa dubbisuu (ykn kallattiidhaan bakka buusuu)
TOKEN = os.environ.get("BOT_TOKEN", "8677969421:AAFyY_cNRkx-3X3N5TxI7nilY342rh9DtHc")

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
    logger.info("Ararsa Technology Solutions Bot Starting...")
    
    # Application uumuu
    application = Application.builder().token(TOKEN).build()

    # Handlers galmeessuu
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Polling eegaluu
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Python 3.12+ fi Render irratti RuntimeError akka hin uumamneef
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    main()
