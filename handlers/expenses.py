from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.operations import add_expense, get_user_categories, add_user_category
from utils.validators import validate_amount, validate_category
from utils.formatters import format_expense_message
import logging

logger = logging.getLogger(__name__)

# State constants for guided input
GUIDED_AMOUNT, GUIDED_CATEGORY, GUIDED_DESCRIPTION = range(3)


async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle receiving the expense amount in guided input\"\"\"
    user = update.effective_user
    telegram_user_id = user.id
    
    try:
        amount_str = update.message.text
        amount, error = validate_amount(amount_str)
        
        if error:
            await update.message.reply_text(f\"❌ {error}. Please enter a valid amount (e.g., 50000):\")
            return
        
        # Validate that this is actually a number the user entered (not a command)
        try:
            float(amount_str)
        except ValueError:
            await update.message.reply_text(\"❌ Please enter a valid amount (e.g., 50000):\")
            return
        
        # Store amount in user context
        if 'guided_expense' not in context.user_data:
            context.user_data['guided_expense'] = {}
        context.user_data['guided_expense']['amount'] = amount
        
        # Get user's available categories
        categories = get_user_categories(telegram_user_id)
        
        # Format categories for display
        categories_text = \"\\n\".join([f\"  • {cat}\" for cat in categories])
        await update.message.reply_text(
            f\"Jumlah pengeluaran: {amount:,}\\n\\n\"
            f\"Pilih kategori berikut atau ketik kategori baru:\\n\"
            f\"{categories_text}\\n\\n\"
            f\"Ketik nama kategori:\"
        )
        
        # We'll handle the category input using a different approach since we're not using ConversationHandler
        # The next message from the user will be handled as category input
        # This requires setting state in the user context
        context.user_data['awaiting_category'] = True
        
    except Exception as e:
        logger.error(f\"Error receiving amount: {str(e)}\")
        await update.message.reply_text(f\"❌ Error: {str(e)}\")


async def add_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle the /tambah command - can be used with arguments or start guided input\"\"\"
    user = update.effective_user
    telegram_user_id = user.id
    
    # Check if we're awaiting category input for guided flow
    if context.user_data.get('awaiting_category'):
        # This is category input for guided flow
        category = update.message.text.strip()
        
        # Validate category
        is_valid, error = validate_category(category)
        if not is_valid:
            await update.message.reply_text(f\"❌ {error}\")
            return
        
        # Store category in user context
        context.user_data['guided_expense']['category'] = category
        await update.message.reply_text(\"Masukkan deskripsi (opsional):\")
        
        # Set state to awaiting description
        context.user_data['awaiting_category'] = False
        context.user_data['awaiting_description'] = True
        return
    
    # Check if we're awaiting description input for guided flow
    elif context.user_data.get('awaiting_description'):
        # This is description input for guided flow
        description = update.message.text.strip()
        
        # Store description in user context and complete the expense
        context.user_data['guided_expense']['description'] = description if description.lower() != 'skip' else None
        
        # Get stored amount and category
        amount = context.user_data['guided_expense'].get('amount')
        category = context.user_data['guided_expense'].get('category')
        description = context.user_data['guided_expense']['description']
        
        try:
            # Add new category if it doesn't exist for this user
            categories = get_user_categories(telegram_user_id)
            if category not in categories:
                add_user_category(telegram_user_id, category)
            
            # Add expense to database
            expense = add_expense(telegram_user_id, amount, category, description)
            
            # Send success message
            success_message = f\"✅ Pengeluaran tercatat!\\n{format_expense_message(expense)}\"
            await update.message.reply_text(success_message)
            
        except Exception as e:
            logger.error(f\"Error saving guided expense: {str(e)}\")
            await update.message.reply_text(f\"❌ Error occurred while saving expense: {str(e)}\")
        finally:
            # Clear user data
            context.user_data.clear()
        
        return
    
    # If arguments are provided, add expense directly
    if context.args:
        if len(context.args) < 2:
            await update.message.reply_text(
                \"❌ Usage: /tambah [amount] [category] [description?]\\n\"
                \"Example: /tambah 50000 makan 'makan siang'\"
            )
            return
        
        # Parse arguments
        try:
            amount_str = context.args[0]
            category = context.args[1]
            description = \" \".join(context.args[2:]) if len(context.args) > 2 else None
            
            # Validate amount
            amount, error = validate_amount(amount_str)
            if error:
                await update.message.reply_text(f\"❌ {error}\")
                return
            
            # Validate category
            is_valid, error = validate_category(category)
            if not is_valid:
                await update.message.reply_text(f\"❌ {error}\")
                return
            
            # Add expense to database
            expense = add_expense(telegram_user_id, amount, category, description)
            
            # Send confirmation message
            success_message = f\"✅ Pengeluaran tercatat!\\n{format_expense_message(expense)}\"
            await update.message.reply_text(success_message)
            
        except Exception as e:
            logger.error(f\"Error adding expense: {str(e)}\")
            await update.message.reply_text(f\"❌ Error occurred while adding expense: {str(e)}\")
    else:
        # Start guided input - we handle this in main.py by sending the prompt
        # The actual handling of the amount input will be in receive_amount
        pass


async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle receiving the expense amount"""
    user = update.effective_user
    telegram_user_id = user.id
    
    try:
        amount_str = update.message.text
        amount, error = validate_amount(amount_str)
        
        if error:
            await update.message.reply_text(f"❌ {error}. Please enter a valid amount (e.g., 50000):")
            return AMOUNT
        
        # Store amount in user context
        context.user_data['expense_amount'] = amount
        
        # Get user's available categories
        categories = get_user_categories(telegram_user_id)
        
        # Create inline keyboard for categories
        keyboard = []
        for cat in categories:
            keyboard.append([InlineKeyboardButton(cat, callback_data=f"cat_{cat}")])
        
        # Add option to add new category
        keyboard.append([InlineKeyboardButton("➕ Add New Category", callback_data="new_category")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Pilih kategori:", reply_markup=reply_markup)
        
        return CATEGORY
    except Exception as e:
        logger.error(f"Error receiving amount: {str(e)}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
        return ConversationHandler.END


async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle receiving the expense category"""
    query = update.callback_query
    await query.answer()
    
    # Extract category from callback data
    if query.data.startswith("cat_"):
        category = query.data[4:]  # Remove "cat_" prefix
    elif query.data == "new_category":
        await query.edit_message_text("Masukkan nama kategori baru:")
        return CATEGORY
    else:
        # Direct text input for category
        category = query.data
    
    # If it's a new category, handle it
    if query.data == "new_category":
        # Store category in user context
        context.user_data['expense_category'] = category
        await query.edit_message_text(f"Nama kategori yang dimasukkan: {category}")
        await query.message.reply_text("Masukkan deskripsi (opsional):")
        return DESCRIPTION
    else:
        # Validate category
        is_valid, error = validate_category(category)
        if not is_valid:
            await query.edit_message_text(f"❌ {error}")
            return ConversationHandler.END
        
        # Store category in user context
        context.user_data['expense_category'] = category
        
        await query.edit_message_text(f"Kategori dipilih: {category}")
        await query.message.reply_text("Masukkan deskripsi (opsional):")
        return DESCRIPTION


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle receiving the expense description"""
    description = update.message.text
    
    # Store description in user context
    context.user_data['expense_description'] = description if description.strip() else None
    
    # Get stored amount and category
    amount = context.user_data.get('expense_amount')
    category = context.user_data.get('expense_category')
    description = context.user_data.get('expense_description')
    
    # Show confirmation message
    confirm_text = f"Konfirmasi pengeluaran:\n\n💰 {amount} - {category}"
    if description:
        confirm_text += f" - {description}"
    
    keyboard = [
        [InlineKeyboardButton("✅ Simpan", callback_data="confirm_yes"),
         InlineKeyboardButton("❌ Batal", callback_data="confirm_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirm_text, reply_markup=reply_markup)
    
    return CONFIRM


async def confirm_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expense confirmation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_yes":
        user = update.effective_user
        telegram_user_id = user.id
        
        try:
            # Get stored data
            amount = context.user_data.get('expense_amount')
            category = context.user_data.get('expense_category')
            description = context.user_data.get('expense_description')
            
            # Add new category if it doesn't exist for this user
            categories = get_user_categories(telegram_user_id)
            if category not in categories:
                add_user_category(telegram_user_id, category)
            
            # Add expense to database
            expense = add_expense(telegram_user_id, amount, category, description)
            
            # Send success message
            success_message = f"✅ Pengeluaran tercatat!\n{format_expense_message(expense)}"
            await query.edit_message_text(success_message)
            
        except Exception as e:
            logger.error(f"Error confirming expense: {str(e)}")
            await query.edit_message_text(f"❌ Error occurred while saving expense: {str(e)}")
    
    elif query.data == "confirm_no":
        await query.edit_message_text("❌ Pengeluaran dibatalkan.")
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the expense addition process"""
    await update.message.reply_text("❌ Pengeluaran dibatalkan.")
    context.user_data.clear()
    return ConversationHandler.END


def get_expense_conversation_handler():
    """Return the conversation handler for guided expense input"""
    from telegram.ext import ConversationHandler, MessageHandler, filters, CallbackQueryHandler
    
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^\d+'), receive_amount)],  # For direct amount input
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
            CATEGORY: [
                CallbackQueryHandler(receive_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category)  # For new category input
            ],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            CONFIRM: [CallbackQueryHandler(confirm_expense)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel_expense)]
    )