
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_weekly_pdf(user_summary, start_date, end_date, pdf_path):

    # end_date is exclusive, so display Sunday instead.
    inclusive_end_date = end_date - __import__("datetime").timedelta(days=1)

    document = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()
    content = []

    # Report heading
    content.append(
        Paragraph("Weekly Expense Report", styles["Title"])
    )

    content.append(Spacer(1, 10))

    name = user_summary.get("full_name") or user_summary["username"]

    content.append(
        Paragraph(f"Hello {name},", styles["Normal"])
    )

    content.append(
        Paragraph(
            f"Reporting period: {start_date} to {inclusive_end_date}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 15))

    # Expense summary
    content.append(
        Paragraph("Expense Summary", styles["Heading2"])
    )

    summary_data = [
        ["Description", "Value"],
        ["Total Expenses", str(user_summary["total_expenses"])],
        ["Total Transactions", str(user_summary["total_transactions"])],
        ["Average Transaction", str(user_summary["average_transaction"])]
    ]

    highest = user_summary.get("highest_category")

    if highest:
        summary_data.append([
            "Highest Spending Category",
            f'{highest["category"]} - {highest["amount"]}'
        ])
    else:
        summary_data.append([
            "Highest Spending Category",
            "No expenses"
        ])

    summary_table = Table(summary_data, colWidths=[85 * mm, 75 * mm])

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    content.append(summary_table)
    content.append(Spacer(1, 15))

    # Category-wise expenses
    content.append(
        Paragraph("Category-wise Expenses", styles["Heading2"])
    )

    category_data = [["Category", "Amount"]]

    for category, amount in user_summary["category_totals"].items():
        category_data.append([str(category), str(amount)])

    if len(category_data) == 1:
        category_data.append(["No expenses this week", "0.00"])

    category_table = Table(
        category_data,
        colWidths=[85 * mm, 75 * mm]
    )

    category_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    content.append(category_table)
    content.append(Spacer(1, 15))

    # Daily expenses
    content.append(
        Paragraph("Daily Expenses", styles["Heading2"])
    )

    daily_data = [["Date", "Amount"]]

    for expense_date, amount in user_summary["daily_totals"].items():
        daily_data.append([str(expense_date), str(amount)])

    daily_table = Table(
        daily_data,
        colWidths=[85 * mm, 75 * mm]
    )

    daily_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    content.append(daily_table)
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Thank you for using Daily Expense Tracker!",
            styles["Normal"]
        )
    )

    document.build(content)

    return str(pdf_path)
