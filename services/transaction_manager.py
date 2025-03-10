from models.transaction import Transaction
from models.recurring_transaction import RecurringTransaction
import schedule

from datetime import datetime

class TransactionManager:
    def __init__(self):
        self.transactions = []
        self.recurring_transactions = []
        self.load_transactions()
        
    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        self.save_transactions()
    
    def add_recurring_transaction(self, transaction: RecurringTransaction):
        self.recurring_transactions.append(transaction)
        self.save_transactions()
    
    def delete_transaction(self, transaction_id: str):
        self.transactions =[t for t in self.transactions if t.id != transaction_id]
        self.save_transactions()
        
    def get_transactions_by_category(self, category: str):
        return [t for t in self.transactions if t.category.lower() == category.lower()]
    
    def process_recurring_transactions(self):
        for transaction in self.recurring_transactions:
            if transaction.is_active() and transaction.calculate_next_due_date() <= datetime.now():
                next_transaction = transaction.generate_transaction()
                self.add_transaction(next_transaction)
    
    def load_transactions(self):
        pass
    
    def generate_report(self):
        pass
    
    def save_transactions(self):
        """Saves transactions to a JSON file."""
        data = {
            "transactions": [vars(t) for t in self.transactions],
            "recurring_transactions": [vars(t) for t in self.recurring_transactions]
        }