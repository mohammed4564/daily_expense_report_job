# Daily Expense Tracker – Weekly ETL & Email Reporting

## Project Overview

The **Daily Expense Tracker** is a Python-based ETL and reporting project that automatically processes users' weekly expenses, generates personalized expense reports, stores summary data in PostgreSQL, and sends reports through email.

The ETL pipeline is automated using **GitHub Actions**, so reports can be generated and delivered every Monday without manual execution.

## Key Features

- Extract weekly expense records from PostgreSQL.
- Process expenses for each active user.
- Validate expense records before loading.
- Calculate total expenses and transaction counts.
- Calculate average transaction amounts.
- Identify the highest spending category.
- Generate category-wise and daily expense summaries.
- Store weekly summaries in PostgreSQL.
- Generate personalized HTML and PDF reports.
- Send weekly reports through Gmail SMTP.
- Automate weekly execution using GitHub Actions.
- Use database UPSERT operations to avoid duplicate weekly summary records.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | ETL development |
| PostgreSQL | Database |
| SQL | Data extraction and loading |
| Pandas | Data processing, if used |
| Jinja2 | HTML report generation |
| ReportLab | PDF report generation |
| SMTP | Email delivery |
| Git & GitHub | Version control |
| GitHub Actions | Workflow automation |

## Project Architecture

```text
PostgreSQL Database
        |
        v
     EXTRACT
        |
        v
    TRANSFORM
        |
        v
       LOAD
        |
        v
Weekly Expense Reports Table
        |
        v
   REPORT GENERATION
        |
        +----------------+
        |                |
        v                v
    HTML Report      PDF Report
        |                |
        +--------+-------+
                 |
                 v
            EMAIL SERVICE
                 |
                 v
          User Gmail Inbox

       GitHub Actions
       Runs the ETL weekly
```

## Project Structure

```text
daily_expense_report_job/
│
├── database/
│   ├── __init__.py
│   └── database.py
│
├── etl/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── run_etl.py
│
├── reports/
│   ├── __init__.py
│   ├── report_generator.py
│   ├── pdf_generator.py
│   └── templates/
│       └── weekly_report.html
│
├── services/
│   ├── __init__.py
│   └── email_service.py
│
├── .github/
│   └── workflows/
│       └── weekly-etl.yml
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Database Design

### 1. Users Table

Stores user information.

Important columns:
- `user_id`
- `username`
- `email`
- `full_name`
- `is_active`

### 2. Expenses Table

Stores individual expense transactions.

Important columns:
- `expense_id`
- `user_id`
- `expense_date`
- `category`
- `description`
- `amount`

### 3. Weekly Expense Reports Table

Stores aggregated weekly expense summaries.

Important columns:
- `report_id`
- `user_id`
- `week_start`
- `week_end`
- `total_expenses`
- `total_transactions`
- `average_transaction`
- `highest_category`
- `category_totals`
- `daily_totals`
- `processed_at`

## ETL Process

### 1. Extract

- Fetch all active users.
- Fetch expense records for the previous week.
- Use a date range from Monday to Sunday.

### 2. Transform

- Validate expense records.
- Exclude invalid and duplicate records.
- Calculate total expenses per user.
- Calculate transaction counts and averages.
- Calculate category-wise expense totals.
- Calculate daily expense totals.
- Identify the highest spending category.

### 3. Load

- Insert weekly summaries into PostgreSQL.
- Update existing records using UPSERT.
- Maintain one summary record per user per reporting week.

### 4. Report Generation

- Generate personalized HTML reports using Jinja2.
- Generate PDF reports using ReportLab.
- Prepare the reports for email delivery.

### 5. Email Delivery

- Send individual weekly expense reports.
- Attach the generated PDF report.
- Use Gmail SMTP for email delivery.

## Installation and Setup

### Prerequisites

- Python 3.11 or later
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/mohammed4564/daily_expense_report_job.git

cd daily_expense_report_job
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv daily_exp_venv

daily_exp_venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=your_postgresql_connection_url

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SENDER_NAME=Expense Tracker
```

**Security:** Never commit `.env` or actual credentials to GitHub. Use GitHub repository secrets for automated execution.

### 5. Run the ETL Pipeline

```bash
python -m etl.run_etl
```

## GitHub Actions Automation

The project uses GitHub Actions to execute the ETL pipeline automatically.

Workflow file:

```text
.github/workflows/weekly-etl.yml
```

### Schedule

```yaml
on:
  schedule:
    - cron: "0 3 * * 1"
  workflow_dispatch:
```

**Execution schedule:**

- Frequency: Every Monday
- Time: 03:00 UTC
- Indian Standard Time: 08:30 AM
- Reporting period: Previous Monday to Sunday

The `workflow_dispatch` option allows manual execution from the GitHub Actions interface.

### Required GitHub Secrets

Configure these under:

**GitHub Repository → Settings → Secrets and variables → Actions**

| Secret | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection URL |
| `SMTP_HOST` | Gmail SMTP host |
| `SMTP_PORT` | SMTP port |
| `SMTP_EMAIL` | Sender email address |
| `SMTP_PASSWORD` | Gmail App Password |
| `SENDER_NAME` | Email sender name |

## Idempotency

The weekly report loading process uses PostgreSQL UPSERT with a unique constraint on:

```sql
(user_id, week_start, week_end)
```

This prevents duplicate weekly summary records when the same reporting period is processed again.

Note: Re-running the pipeline can still send another email for the same reporting period.

## Future Enhancements

- Expense analytics dashboard.
- Monthly and yearly expense reports.
- Budget tracking and alerts.
- Spending trend analysis.
- Email delivery tracking.
- Automated email deduplication.
- Data quality monitoring and logging.

## Author

**Mohammed Umar**

GitHub: https://github.com/mohammed4564

---

*Built with Python, PostgreSQL, ETL concepts, and GitHub Actions.*