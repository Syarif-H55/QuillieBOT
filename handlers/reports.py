from telegram import Update
from telegram.ext import ContextTypes
from database.operations import get_expenses_by_period, get_weekly_expenses_comparison, get_user_by_telegram_id
from utils.formatters import format_report_message, create_expense_chart, format_currency
from datetime import date, timedelta, datetime
import logging

logger = logging.getLogger(__name__)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle the /laporan command\"\"\"
    user = update.effective_user
    telegram_user_id = user.id
    
    # Determine the report period
    period = \"today\"  # Default to today
    
    if context.args:
        arg = context.args[0].lower()
        if arg in [\"hari\", \"today\", \"harian\"]:
            period = \"today\"
        elif arg in [\"minggu\", \"week\", \"mingguan\"]:
            period = \"week\"
        elif arg in [\"bulan\", \"month\", \"bulanan\"]:
            period = \"month\"
        elif arg in [\"tahun\", \"year\", \"tahunan\"]:
            period = \"year\"
        else:
            # Check if it's a custom date range
            try:
                # Parse custom date range like \"2024-01-01 2024-01-31\"
                if len(context.args) >= 2:
                    start_date = context.args[0]
                    end_date = context.args[1]
                    period = f\"{start_date} {end_date}\"
                else:
                    await update.message.reply_text(
                        \"❌ Periode tidak valid. Gunakan: /laporan [hari|minggu|bulan|tahun] atau \"
                        \"/laporan [tanggal_mulai] [tanggal_akhir] (format: YYYY-MM-DD)\"
                    )
                    return
            except Exception:
                await update.message.reply_text(
                    \"❌ Periode tidak valid. Gunakan: /laporan [hari|minggu|bulan|tahun] atau \"
                    \"/laporan [tanggal_mulai] [tanggal_akhir] (format: YYYY-MM-DD)\"
                )
                return
    
    try:
        # Get expenses for the specified period
        expenses = get_expenses_by_period(telegram_user_id, period)
        
        # Determine display name and dates based on period
        today = date.today()
        if period == \"today\":
            period_name = \"Hari Ini\"
            start_date = end_date = today
            comparison_data = None
        elif period == \"week\":
            period_name = \"Minggu Ini\"
            start_date = today - timedelta(days=today.weekday())  # Monday
            end_date = start_date + timedelta(days=6)  # Sunday
            # Get comparison data for weekly reports
            comparison_data = get_weekly_expenses_comparison(telegram_user_id)
        elif period == \"month\":
            period_name = \"Bulan Ini\"
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(day=31)
            else:
                next_month = today.replace(month=today.month + 1)
                end_date = next_month.replace(day=1) - timedelta(days=1)
            comparison_data = None
        elif period == \"year\":
            period_name = \"Tahun Ini\"
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            comparison_data = None
        else:
            # Custom date range
            period_name = \"Custom\"
            start_date_str, end_date_str = period.split()
            start_date = datetime.strptime(start_date_str, \"%Y-%m-%d\").date()
            end_date = datetime.strptime(end_date_str, \"%Y-%m-%d\").date()
            comparison_data = None
        
        # Format and send report message
        report_message = format_report_message(expenses, period_name, start_date, end_date, comparison_data)
        await update.message.reply_text(report_message)
        
        # If it's a weekly report, also send comparison
        if period == \"week\" and comparison_data:
            current_data, previous_data = comparison_data
            if current_data['total'] > 0 or previous_data['total'] > 0:
                comparison_message = (
                    f\"📊 Perbandingan Minggu Ini vs Minggu Lalu:\\n\"
                    f\" minggu ini: {format_currency(current_data['total'])}\\n\"
                    f\" minggu lalu: {format_currency(previous_data['total'])}\"
                )
                await update.message.reply_text(comparison_message)
    
    except Exception as e:
        logger.error(f\"Error generating report: {str(e)}\")
        await update.message.reply_text(f\"❌ Error occurred while generating report: {str(e)}\")


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle the /kategori command\"\"\"
    user = update.effective_user
    telegram_user_id = user.id
    
    try:
        from database.operations import get_user_categories
        from utils.formatters import format_categories_list
        
        categories = get_user_categories(telegram_user_id)
        message = format_categories_list(categories)
        await update.message.reply_text(message)
    
    except Exception as e:
        logger.error(f\"Error getting categories: {str(e)}\")
        await update.message.reply_text(f\"❌ Error occurred while getting categories: {str(e)}\")


async def set_budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle the /set_budget command\"\"\"
    user = update.effective_user
    telegram_user_id = user.id
    
    if not context.args:
        await update.message.reply_text(
            \"❌ Usage: /set_budget [amount]\\n\"
            \"Example: /set_budget 5000000\"
        )
        return
    
    try:
        from database.operations import set_monthly_budget
        from utils.validators import validate_amount
        
        budget_str = context.args[0]
        budget_amount, error = validate_amount(budget_str)
        
        if error:
            await update.message.reply_text(f\"❌ {error}\")
            return
        
        # Update user's budget in database
        updated_user = set_monthly_budget(telegram_user_id, budget_amount)
        
        from utils.formatters import format_currency
        success_message = f\"✅ Monthly budget set to {format_currency(budget_amount)}\"
        await update.message.reply_text(success_message)
    
    except Exception as e:
        logger.error(f\"Error setting budget: {str(e)}\")
        await update.message.reply_text(f\"❌ Error occurred while setting budget: {str(e)}\")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Handle the /export command\"\"\"
    # This would export expenses to a file (CSV, etc.)
    # For now, just send a placeholder message
    message = \"📤 Export feature is coming soon! You'll be able to download your expense data as CSV.\"
    await update.message.reply_text(message)