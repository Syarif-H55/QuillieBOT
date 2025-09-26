from decimal import Decimal
import matplotlib.pyplot as plt
import io
from datetime import date, datetime
from config import CURRENCY_SYMBOL


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "Rp 0"

    # Convert to Decimal if it's not already
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    # Format with thousands separator and currency symbol
    formatted_amount = f"{CURRENCY_SYMBOL}{amount:,.0f}".replace(",", ".")
    return formatted_amount


def format_date_range(start_date, end_date):
    """Format a date range for display"""
    if start_date == end_date:
        return start_date.strftime("%d %b %Y")
    else:
        return f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"


def format_expense_message(expense):
    """Format a single expense as a message"""
    message = f"💰 {format_currency(expense.amount)}"
    message += f"🏷️ {expense.category}"
    if expense.description:
        message += f"📝 {expense.description}"
    message += f"📅 {expense.date.strftime('%d %b %Y')}"
    return message


def format_expense_summary(expenses):
    """Format a list of expenses with total and category breakdown"""
    if not expenses:
        return "❌ No expenses found for this period."

    total_amount = sum(expense.amount for expense in expenses)
    message = f"📊 Total: {format_currency(total_amount)}\n"
    message += "──────────────────\n"

    # Group expenses by category
    category_totals = {}
    for expense in expenses:
        category = expense.category
        if category not in category_totals:
            category_totals[category] = Decimal('0')
        category_totals[category] += expense.amount

    # Sort categories by amount (descending)
    sorted_categories = sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Calculate percentages and format
    for category, amount in sorted_categories:
        percentage = (amount / total_amount) * 100
        message += f"  {category}: {format_currency(amount)} ({percentage:.0f}%)\n"

    return message


def format_weekly_comparison(current_data, previous_data):
    """Format comparison between current and previous week"""
    if not current_data or not previous_data:
        return ""

    current_total = current_data['total']
    previous_total = previous_data['total']

    if previous_total == 0:
        if current_total == 0:
            change_text = "0% (no change)"
            change_emoji = "➡️"
        else:
            change_text = "100% (new)"
            change_emoji = "🆕"
    else:
        change_percent = ((current_total - previous_total) / previous_total) * 100
        if change_percent > 0:
            change_text = f"{change_percent:+.0f}%"
            change_emoji = "📈"
        elif change_percent < 0:
            change_text = f"{change_percent:+.0f}%"
            change_emoji = "📉"
        else:
            change_text = f"{change_percent:+.0f}%"
            change_emoji = "➡️"

    return f"\n📈 vs previous week: {change_text} {change_emoji}"


def format_report_message(expenses, period_name, start_date, end_date, comparison_data=None):
    """Format a complete report message"""
    period_display = format_date_range(start_date, end_date)
    message = f"📊 Laporan {period_name.title()} ({period_display})\n\n"

    # Add expense summary
    message += format_expense_summary(expenses)

    # Add comparison if available
    if comparison_data:
        current_data, previous_data = comparison_data
        message += format_weekly_comparison(current_data, previous_data)

    return message


def create_expense_chart(expenses):
    """Create a simple chart image of expenses by category"""
    if not expenses:
        return None

    # Group expenses by category
    category_totals = {}
    for expense in expenses:
        category = expense.category
        if category not in category_totals:
            category_totals[category] = Decimal('0')
        category_totals[category] += expense.amount

    # Prepare data for chart
    categories = list(category_totals.keys())
    amounts = [float(amount) for amount in category_totals.values()]

    # Create the chart
    plt.figure(figsize=(10, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title('Pengeluaran Berdasarkan Kategori')

    # Save chart to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()

    return img_buffer


def format_categories_list(categories):
    """Format a list of categories for display"""
    if not categories:
        return "❌ No categories found."

    message = "🏷️ Categories:\n"
    for i, category in enumerate(categories, 1):
        message += f"  {i}. {category}\n"

    return message


def format_budget_message(budget, current_spending):
    """Format budget status message"""
    if budget is None:
        return "❌ Budget not set. Use /set_budget to set your monthly budget."

    budget = float(budget)
    current_spending = float(current_spending)
    remaining = budget - current_spending
    percentage = (current_spending / budget) * 100

    status_emoji = "🟢" if percentage < 50 else "🟡" if percentage < 80 else "🔴"

    message = f"💰 Monthly Budget: {format_currency(budget)}\n"
    message += f"💳 Spent: {format_currency(current_spending)} ({percentage:.1f}%)\n"
    message += f"✅ Remaining: {format_currency(remaining)}\n"
    message += f"{status_emoji} Status: "

    if percentage >= 100:
        message += "⚠️ Budget exceeded!"
    elif percentage >= 90:
        message += "⚠️ Approaching budget limit!"
    elif percentage >= 75:
        message += "⚠️ Close to budget limit"
    else:
        message += "✅ Within budget"

    return message
