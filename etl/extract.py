
from datetime import date, timedelta

from database.database import get_db_connection


def get_previous_week_range(reference_date=None):
    """
    Returns the previous Monday-to-Sunday reporting period.

    The end date is exclusive.
    Example:
        start_date = Monday
        end_date   = following Monday
    """
    if reference_date is None:
        reference_date = date.today()

    current_monday = (
        reference_date
        - timedelta(days=reference_date.weekday())
    )

    start_date = current_monday - timedelta(days=7)
    end_date = current_monday

    return start_date, end_date


def fetch_active_users():
    """Fetch all active users without retrieving password hashes."""

    query = """
        SELECT
            user_id,
            username,
            email,
            full_name
        FROM users
        WHERE is_active = TRUE
        ORDER BY user_id;
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

            columns = [column[0] for column in cursor.description]

            users = [
                dict(zip(columns, row))
                for row in rows
            ]

            return users

    finally:
        connection.close()


def fetch_weekly_expenses(start_date, end_date):
    """
    Fetch expenses belonging to active users
    within the requested reporting period.

    end_date is exclusive.
    """

    query = """
        SELECT
            u.user_id,
            u.username,
            u.email,
            u.full_name,
            e.expense_id,
            e.expense_date,
            e.category,
            e.description,
            e.amount
        FROM users u
        INNER JOIN expenses e
            ON u.user_id = e.user_id
        WHERE
            u.is_active = TRUE
            AND e.expense_date >= %s
            AND e.expense_date < %s
        ORDER BY
            u.user_id,
            e.expense_date,
            e.expense_id;
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (start_date, end_date)
            )

            rows = cursor.fetchall()

            columns = [column[0] for column in cursor.description]

            expenses = [
                dict(zip(columns, row))
                for row in rows
            ]

            return expenses

    finally:
        connection.close()

