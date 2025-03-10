import models.transaction as Transaction
import datetime as dt

class TransactionManager:
    def __init__(self):
        self.transactions = []
        self.recurring_transactions = []
        
    def add_transaction(self):
        pass
    
    def add_recurring_transaction(self):
        pass
    
    def delete_transaction(self):
        pass
    
    def process_recurring_transactions(self):
        for transaction in self.recurring_transactions:
            if transaction.is_active() and transaction.calculate_next_due_date() <= dt.datetime.now():
                next_transaction = transaction.generate_next_transaction()
                self.add_transaction(next_transaction)
    
    def get_transactions_by_category(self):
        pass
    
    def generate_report(self):
        pass