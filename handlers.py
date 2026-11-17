import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import OWNER_ID, SERVICE_DOMAINS
from database import is_authorized, add_admin_record, remove_admin_record, get_admin_ids
from gmail_service import search_latest_service_email

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def authorized(update: Update) -> bool:
    return bool(update.effective_user and is_authorized(update.effective_user.id))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("Access denied. Ask the bot owner for access.")
        return
    keyboard = [[InlineKeyboardButton(name, callback_data=f"service:{name}")]
                for name in SERVICE_DOMAINS]
    await update.message.reply_text(
        "Choose a service first. Then send the email address to search for a matching "
        "message in the connected Gmail inbox.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_authorized(query.from_user.id):
        await query.edit_message_text("Access denied.")
        return
    service = query.data.split(":", 1)[1]
    context.user_data["selected_service"] = service
    await query.edit_message_text(
        f"Selected: {service}\n\nNow send the email address to use as the recipient filter."
    )

async def email_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("Access denied.")
        return
    service = context.user_data.get("selected_service")
    if not service:
        await update.message.reply_text("Please choose Disney+, Netflix, or ChatGPT first using /start.")
        return
    address = update.message.text.strip()
    if not EMAIL_RE.match(address):
        await update.message.reply_text("That doesn't look like a valid email address. Please try again.")
        return
    await update.message.reply_text(f"Checking the connected Gmail inbox for a {service} message to {address}…")
    try:
        result = search_latest_service_email(service, address)
        if not result:
            await update.message.reply_text(
                f"No matching {service} email was found for {address} in the connected Gmail inbox."
            )
        else:
            await update.message.reply_text(
                f"Matching email found\n"
                f"Service: {service}\n"
                f"Recipient filter: {address}\n"
                f"From: {result['from']}\n"
                f"Subject: {result['subject']}\n"
                f"Received: {result['date']}\n\n"
                "For security, this bot displays email metadata only; it does not extract or forward login codes."
            )
    except Exception as exc:
        await update.message.reply_text(f"Could not search Gmail: {exc}")
    finally:
        context.user_data.pop("selected_service", None)

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can add admins.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /addadmin TELEGRAM_USER_ID")
        return
    user_id = int(context.args[0])
    add_admin_record(user_id, OWNER_ID)
    await update.message.reply_text(f"Admin added: {user_id}")

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can remove admins.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /removeadmin TELEGRAM_USER_ID")
        return
    try:
        remove_admin_record(int(context.args[0]))
        await update.message.reply_text(f"Admin removed: {context.args[0]}")
    except ValueError as exc:
        await update.message.reply_text(str(exc))

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can view the admin list.")
        return
    ids = get_admin_ids()
    await update.message.reply_text("Authorized admins:\n" + ("\n".join(map(str, ids)) if ids else "(none)"))
