from sqlalchemy.exc import IntegrityError
from .models import User, Expense, Category, get_session
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def register_user(telegram_user_id, username=None, first_name=None, last_name=None):
    """Register a new user or update existing user info"""
    session = get_session()
    try:
        # Check if user already exists
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        
        if user:
            # Update existing user info
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.weekly_report_enabled = True
        else:
            # Create new user
            user = User(
                telegram_user_id=telegram_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
        
        session.commit()
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Error registering user {telegram_user_id}: {str(e)}")
        raise
    finally:
        session.close()


def add_expense(telegram_user_id, amount, category, description=None):
    """Add a new expense for a user"""
    session = get_session()
    try:
        # Get user by telegram user ID
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Create new expense
        expense = Expense(
            user_id=user.user_id,
            amount=Decimal(str(amount)),
            category=category,
            description=description,
            date=date.today()
        )
        
        session.add(expense)
        session.commit()
        return expense
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding expense for user {telegram_user_id}: {str(e)}")
        raise
    finally:
        session.close()


def get_user_expenses(telegram_user_id, start_date=None, end_date=None):
    """Get expenses for a user within a date range"""
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not user:
            return []
        
        query = session.query(Expense).filter(Expense.user_id == user.user_id)
        
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        
        return query.all()
    finally:
        session.close()


def get_expenses_by_period(telegram_user_id, period):
    """Get expenses for a user by predefined period"""
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not user:
            return []
        
        today = date.today()
        
        if period == "today":
            start_date = today
            end_date = today
        elif period == "week":
            start_date = today - timedelta(days=today.weekday())  # Monday of current week
            end_date = start_date + timedelta(days=6)
        elif period == "month":
            start_date = today.replace(day=1)
            # Calculate end of month
            if today.month == 12:
                end_date = today.replace(day=31)
            else:
                next_month = today.replace(month=today.month + 1)
                end_date = next_month.replace(day=1) - timedelta(days=1)
        elif period == "year":
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:
            # For custom periods, assume period is a date string like "2024-01-01 2024-01-31"
            try:
                start_str, end_str = period.split()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
            except:
                return []
        
        expenses = session.query(Expense).filter(
            Expense.user_id == user.user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
        
        return expenses
    finally:
        session.close()


def get_weekly_expenses_comparison(telegram_user_id):
    """Get current week vs previous week expenses for comparison"""
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if not user:
            return {}, {}
        
        today = date.today()
        # Current week: Monday to Sunday of current week
        current_week_start = today - timedelta(days=today.weekday())
        current_week_end = current_week_start + timedelta(days=6)
        
        # Previous week: Monday to Sunday of previous week
        previous_week_start = current_week_start - timedelta(days=7)
        previous_week_end = current_week_end - timedelta(days=7)
        
        current_week_expenses = session.query(Expense).filter(
            Expense.user_id == user.user_id,
            Expense.date >= current_week_start,
            Expense.date <= current_week_end
        ).all()
        
        previous_week_expenses = session.query(Expense).filter(
            Expense.user_id == user.user_id,
            Expense.date >= previous_week_start,
            Expense.date <= previous_week_end
        ).all()
        
        current_total = sum(expense.amount for expense in current_week_expenses)
        previous_total = sum(expense.amount for expense in previous_week_expenses)
        
        return {
            'expenses': current_week_expenses,
            'total': current_total,
            'start_date': current_week_start,
            'end_date': current_week_end
        }, {
            'expenses': previous_week_expenses,
            'total': previous_total,
            'start_date': previous_week_start,
            'end_date': previous_week_end
        }
    finally:
        session.close()


def get_user_categories(telegram_user_id):
    """Get all categories for a user (both default and custom)"""
    session = get_session()
    try:
        # Get default categories
        default_categories = session.query(Category).filter(
            Category.is_default == True
        ).all()
        
        # Get user's custom categories
        user_categories = session.query(Category).filter(
            Category.user_id == telegram_user_id
        ).all()
        
        all_categories = [cat.category_name for cat in default_categories]
        all_categories.extend([cat.category_name for cat in user_categories])
        
        return list(set(all_categories))  # Remove duplicates
    finally:
        session.close()


def add_user_category(telegram_user_id, category_name):
    """Add a custom category for a user"""
    session = get_session()
    try:
        # Check if category already exists for this user
        existing = session.query(Category).filter(
            Category.user_id == telegram_user_id,
            Category.category_name == category_name
        ).first()
        
        if existing:
            return existing
        
        # Create new category
        category = Category(
            category_name=category_name,
            user_id=telegram_user_id
        )
        session.add(category)
        session.commit()
        return category
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding category for user {telegram_user_id}: {str(e)}")
        raise
    finally:
        session.close()


def get_user_by_telegram_id(telegram_user_id):
    """Get user by Telegram user ID"""
    session = get_session()
    try:
        return session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    finally:
        session.close()


def update_weekly_report_setting(telegram_user_id, enabled):
    """Update whether user receives weekly reports"""
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if user:
            user.weekly_report_enabled = enabled
            session.commit()
            return user
        return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating weekly report setting for user {telegram_user_id}: {str(e)}")
        raise
    finally:
        session.close()


def set_monthly_budget(telegram_user_id, budget_amount):
    """Set monthly budget for a user"""
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if user:
            user.monthly_budget = budget_amount
            session.commit()
            return user
        return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting monthly budget for user {telegram_user_id}: {str(e)}")
        raise
    finally:
        session.close()


def get_users_for_weekly_report():
    """Get all active users who want to receive weekly reports"""
    session = get_session()
    try:
        return session.query(User).filter(
            User.is_active == True,
            User.weekly_report_enabled == True
        ).all()
    finally:
        session.close()