import pytest
import models.transaction as Transaction
from datetime import datetime

def test_create_transaction():
    transaction = Transaction.Transaction(100, "debit", "groceries", "Whole Foods", "Mastercard")
    assert transaction.id != ""
    assert isinstance(transaction.date, datetime)
    assert transaction.date != ""
    assert transaction.amount == 100
    assert transaction.type == "debit"
    assert transaction.category == "groceries"
    assert transaction.payee == "Whole Foods"
    assert transaction.issuer == "Mastercard"
    
def test_display_transaction():
    transaction = Transaction.Transaction(100, "debit", "groceries", "Whole Foods", "Mastercard")
    assert transaction.display_transaction() != ""
    assert transaction.display_transaction() == f"date: {transaction.date}\nid: {transaction.id}\namount: {transaction.amount}\ntype: {transaction.type}\ncategory: {transaction.category}\npayee: {transaction.payee}\nissuer: {transaction.issuer}"

def test_date_assigned_at_creation():
    transaction = Transaction.Transaction(100, "debit", "groceries", "Whole Foods", "Mastercard")
    assert isinstance(transaction.date, datetime)
    assert transaction.date != None
