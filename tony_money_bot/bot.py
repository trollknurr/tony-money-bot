import asyncio
import logging
import re

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from tony_money_bot.config import settings
from tony_money_bot.gsheet import get_categories, make_report, write_new_spent

logger = logging.getLogger(__name__)
MSG_RE = re.compile(r"([\d\.]+) (\w+)")


async def start_spent_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    if chat_id != settings.GROUP:
        logger.info("Update from a different group. Ignoring.")
        return

    if MSG_RE.match(update.message.text):
        logger.info("Getting categories...")
        categories = get_categories()
        logger.info("Sending keyboard...")
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(category, callback_data=ix)] for ix, category in enumerate(categories)]
        )
        await update.message.reply_text("Choose category:", reply_markup=reply_markup)

    else:
        await update.message.reply_text("Invalid message format.")


async def finish_spent_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Processing...")

    data = query.data
    category = get_categories()[int(data)]

    await query.edit_message_text("Adding to spreadsheet...")

    if m := MSG_RE.match(query.message.reply_to_message.text):
        amount, name = m.groups()
        amount = float(amount.replace(",", "."))
        write_new_spent(amount, category, name)

        await query.edit_message_text(f"Added {amount} to {category}")

    else:
        await query.edit_message_text("Error: not matched")


async def send_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Preparing report...")
    report = await asyncio.to_thread(make_report)
    await update.message.reply_text(
        "\n".join(f"{name}: {amount}" for name, amount in report.items()),
    )


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(settings.BOT_TOKEN.get_secret_value()).build()
    application.add_handler(CommandHandler("report", send_report))
    application.add_handler(MessageHandler(filters.ChatType.GROUP, start_spent_record))
    application.add_handler(CallbackQueryHandler(finish_spent_record))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
