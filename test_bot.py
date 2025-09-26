# test_bot.py - Simple test script to verify bot functionality

import asyncio
from database.models import initialize_database
from database.operations import register_user, add_expense, get_user_expenses
from utils.validators import validate_amount, validate_category
from utils.formatters import format_currency

def test_database():
    print("Testing database initialization...")
    initialize_database()
    print("✓ Database initialized")
    
    print("\\nTesting user registration...")
    user = register_user(123456789, "testuser", "Test", "User")
    print(f"✓ User registered: {user.first_name} {user.last_name}")
    
    print("\\nTesting expense addition...")
    expense = add_expense(123456789, 50000, "Makan", "Makan siang")
    print(f"✓ Expense added: {expense.amount} for {expense.category}")
    
    print("\\nTesting expense retrieval...")
    expenses = get_user_expenses(123456789)
    print(f"✓ Found {len(expenses)} expenses")
    for exp in expenses:
        print(f"  - {exp.amount} for {exp.category}")
    
    print("\\nTesting validators...")
    amount, error = validate_amount("50000")    
    if error:
        print(f"✗ Amount validation failed: {error}")
    else:
        print(f"✓ Amount validation: {amount}")
    
    is_valid, error = validate_category("Makan")
    if not is_valid:
        print(f"✗ Category validation failed: {error}")
    else:
        print(f"✓ Category validation passed")
    
    print("\\nTesting formatters...")
    formatted = format_currency(50000)
    print(f"✓ Currency formatted: {formatted}")

if __name__ == "__main__":
    test_database()
    print("\\n✓ All tests completed successfully!")
