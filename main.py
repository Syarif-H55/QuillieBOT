import logging
import os
import sys
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Initialize logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Import handlers and database functions
from config import BOT_TOKEN
from database.models import initialize_database
from handlers.start import start
from handlers.expenses import add_expense_command, receive_amount
from handlers.reports import (
    report_command,
    categories_command,
    set_budget_command,
    export_command,
)
from handlers.scheduler import ReportScheduler


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message to the user"""
    help_text = (
        "📖 <b>QuillieBOT - Expense Tracker Help</b>\n\n"
        "<b>Commands:</b>\n"
        "/start - Start the bot and register\n"
        "/help - Show this help message\n"
        "/tambah - Add an expense (guided) or /tambah [amount] [category] [description]\n"
        "/laporan - View today's expenses\n"
        "/laporan minggu - View weekly expenses\n"
        "/laporan bulan - View monthly expenses\n"
        "/kategori - View available categories\n"
        "/set_budget - Set monthly budget /set_budget [amount]\n"
        "/export - Export your expense data\n\n"
        "Example usage:\n"
        '/tambah 50000 makan "makan siang"\n'
        '/tambah 75000 transportasi "transportasi ke tempat"\n'
    )
    await update.message.reply_html(help_text)


async def setup_bot_commands(application: Application):
    """Set up bot commands"""
    commands = [
        BotCommand("start", "Start the bot and register"),
        BotCommand("help", "Show help message"),
        BotCommand("tambah", "Add an expense"),
        BotCommand("laporan", "View expense report"),
        BotCommand("kategori", "View available categories"),
        BotCommand("set_budget", "Set monthly budget"),
        BotCommand("export", "Export expense data"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    """Start the bot"""
    # Initialize database
    initialize_database()
    logger.info("Database initialized")

    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("laporan", report_command))
    application.add_handler(CommandHandler("kategori", categories_command))
    application.add_handler(CommandHandler("set_budget", set_budget_command))
    application.add_handler(CommandHandler("export", export_command))

    # Handle the /tambah command separately to determine if it has arguments
    async def tambah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            # If there are command arguments, process directly
            await add_expense_command(update, context)
        else:
            # If no arguments, start guided flow
            await update.message.reply_text(
                "Masukkan jumlah pengeluaran (contoh: 50000 makan):"
            )

    application.add_handler(CommandHandler("tambah", tambah_command))

    # Handle guided expense input (text messages after /tambah without args)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)
    )

    # Setup bot commands (dipanggil lewat post_init)
    async def post_init(app: Application) -> None:
        await setup_bot_commands(app)

    application.post_init = post_init

    # Initialize scheduler
    scheduler = ReportScheduler()
    scheduler.start_scheduler()
    logger.info("Scheduler started")

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),  # ambil port dari Railway
        url_path="7628457855:AAH1VSKv9iHJ0xHozGRm6dhSucV91rfGLV8",
        webhook_url=f"https://{os.environ.get('RAILWAY_STATIC_URL')}/{"7628457855:AAH1VSKv9iHJ0xHozGRm6dhSucV91rfGLV8"}",
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
