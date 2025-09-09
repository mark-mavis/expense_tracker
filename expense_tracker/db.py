from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            PRAGMA foreign_keys = ON;
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                currency TEXT NOT NULL,
                category TEXT,
                recurrence TEXT NOT NULL,
                start_date TEXT,
                next_due_date TEXT,
                notes TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                expense_id INTEGER NOT NULL,
                amount_cents INTEGER NOT NULL,
                paid_date TEXT NOT NULL,
                method TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(expense_id) REFERENCES expenses(id) ON DELETE CASCADE
            );
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_expenses_next_due ON expenses(next_due_date);
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_payments_expense ON payments(expense_id);
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_payments_paid_date ON payments(paid_date);
            """
        )
        conn.commit()


def add_expense(
    db_path: str,
    *,
    name: str,
    amount_cents: int,
    currency: str = "USD",
    category: Optional[str] = None,
    recurrence: str = "none",
    start_date: Optional[str] = None,  # YYYY-MM-DD
    next_due_date: Optional[str] = None,  # YYYY-MM-DD
    notes: Optional[str] = None,
    active: bool = True,
) -> int:
    now = _utc_now_iso()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO expenses (
                name, amount_cents, currency, category, recurrence,
                start_date, next_due_date, notes, active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                amount_cents,
                currency,
                category,
                recurrence,
                start_date,
                next_due_date,
                notes,
                1 if active else 0,
                now,
                now,
            ),
        )
        expense_id = cur.lastrowid
        conn.commit()
        return int(expense_id)


def update_expense_next_due_and_active(
    db_path: str, expense_id: int, *, next_due_date: Optional[str], active: Optional[bool] = None
) -> None:
    now = _utc_now_iso()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        if active is None:
            cur.execute(
                "UPDATE expenses SET next_due_date = ?, updated_at = ? WHERE id = ?",
                (next_due_date, now, expense_id),
            )
        else:
            cur.execute(
                "UPDATE expenses SET next_due_date = ?, active = ?, updated_at = ? WHERE id = ?",
                (next_due_date, 1 if active else 0, now, expense_id),
            )
        conn.commit()


def set_expense_active(db_path: str, expense_id: int, active: bool) -> None:
    now = _utc_now_iso()
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE expenses SET active = ?, updated_at = ? WHERE id = ?",
            (1 if active else 0, now, expense_id),
        )
        conn.commit()


def get_expense_by_id(db_path: str, expense_id: int):
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        return cur.fetchone()


def get_expense_by_name(db_path: str, name: str):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM expenses WHERE lower(name) = lower(?) ORDER BY id LIMIT 1",
            (name,),
        )
        return cur.fetchone()


def list_expenses(db_path: str, *, include_inactive: bool = False):
    sql = "SELECT * FROM expenses"
    if not include_inactive:
        sql += " WHERE active = 1"
    sql += " ORDER BY COALESCE(next_due_date, '9999-12-31'), name"
    with get_connection(db_path) as conn:
        return list(conn.execute(sql))


def record_payment(
    db_path: str,
    *,
    expense_id: int,
    amount_cents: int,
    paid_date: str,  # YYYY-MM-DD
    method: Optional[str] = None,
    notes: Optional[str] = None,
) -> int:
    now = _utc_now_iso()
    with get_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO payments (expense_id, amount_cents, paid_date, method, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (expense_id, amount_cents, paid_date, method, notes, now),
        )
        payment_id = cur.lastrowid
        conn.commit()
        return int(payment_id)


def list_payments(
    db_path: str,
    *,
    expense_id: Optional[int] = None,
    year_month: Optional[str] = None,  # YYYY-MM
):
    clauses: list[str] = []
    params: list[object] = []
    if expense_id is not None:
        clauses.append("expense_id = ?")
        params.append(expense_id)
    if year_month is not None:
        clauses.append("substr(paid_date, 1, 7) = ?")
        params.append(year_month)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM payments{where} ORDER BY paid_date DESC, id DESC"
    with get_connection(db_path) as conn:
        return list(conn.execute(sql, params))


def upcoming_expenses(db_path: str, *, until_date: str):
    """Return active expenses with a next_due_date on or before until_date (YYYY-MM-DD)."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            SELECT * FROM expenses
            WHERE active = 1 AND next_due_date IS NOT NULL AND next_due_date <= ?
            ORDER BY next_due_date, name
            """,
            (until_date,),
        )
        return list(cur)


def monthly_payment_summary(db_path: str, *, year: int, month: int) -> dict[str, int]:
    ym = f"{year:04d}-{month:02d}"
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT COALESCE(SUM(amount_cents), 0) AS total_cents, COUNT(*) AS cnt FROM payments WHERE substr(paid_date,1,7) = ?",
            (ym,),
        )
        row = cur.fetchone()
        return {"total_cents": int(row[0] or 0), "count": int(row[1] or 0)}
