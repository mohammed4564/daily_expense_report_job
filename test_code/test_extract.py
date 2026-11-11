
from datetime import date

from etl.extract import (
    fetch_weekly_expenses,
    get_previous_week_range
)

# Simulate the next Monday's reporting run.
start_date, end_date = get_previous_week_range(
    reference_date=date(2026, 11, 16)
)

print("Start date:", start_date)
print("End date (exclusive):", end_date)

expenses = fetch_weekly_expenses(
    start_date,
    end_date
)

print("Total expenses:", len(expenses))

for expense in expenses:
    print(
        expense["user_id"],
        expense["category"],
        expense["amount"],
        expense["expense_date"]
    )
