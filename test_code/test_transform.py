
from datetime import date

from etl.extract import (
    fetch_active_users,
    fetch_weekly_expenses
)

from etl.transform import transform_expenses


start_date = date(2026, 11, 9)
end_date = date(2026, 11, 16)

# Extract data
users = fetch_active_users()

expenses = fetch_weekly_expenses(
    start_date,
    end_date
)

# Transform data
result = transform_expenses(
    users=users,
    expenses=expenses,
    start_date=start_date,
    end_date=end_date
)

print("\n========== TRANSFORMATION RESULTS ==========")

print("Total users:", result["total_users"])
print("Total expense records:", result["total_expense_records"])
print("Validation errors:", result["validation_error_count"])

for user in result["user_summaries"]:

    print("\nUser ID:", user["user_id"])
    print("Username:", user["username"])
    print("Total expenses:", user["total_expenses"])
    print("Transactions:", user["total_transactions"])
    print("Average:", user["average_transaction"])
    print("Category totals:", user["category_totals"])
    print("Daily totals:", user["daily_totals"])
    print("Highest category:", user["highest_category"])

print("\n============================================")
