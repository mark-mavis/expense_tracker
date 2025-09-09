from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Optional

from . import __version__
from . import db as dbm
from .recurrence import (
    compute_next_due_date,
    normalize_recurrence,
    parse_date,
    parse_yyyy_mm,
)


DEFAULT_DB = "expenses.db"


def _amount_to_cents(amount_text: str) -> int:
    d = Decimal(amount_text).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)


def _cents_to_amount(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(int(cents))
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def _print_rows(rows, *, fields: list[str]) -> None:
    if not rows:
        print("(none)")
        return
    widths = {f: max(len(f), max(len(str(r[f])) if r[f] is not None else 0 for r in rows)) for f in fields}
    header = "  ".join(f.ljust(widths[f]) for f in fields)
    print(header)
    print("  ".join("-" * widths[f] for f in fields))
    for r in rows:
        print("  ".join((str(r[f]) if r[f] is not None else "").ljust(widths[f]) for f in fields))


def _resolve_db_path(arg: Optional[str]) -> str:
    return str(Path(arg or DEFAULT_DB))


def cmd_init(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    dbm.init_db(db_path)
    print(f"Initialized database at {db_path}")


def cmd_add(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    dbm.init_db(db_path)

    recurrence = normalize_recurrence(args.recurrence)
    amount_cents = _amount_to_cents(args.amount)

    start = parse_date(args.start) if args.start else None
    next_due = parse_date(args.next) if args.next else None
    if next_due is None:
        if recurrence == "none":
            next_due = start
        else:
            basis = start or date.today()
            next_due = basis

    expense_id = dbm.add_expense(
        db_path,
        name=args.name,
        amount_cents=amount_cents,
        currency=args.currency,
        category=args.category,
        recurrence=recurrence,
        start_date=start.isoformat() if start else None,
        next_due_date=next_due.isoformat() if next_due else None,
        notes=args.notes,
        active=True,
    )
    print(f"Added expense #{expense_id}: {args.name} {args.currency} {_cents_to_amount(amount_cents)} ({recurrence})")


def cmd_list(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    rows = dbm.list_expenses(db_path, include_inactive=args.all or args.inactive)
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "amount": f"{r['currency']} {_cents_to_amount(r['amount_cents'])}",
            "recurrence": r["recurrence"],
            "next_due": r["next_due_date"] or "",
            "active": "yes" if r["active"] else "no",
            "category": r["category"] or "",
        })
    _print_rows(out, fields=["id", "name", "amount", "recurrence", "next_due", "active", "category"])


def cmd_upcoming(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    cutoff = date.today() + timedelta(days=args.days)
    rows = dbm.upcoming_expenses(db_path, until_date=cutoff.isoformat())
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "due": r["next_due_date"],
            "amount": f"{r['currency']} {_cents_to_amount(r['amount_cents'])}",
            "recurrence": r["recurrence"],
            "category": r["category"] or "",
        })
    _print_rows(out, fields=["id", "name", "due", "amount", "recurrence", "category"])


def _find_expense(db_path: str, identifier: str):
    if identifier.isdigit():
        row = dbm.get_expense_by_id(db_path, int(identifier))
        return dict(row) if row else None
    row = dbm.get_expense_by_name(db_path, identifier)
    return dict(row) if row else None


def cmd_pay(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    row = _find_expense(db_path, args.expense)
    if not row:
        print(f"Expense not found: {args.expense}")
        return

    amount_cents = _amount_to_cents(args.amount) if args.amount else int(row["amount_cents"])
    paid_date = parse_date(args.date).isoformat() if args.date else date.today().isoformat()

    payment_id = dbm.record_payment(
        db_path,
        expense_id=int(row["id"]),
        amount_cents=amount_cents,
        paid_date=paid_date,
        method=args.method,
        notes=args.notes,
    )

    recurrence = row["recurrence"]
    start = parse_date(row["start_date"]) if row["start_date"] else None
    current_due = parse_date(row["next_due_date"]) if row["next_due_date"] else None
    if recurrence == "none":
        dbm.update_expense_next_due_and_active(db_path, int(row["id"]), next_due_date=None, active=False)
        print(f"Recorded payment #{payment_id}. Deactivated one-off expense '{row['name']}'.")
    else:
        next_due = compute_next_due_date(current_due, start, recurrence, from_date=parse_date(paid_date))
        dbm.update_expense_next_due_and_active(db_path, int(row["id"]), next_due_date=next_due.isoformat(), active=True)
        print(f"Recorded payment #{payment_id}. Next due on {next_due.isoformat()}.")


def cmd_month(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    if args.month:
        year, month = parse_yyyy_mm(args.month)
    else:
        today = date.today()
        year, month = today.year, today.month
    summary = dbm.monthly_payment_summary(db_path, year=year, month=month)
    total = _cents_to_amount(summary["total_cents"])
    print(f"Payments in {year:04d}-{month:02d}: {total} across {summary['count']} payments")


def cmd_payments(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    expense_id: Optional[int] = int(args.id) if args.id else None
    if args.name and not expense_id:
        row = dbm.get_expense_by_name(db_path, args.name)
        if row:
            expense_id = int(row["id"])
    rows = dbm.list_payments(db_path, expense_id=expense_id, year_month=args.month)
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "expense_id": r["expense_id"],
            "paid_date": r["paid_date"],
            "amount": _cents_to_amount(r["amount_cents"]),
            "method": r["method"] or "",
        })
    _print_rows(out, fields=["id", "expense_id", "paid_date", "amount", "method"])


def cmd_export(args: argparse.Namespace) -> None:
    db_path = _resolve_db_path(args.db)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    table = args.table

    def write_csv(file: Path, rows, fields: list[str]) -> None:
        with file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for r in rows:
                writer.writerow([r[f] for f in fields])

    if table in ("expenses", "all"):
        rows = dbm.list_expenses(db_path, include_inactive=True)
        fields = [
            "id",
            "name",
            "amount_cents",
            "currency",
            "category",
            "recurrence",
            "start_date",
            "next_due_date",
            "notes",
            "active",
            "created_at",
            "updated_at",
        ]
        write_csv(output if table == "expenses" else output.with_name(output.stem + "_expenses.csv"), rows, fields)

    if table in ("payments", "all"):
        rows = dbm.list_payments(db_path)
        fields = ["id", "expense_id", "amount_cents", "paid_date", "method", "notes", "created_at"]
        write_csv(output if table == "payments" else output.with_name(output.stem + "_payments.csv"), rows, fields)

    print(f"Exported {table} to {output if table != 'all' else output.with_name(output.stem + '_{expenses,payments}.csv')}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="expense-tracker", description="Expense tracker CLI")
    p.add_argument("--db", help="Path to SQLite database file (default: expenses.db)")

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="Initialize the database")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("add", help="Add a new expense/subscription/bill")
    sp.add_argument("name", help="Name of the expense")
    sp.add_argument("amount", help="Amount, e.g. 12.34")
    sp.add_argument("--currency", default="USD", help="Currency code (default USD)")
    sp.add_argument("--category", help="Category label")
    sp.add_argument("--recurrence", default="monthly", help="Recurrence: none, daily, weekly, biweekly, monthly, quarterly, yearly")
    sp.add_argument("--start", help="Start date YYYY-MM-DD")
    sp.add_argument("--next", help="Next due date YYYY-MM-DD (override)")
    sp.add_argument("--notes", help="Notes")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("list", help="List expenses")
    sp.add_argument("--all", action="store_true", help="Include inactive expenses")
    sp.add_argument("--inactive", action="store_true", help="Only inactive expenses")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("upcoming", help="Show upcoming due expenses")
    sp.add_argument("--days", type=int, default=30, help="Days ahead to include (default 30)")
    sp.set_defaults(func=cmd_upcoming)

    sp = sub.add_parser("pay", help="Record a payment for an expense")
    sp.add_argument("expense", help="Expense id or name")
    sp.add_argument("--amount", help="Amount paid (defaults to expense amount)")
    sp.add_argument("--date", help="Payment date YYYY-MM-DD (default today)")
    sp.add_argument("--method", help="Payment method (note)")
    sp.add_argument("--notes", help="Notes")
    sp.set_defaults(func=cmd_pay)

    sp = sub.add_parser("month", help="Show payment summary for a month")
    sp.add_argument("--month", help="YYYY-MM (default current month)")
    sp.set_defaults(func=cmd_month)

    sp = sub.add_parser("payments", help="List payments")
    sp.add_argument("--month", help="YYYY-MM to filter")
    sp.add_argument("--id", help="Filter by expense id")
    sp.add_argument("--name", help="Filter by expense name")
    sp.set_defaults(func=cmd_payments)

    sp = sub.add_parser("export", help="Export to CSV")
    sp.add_argument("output", help="Output CSV path (basename if table=all)")
    sp.add_argument("--table", choices=["expenses", "payments", "all"], default="all")
    sp.set_defaults(func=cmd_export)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0
