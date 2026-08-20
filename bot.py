import os
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("technology_solution_bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/")
WEBHOOK_PATH = "/telegram/webhook"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

app = FastAPI(title="Technology Solution Telegram Bot")

SERVICES = {
    "computer": ("💻 Computer Maintenance",
                 "Windows installation, software setup, troubleshooting, cleaning, upgrades and performance optimization."),
    "printer": ("🖨 Printer Service",
                "Printer installation, driver configuration, network printing, troubleshooting and maintenance."),
    "network": ("🌐 Network Solutions",
                "LAN/Wi-Fi installation, router and switch configuration, IP/DHCP/NAT setup and network troubleshooting."),
    "cctv": ("📹 CCTV & Security",
             "CCTV planning, installation, configuration and network access."),
    "server": ("🖥 Server & IT Support",
               "Basic server setup, backup, user support and IT infrastructure assistance."),
    "vpn": ("🔐 VPN Solutions",
            "Business and secure remote-access VPN configuration and troubleshooting."),
}

def main_menu():
    b = InlineKeyboardBuilder()
    b.button(text="💻 Services", callback_data="services")
    b.button(text="📋 Request Service", callback_data="request")
    b.button(text="💰 Get a Quote", callback_data="quote")
    b.button(text="🛒 Products", callback_data="products")
    b.button(text="📞 Contact Us", callback_data="contact")
    b.button(text="🌍 Language", callback_data="language")
    b.adjust(2)
    return b.as_markup()

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="home")]
    ])

def services_menu():
    b = InlineKeyboardBuilder()
    for key, (title, _) in SERVICES.items():
        b.button(text=title, callback_data=f"service:{key}")
    b.button(text="🏠 Main Menu", callback_data="home")
    b.adjust(1)
    return b.as_markup()

async def notify_admin(text: str):
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text)
        except Exception:
            logger.exception("Could not notify admin")

WELCOME = """
<b>🚀 Welcome to Technology Solution!</b>

Your trusted partner for professional IT and technology services.

We provide:
• Computer & printer maintenance
• Network & Wi-Fi solutions
• CCTV & security
• Software and Windows installation
• IT support
• VPN and remote-access solutions

Choose a service below to get started.
"""

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME, reply_markup=main_menu())

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "<b>Technology Solution Help</b>\n\n"
        "Use the buttons to request a service, ask for a quotation, "
        "view our services, or contact our team.",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "home")
async def home(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(WELCOME, reply_markup=main_menu())

@router.callback_query(F.data == "services")
async def services(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("<b>💻 Our Professional Services</b>\n\nSelect a service:", reply_markup=services_menu())

@router.callback_query(F.data.startswith("service:"))
async def service_detail(call: CallbackQuery):
    await call.answer()
    key = call.data.split(":", 1)[1]
    title, description = SERVICES[key]
    text = f"<b>{title}</b>\n\n{description}\n\n📋 Need this service? Tap <b>Request Service</b>."
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Request This Service", callback_data=f"request:{key}")],
        [InlineKeyboardButton(text="⬅️ Services", callback_data="services")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="home")]
    ])
    await call.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "products")
async def products(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "<b>🛒 Technology Products</b>\n\n"
        "We can help you source and configure:\n"
        "• Computers & laptops\n"
        "• Printers & consumables\n"
        "• Routers & switches\n"
        "• Wi-Fi equipment\n"
        "• Network cables & accessories\n"
        "• CCTV equipment\n\n"
        "Send us what you need and we will prepare a quotation.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Request Quote", callback_data="quote")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="home")]
        ])
    )

@router.callback_query(F.data == "contact")
async def contact(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "<b>📞 Contact Technology Solution</b>\n\n"
        "📱 Phone: 0912688641\n"
        "📧 Email: ararsa1221@gmail.com\n"
        "📍 Location: Dodola, Ethiopia\n"
        "🕒 Hours: Monday–Saturday\n\n"
        "For urgent technical support, send a service request through this bot.",
        reply_markup=back_menu()
    )

@router.callback_query(F.data == "language")
async def language(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "<b>🌍 Language</b>\n\n"
        "Choose your preferred language.\n\n"
        "🇬🇧 English\n"
        "🇪🇹 Afaan Oromo\n"
        "🇪🇹 Amharic\n\n"
        "Multilingual support can be expanded in the next version.",
        reply_markup=back_menu()
    )

@router.callback_query(F.data == "request")
async def request_general(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📋 Service Request</b>\n\n"
        "Please send one message containing:\n"
        "1. Your name\n"
        "2. Phone number\n"
        "3. Service you need\n"
        "4. Your location\n"
        "5. Short description of the problem\n\n"
        "You can also attach a photo of the problem."
    )

@router.callback_query(F.data.startswith("request:"))
async def request_specific(call: CallbackQuery):
    await call.answer()
    key = call.data.split(":", 1)[1]
    title = SERVICES[key][0]
    await call.message.answer(
        f"<b>📋 Request: {title}</b>\n\n"
        "Please reply with your name, phone number, location and a short description of what you need."
    )

@router.callback_query(F.data == "quote")
async def quote(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>💰 Get a Quote</b>\n\n"
        "Send your requirement in one message. Include quantities, equipment/model if known, "
        "installation location and your phone number.\n\n"
        "Our team will review it and contact you."
    )

@router.message(F.text)
async def customer_message(message: Message):
    if message.text.startswith("/"):
        return
    user = message.from_user
    customer = (
        f"🔔 <b>New Customer Request</b>\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🆔 Telegram ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username if user.username else 'N/A'}\n"
        f"🕒 Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"💬 Message:\n{message.text}"
    )
    await notify_admin(customer)
    await message.answer(
        "✅ <b>Request received!</b>\n\n"
        "Thank you for contacting Technology Solution. "
        "Our team will review your request and contact you soon.",
        reply_markup=main_menu()
    )

@router.message()
async def customer_nontext(message: Message):
    user = message.from_user
    await notify_admin(
        f"🔔 <b>New Customer Attachment</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 <code>{user.id}</code>\n"
        f"📎 Content type: {message.content_type}"
    )
    await message.answer(
        "✅ We received your attachment. Please also send your name, phone number, location and a short description.",
        reply_markup=main_menu()
    )

@app.get("/")
async def root():
    return {"status": "online", "service": "Technology Solution Telegram Bot"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    from aiogram.types import Update
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def startup():
    if WEBHOOK_URL:
        await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
        logger.info("Webhook configured: %s%s", WEBHOOK_URL, WEBHOOK_PATH)
    else:
        logger.warning("WEBHOOK_URL is not set. Set it in Render.")

@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    await bot.session.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
