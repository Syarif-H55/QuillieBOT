from telegram import Update
from telegram.ext import ContextTypes
from database.operations import register_user
from config import DEFAULT_CATEGORIES


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle the /start command\"\"\"
    user = update.effective_user
    telegram_user_id = user.id
    
    # Register or update user in database
    db_user = register_user(
        telegram_user_id=telegram_user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Send welcome message
    welcome_message = (
        f\"👋 Hello {user.first_name}!\\n\\n\"
        f\"Welcome to QuillieBOT - Your personal expense tracker!\\n\\n\"
        f\"📝 You can start tracking your expenses with these commands:\\n\\n\"
        f\"• /tambah [amount] [category] [description] - Add expense quickly\\n\"
        f\"• /tambah - Add expense with guided input\\n\"
        f\"• /laporan - View today's expenses\\n\"
        f\"• /laporan minggu - View weekly expenses\\n\"
        f\"• /laporan bulan - View monthly expenses\\n\\n\"
        f\"🏷️ Available categories: {', '.join(DEFAULT_CATEGORIES)}\\n\\n\"
        f\"Need help? Just type /help to see all available commands!\"
    )
    
    await update.message.reply_text(welcome_message)