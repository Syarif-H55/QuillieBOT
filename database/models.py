from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)  # For unsubscribing from weekly reports
    weekly_report_enabled = Column(Boolean, default=True)  # Whether to receive weekly reports
    monthly_budget = Column(DECIMAL(10, 2))  # Optional monthly budget
    
    expenses = relationship("Expense", back_populates="user")


class Expense(Base):
    __tablename__ = 'expenses'
    
    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(255), nullable=False)
    description = Column(String(500))  # Optional description
    date = Column(Date, default=datetime.now().date())
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="expenses")


class Category(Base):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)  # Null for default categories
    is_default = Column(Boolean, default=False)  # True for default categories


def get_database_url():
    """Get the database URL from environment or default to SQLite"""
    from config import DATABASE_URL
    return DATABASE_URL


def get_engine():
    """Create and return a database engine"""
    database_url = get_database_url()
    return create_engine(database_url)


def get_session():
    """Create and return a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def initialize_database():
    """Initialize the database with tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    session = get_session()
    
    # Add default categories if they don't exist
    from config import DEFAULT_CATEGORIES
    existing_categories = session.query(Category).filter(Category.is_default == True).all()
    
    if not existing_categories:
        for cat_name in DEFAULT_CATEGORIES:
            default_category = Category(
                category_name=cat_name,
                is_default=True
            )
            session.add(default_category)
        session.commit()
    
    session.close()