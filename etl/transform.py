
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation


ZERO = Decimal("0.00")


def transform_expenses(users, expenses, start_date, end_date):
    """
    Transform weekly expense records into user-wise summaries.

    Parameters:
        users: Active user records from PostgreSQL.
        expenses: Weekly expense records from PostgreSQL.
        start_date: First reporting date (inclusive).
        end_date: Last reporting boundary (exclusive).

    Returns:
        Dictionary containing user summaries and validation errors.
    """

    # Create a summary for every active user,
    # including users who have no expenses.
    summaries = {}

    for user in users:
        user_id = user["user_id"]

        summaries[user_id] = {
            "user_id": user_id,
            "username": user["username"],
            "full_name": user.get("full_name"),
            "email": user["email"],
            "total_expenses": ZERO,
            "total_transactions": 0,
            "category_totals": defaultdict(lambda: ZERO),
            "daily_totals": defaultdict(lambda: ZERO),
            "highest_category": None,
            "average_transaction": ZERO
        }

    validation_errors = []
    processed_expense_ids = set()

    # Validate and process each expense.
    for expense in expenses:

        expense_id = expense.get("expense_id")
        user_id = expense.get("user_id")
        expense_date = expense.get("expense_date")
        category = expense.get("category")
        amount = expense.get("amount")

        # Check whether the expense belongs to an active user.
        if user_id not in summaries:
            validation_errors.append(
                f"Expense {expense_id}: Unknown or inactive user."
            )
            continue

        # Check duplicate expense IDs.
        if expense_id in processed_expense_ids:
            validation_errors.append(
                f"Expense {expense_id}: Duplicate expense record."
            )
            continue

        # Validate expense date.
        if not expense_date:
            validation_errors.append(
                f"Expense {expense_id}: Missing expense date."
            )
            continue

        if not (start_date <= expense_date < end_date):
            validation_errors.append(
                f"Expense {expense_id}: Date outside reporting period."
            )
            continue

        # Validate category.
        if not category or not category.strip():
            validation_errors.append(
                f"Expense {expense_id}: Invalid category."
            )
            continue

        category = category.strip()

        # Validate monetary amount.
        try:
            amount = Decimal(str(amount))

            if not amount.is_finite() or amount <= ZERO:
                raise InvalidOperation

        except (InvalidOperation, TypeError, ValueError):
            validation_errors.append(
                f"Expense {expense_id}: Invalid amount."
            )
            continue

        # Mark the expense as processed.
        processed_expense_ids.add(expense_id)

        summary = summaries[user_id]

        # Calculate total spending.
        summary["total_expenses"] += amount

        # Count transactions.
        summary["total_transactions"] += 1

        # Calculate category-wise spending.
        summary["category_totals"][category] += amount

        # Calculate daily spending.
        summary["daily_totals"][expense_date] += amount

    # Finalize user summaries.
    for summary in summaries.values():

        transaction_count = summary["total_transactions"]

        if transaction_count > 0:

            summary["average_transaction"] = (
                summary["total_expenses"]
                / Decimal(transaction_count)
            ).quantize(Decimal("0.01"))

        # Find highest spending category.
        if summary["category_totals"]:

            highest = max(
                summary["category_totals"].items(),
                key=lambda item: (item[1], item[0])
            )

            summary["highest_category"] = {
                "category": highest[0],
                "amount": highest[1]
            }

        # Convert category totals to a normal dictionary.
        summary["category_totals"] = dict(
            sorted(
                summary["category_totals"].items(),
                key=lambda item: (-item[1], item[0])
            )
        )

        # Include all seven days, even days with no spending.
        daily_totals = {}

        current_date = start_date

        while current_date < end_date:

            daily_totals[current_date] = (
                summary["daily_totals"].get(current_date, ZERO)
            )

            current_date += timedelta(days=1)

        summary["daily_totals"] = daily_totals

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_users": len(summaries),
        "total_expense_records": len(processed_expense_ids),
        "validation_error_count": len(validation_errors),
        "validation_errors": validation_errors,
        "user_summaries": list(summaries.values())
    }

