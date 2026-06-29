"""
Automated ID generation for statements and cases.

Statement IDs follow the pattern STM-YYYY-000001 and increment
sequentially per year, satisfying the "statement numbering automation"
requirement.
"""

from datetime import date

from models import Statement


def generate_statement_id():
    year = date.today().year
    prefix = f"STM-{year}-"

    latest = (
        Statement.query.filter(Statement.statement_id.like(f"{prefix}%"))
        .order_by(Statement.id.desc())
        .first()
    )

    if latest:
        last_seq = int(latest.statement_id.split("-")[-1])
        next_seq = last_seq + 1
    else:
        next_seq = 1

    return f"{prefix}{next_seq:06d}"
