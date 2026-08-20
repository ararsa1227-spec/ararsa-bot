import logging
import os
import sys
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Logging configure gochuu
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Logii httpx akka hin baay'annee fi irra deddeebiin hin mul'anne hir'isuu
logging.getLogger("httpx").setLevel(logging.WARNING)

# Environment Variable irraa token fudhachuu
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /start bakka kanaa deebii kenne."""
    user = update.effective_user
    await update.message.reply_html(
        f"Akkam {user.mention_html()}!\n\nBotii Ararsa Technology Solutions tiin Baga Nagaan Dhufte. Tajaajila filachuuf /help fayyadami."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command /help bakka kanaa deebii kenne."""
    await update.message.reply_text("Tajaajiloota keenya dhihaatan dhihootti asirratti ni argatta!")

def main() -> None:
    """Boticha kaasuu fi polling eegalsiisuu."""
    if not TOKEN:
        logger.error("DOGOGGORA: BOT_TOKEN Environment Variable keessatti hin argamne!")
        sys.exit(1)

    logger.info("Ararsa Technology Solutions Bot eegalaa jira...")
    
    # Application uumuu
    application = Application.builder().token(TOKEN).build()

    # CommandHandlers dabaluu
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Polling eegaluu (drop_pending_updates=True walitti bu'iinsa ergaa moofaa ittisa)
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Botiin dhaabbateera.")
    except Exception as e:
        logger.critical(f"Dhibee hin eegalamne: {e}")
