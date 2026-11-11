
import json
from datetime import timedelta

from psycopg2.extras import Json

from database.database import get_db_connection


def json_serializer(value):
    return json.dumps(value, default=str)


def load_weekly_summaries(result):

    query = """
        INSERT INTO weekly_expense_reports (
            user_id,
            week_start,
            week_end,
            total_expenses,
            total_transactions,
            average_transaction,
            highest_category,
            highest_category_amount,
            category_totals,
            daily_totals,
            processed_at
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (user_id, week_start, week_end)
        DO UPDATE SET
            total_expenses = EXCLUDED.total_expenses,
            total_transactions = EXCLUDED.total_transactions,
            average_transaction = EXCLUDED.average_transaction,
            highest_category = EXCLUDED.highest_category,
            highest_category_amount = EXCLUDED.highest_category_amount,
            category_totals = EXCLUDED.category_totals,
            daily_totals = EXCLUDED.daily_totals,
            processed_at = CURRENT_TIMESTAMP;
    """

    start_date = result["start_date"]
    end_date = result["end_date"] - timedelta(days=1)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            for user in result["user_summaries"]:

                highest = user["highest_category"]

                highest_category = (
                    highest["category"] if highest else None
                )

                highest_amount = (
                    highest["amount"] if highest else None
                )

                category_json = Json(
                    user["category_totals"],
                    dumps=json_serializer
                )

                daily_json = Json(
                    {
                        day.isoformat(): amount
                        for day, amount in user["daily_totals"].items()
                    },
                    dumps=json_serializer
                )

                cursor.execute(
                    query,
                    (
                        user["user_id"],
                        start_date,
                        end_date,
                        user["total_expenses"],
                        user["total_transactions"],
                        user["average_transaction"],
                        highest_category,
                        highest_amount,
                        category_json,
                        daily_json
                    )
                )

        connection.commit()

        print(
            f"Successfully loaded "
            f"{len(result['user_summaries'])} weekly user summaries."
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
