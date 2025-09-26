import re
from decimal import Decimal, InvalidOperation
from datetime import datetime


def validate_amount(amount_str):
    """Validate and convert amount string to Decimal"""
    if not amount_str:
        return None, "Amount is required"
    
    # Remove currency symbols and formatting
    cleaned_amount = re.sub(r'[Rp\s,.\(\)]', '', amount_str.strip())
    
    try:
        amount = Decimal(cleaned_amount)
        if amount <= 0:
            return None, "Amount must be greater than 0"
        return amount, None
    except InvalidOperation:
        return None, f"Invalid amount format: {amount_str}"


def validate_category(category):
    """Validate category name"""
    if not category:
        return False, "Category is required"
    
    if len(category.strip()) == 0:
        return False, "Category cannot be empty"
    
    if len(category.strip()) > 50:
        return False, "Category name too long (max 50 characters)"
    
    return True, None


def validate_date(date_str):
    """Validate date string in YYYY-MM-DD format"""
    if not date_str:
        return None, "Date is required"
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return date_obj, None
    except ValueError:
        return None, f"Invalid date format: {date_str}. Use YYYY-MM-DD format"


def validate_telegram_user_id(user_id):
    """Validate Telegram user ID"""
    try:
        user_id = int(user_id)
        if user_id <= 0:
            return None, "Invalid user ID"
        return user_id, None
    except (ValueError, TypeError):
        return None, "User ID must be a number"