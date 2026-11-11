
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from etl.extract import (
    get_previous_week_range,
    fetch_active_users,
    fetch_weekly_expenses
)

from etl.transform import transform_expenses
from etl.load import load_weekly_summaries

from reports.report_generator import generate_weekly_report
from reports.pdf_generator import generate_weekly_pdf

from services.email_service import send_email


# --------------------------------------------------
# Configure logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Main ETL Pipeline
# --------------------------------------------------

def run_etl():

    start_time = datetime.now(timezone.utc)

    logger.info("=" * 60)
    logger.info("WEEKLY EXPENSE ETL PIPELINE STARTED")
    logger.info("=" * 60)

    try:

        # STEP 1: Determine reporting period
        start_date, end_date = get_previous_week_range()

        # end_date is exclusive, so the actual report ends on Sunday.
        report_end_date = end_date - timedelta(days=1)

        logger.info(
            "Reporting period: %s to %s",
            start_date,
            report_end_date
        )

        # STEP 2: EXTRACT
        logger.info("Starting data extraction")

        users = fetch_active_users()

        expenses = fetch_weekly_expenses(
            start_date,
            end_date
        )

        logger.info("Active users extracted: %s", len(users))
        logger.info("Expense records extracted: %s", len(expenses))

        # STEP 3: TRANSFORM
        logger.info("Starting data transformation")

        result = transform_expenses(
            users=users,
            expenses=expenses,
            start_date=start_date,
            end_date=end_date
        )

        logger.info(
            "Valid expense records: %s",
            result["total_expense_records"]
        )

        logger.info(
            "Validation errors: %s",
            result["validation_error_count"]
        )

        # Stop if data validation fails.
        if result["validation_error_count"] > 0:

            for error in result["validation_errors"]:
                logger.error("Data quality issue: %s", error)

            raise ValueError(
                "ETL stopped because expense validation failed."
            )

        # STEP 4: LOAD
        logger.info("Starting data loading")

        load_weekly_summaries(result)

        logger.info("Weekly summaries loaded successfully.")

        # STEP 5: GENERATE REPORTS AND SEND EMAILS
        logger.info("Starting report generation and email delivery")

        successful_emails = 0
        failed_emails = 0

        # Temporary directory automatically removes PDFs after processing.
        with TemporaryDirectory() as temp_directory:

            for user_summary in result["user_summaries"]:

                user_id = user_summary["user_id"]
                user_email = user_summary["email"]

                try:

                    logger.info(
                        "Generating report for user_id=%s",
                        user_id
                    )

                    # Generate individual HTML report.
                    html_content = generate_weekly_report(
                        user_summary,
                        start_date,
                        end_date
                    )

                    # Generate individual PDF report.
                    pdf_path = Path(temp_directory) / (
                        f"weekly_expense_report_user_{user_id}.pdf"
                    )

                    generate_weekly_pdf(
                        user_summary,
                        start_date,
                        end_date,
                        pdf_path
                    )

                    # Email subject.
                    subject = (
                        f"Weekly Expense Report - "
                        f"{start_date} to {report_end_date}"
                    )

                    # Send email with PDF attachment.
                    send_email(
                        to_email=user_email,
                        subject=subject,
                        html_content=html_content,
                        pdf_path=pdf_path
                    )

                    successful_emails += 1

                    logger.info(
                        "Email sent successfully to user_id=%s",
                        user_id
                    )

                except Exception:

                    failed_emails += 1

                    logger.exception(
                        "Report generation/email failed for user_id=%s",
                        user_id
                    )

        logger.info("Successful emails: %s", successful_emails)
        logger.info("Failed emails: %s", failed_emails)

        if failed_emails > 0:
            raise RuntimeError(
                f"Email delivery failed for {failed_emails} user(s)."
            )

        # STEP 6: COMPLETION
        end_time = datetime.now(timezone.utc)

        duration = (end_time - start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("WEEKLY EXPENSE ETL COMPLETED SUCCESSFULLY")

        logger.info(
            "Users processed: %s",
            result["total_users"]
        )

        logger.info(
            "Expenses processed: %s",
            result["total_expense_records"]
        )

        logger.info(
            "Emails sent: %s",
            successful_emails
        )

        logger.info(
            "Execution time: %.2f seconds",
            duration
        )

        logger.info("=" * 60)

    except Exception:

        logger.exception("WEEKLY EXPENSE ETL FAILED")

        raise


# --------------------------------------------------
# Entry Point
# --------------------------------------------------

if __name__ == "__main__":
    run_etl()
