import logging
import asyncio
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from database.operations import (
    get_users_for_weekly_report,
    get_weekly_expenses_comparison,
)
from utils.formatters import format_report_message, format_currency
from config import BOT_TOKEN, SCHEDULER_TIMEZONE, WEEKLY_REPORT_HOUR

logger = logging.getLogger(__name__)


class ReportScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.bot = Bot(token=BOT_TOKEN)

    def start_scheduler(self):
        """Start the scheduler for weekly reports"""
        # Schedule weekly report on Monday at specified hour (WIB)
        self.scheduler.add_job(
            self.send_weekly_reports,
            CronTrigger(
                day_of_week="mon",
                hour=WEEKLY_REPORT_HOUR,
                timezone=SCHEDULER_TIMEZONE,
            ),
            id="weekly_report_job",
            name="Send weekly expense reports to users",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Scheduler started for weekly reports")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    async def send_weekly_reports(self):
        """Send weekly reports to all active users"""
        try:
            users = get_users_for_weekly_report()
            logger.info(f"Sending weekly reports to {len(users)} users")

            for user in users:
                try:
                    # Get weekly expenses comparison
                    current_data, previous_data = get_weekly_expenses_comparison(
                        user.telegram_user_id
                    )

                    # Only send report if there are expenses this week
                    if current_data["expenses"]:
                        # Format the report message
                        period_name = "Minggu Ini"
                        start_date = current_data["start_date"]
                        end_date = current_data["end_date"]
                        comparison_data = (current_data, previous_data)

                        report_message = format_report_message(
                            current_data["expenses"],
                            period_name,
                            start_date,
                            end_date,
                            comparison_data,
                        )

                        # Add comparison info
                        if previous_data["total"] > 0:
                            change = (
                                (current_data["total"] - previous_data["total"])
                                / previous_data["total"]
                            ) * 100
                            direction = (
                                "📈"
                                if current_data["total"] > previous_data["total"]
                                else "📉"
                            )
                            report_message += (
                                f"\n\nPerbandingan vs minggu lalu: {change:+.1f}% {direction}"
                            )

                        # Send the report to user
                        await self.bot.send_message(
                            chat_id=user.telegram_user_id,
                            text=f"📅 Weekly Expense Report\n\n{report_message}",
                        )
                    else:
                        # Send a message saying no expenses this week
                        await self.bot.send_message(
                            chat_id=user.telegram_user_id,
                            text=(
                                "📅 Weekly Expense Report\n\n"
                                "This week you have no recorded expenses. "
                                "Keep tracking your expenses to see your spending patterns!"
                            ),
                        )

                except Exception as e:
                    logger.error(
                        f"Error sending report to user {user.telegram_user_id}: {str(e)}"
                    )
                    # Continue with next user even if one fails

        except Exception as e:
            logger.error(f"Error in send_weekly_reports: {str(e)}")

    def send_weekly_report_to_user(self, telegram_user_id):
        """Send weekly report to a specific user (for testing or on-demand)"""
        try:
            # Get weekly expenses comparison
            current_data, previous_data = get_weekly_expenses_comparison(
                telegram_user_id
            )

            # Format the report message
            period_name = "Minggu Ini"
            start_date = current_data["start_date"]
            end_date = current_data["end_date"]
            comparison_data = (current_data, previous_data)

            report_message = format_report_message(
                current_data["expenses"],
                period_name,
                start_date,
                end_date,
                comparison_data,
            )

            # Add comparison info
            if previous_data["total"] > 0:
                change = (
                    (current_data["total"] - previous_data["total"])
                    / previous_data["total"]
                ) * 100
                direction = (
                    "📈" if current_data["total"] > previous_data["total"] else "📉"
                )
                report_message += (
                    f"\n\nPerbandingan vs minggu lalu: {change:+.1f}% {direction}"
                )

            return report_message

        except Exception as e:
            logger.error(
                f"Error generating weekly report for user {telegram_user_id}: {str(e)}"
            )
            return f"Error generating report: {str(e)}"
