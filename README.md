# QuillieBOT - Telegram Expense Tracker

A Telegram bot for tracking daily expenses with automatic and on-demand reporting.

## Features

- Multi-user support
- Quick expense entry: `/tambah 50000 makan "makan siang"`
- Guided expense entry with `/tambah`
- Daily, weekly, and monthly reports
- Automatic weekly reports
- Category management
- Budget setting
- Data export

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. The bot token is already configured in the `.env` file with the default token
2. To use your own bot token, update the `.env` file:

```
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///expenses.db
```

## Running the Bot

1. Make sure you have Python 3.8+ installed
2. Run the bot:
   ```
   python main.py
   ```

## Files for API Configuration

- `.env` - Contains the bot token and database URL
- `config.py` - Contains all configuration settings and can be modified for different tokens

## Commands

- `/start` - Start the bot and register
- `/help` - Show help message
- `/tambah` - Add an expense (guided) or `/tambah [amount] [category] [description]`
- `/laporan` - View today's expenses
- `/laporan minggu` - View weekly expenses
- `/laporan bulan` - View monthly expenses
- `/kategori` - View available categories
- `/set_budget [amount]` - Set monthly budget
- `/export` - Export your expense data

## Example Usage

```
/tambah 50000 makan "makan siang"
/tambah 75000 transportasi
/laporan minggu
/set_budget 5000000
```

## Architecture

- `main.py` - Entry point and bot initialization
- `config.py` - Configuration settings
- `database/` - Database models and operations
- `handlers/` - Command handlers
- `utils/` - Utility functions for validation and formatting

