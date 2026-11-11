
from pathlib import Path
from datetime import timedelta
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent / "templates"

environment = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"])
)


def generate_weekly_report(user_summary, start_date, end_date):
    template = environment.get_template("weekly_report.html")

    # ETL end_date is exclusive.
    inclusive_end_date = end_date - timedelta(days=1)

    return template.render(
        user=user_summary,
        start_date=start_date,
        end_date=inclusive_end_date
    )
