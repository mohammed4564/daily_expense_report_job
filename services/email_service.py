
import os
import smtplib
import logging

from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_email(to_email, subject, html_content, pdf_path):

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    sender_name = os.getenv(
        "SENDER_NAME",
        "Daily Expense Tracker"
    )

    if not all([smtp_host, smtp_email, smtp_password]):
        raise ValueError("Missing Gmail SMTP configuration")

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = formataddr((sender_name, smtp_email))
    message["To"] = to_email

    message.set_content(
        "Hello,\n\n"
        "Please find your weekly expense report attached.\n\n"
        "Thank you,\nDaily Expense Tracker"
    )

    # HTML email content
    message.add_alternative(
        html_content,
        subtype="html"
    )

    # Attach PDF
    with open(pdf_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    message.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=os.path.basename(pdf_path)
    )

    try:
        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=30
        ) as server:

            server.starttls()

            server.login(
                smtp_email,
                smtp_password
            )

            server.send_message(message)

        logger.info("Email sent successfully to %s", to_email)

        return True

    except Exception:
        logger.exception("Email delivery failed to %s", to_email)
        raise
