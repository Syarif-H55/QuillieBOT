import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7628457855:AAH1VSKv9iHJ0xHozGRm6dhSucV91rfGLV8")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///expenses.db")

# Scheduler configuration
SCHEDULER_TIMEZONE = "Asia/Jakarta"  # WIB timezone
WEEKLY_REPORT_HOUR = 9  # 09:00 WIB
WEEKLY_REPORT_DAY = 0  # Monday (0-6, Monday is 0)

# Default categories
DEFAULT_CATEGORIES = [
    "Makan", 
    "Transportasi", 
    "Belanja", 
    "Kesehatan", 
    "Hiburan", 
    "Pendidikan", 
    "Lainnya"
]

# Currency formatting
CURRENCY_SYMBOL = "Rp "