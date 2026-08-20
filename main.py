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

# Logging configuring gochuu
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Logiihttpx akka hin baay'anne hir'isuu
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Akkam {user.mention_html()}!\n\nBotii Ararsa Technology Solutions tiin Baga Nagaan Dhufte. Tajaajila filachuuf /help fayyadami."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Tajaajiloota keenya dhihaatan dhihootti asirratti ni argatta!")

async def start_bot() -> None:
    if not TOKEN:
        logger.error("DOGOGGORA: BOT_TOKEN Environment Variable keessatti hin argamne!")
        sys.exit(1)

    logger.info("Ararsa Technology Solutions Bot eegalaa jira...")
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Python 3.14 irratti karaa sirrii polling eegalsiisuu
    async with application:
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        # asyncio.run() fayyadamuun event loop haaraa uuma
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Botiin dhaabbateera.")
    except Exception as e:
        logger.critical(f"Dhibee hin eegalamne: {e}")
