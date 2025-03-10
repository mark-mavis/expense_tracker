import pytest
from models.recurring_transaction import RecurringTransaction
from datetime import datetime

def test_create_recurring_transaction():
    recurring_transaction = RecurringTransaction(100, "debit", "groceries", "Whole Foods", "Mastercard", "2023-01-01", "2023-12-31", "monthly", "2023-02-01")
    assert recurring_transaction.id != ""
    assert isinstance(recurring_transaction.date, datetime)
    assert recurring_transaction.date != ""
    assert recurring_transaction.amount == 100
    assert recurring_transaction.type == "debit"
    assert recurring_transaction.category == "groceries"
    assert recurring_transaction.payee == "Whole Foods"
    assert recurring_transaction.issuer == "Mastercard"
    assert recurring_transaction.start_date == "2023-01-01"
    assert recurring_transaction.end_date == "2023-12-31"
    assert recurring_transaction.recurrence_period == "monthly"
    assert recurring_transaction.next_due_date == "2023-02-01"
    assert recurring_transaction.is_active