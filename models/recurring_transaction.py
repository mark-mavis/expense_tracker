from models.transaction import Transaction
from datetime import date

class RecurringTransaction(Transaction):
    def __init__(self, 
                 ammount: float, 
                 type: str, 
                 category: str, 
                 payee: str, 
                 issuer: str, 
                 start_date: date, 
                 end_date: date, 
                 recurrence_period: str, 
                 next_due_date: date, 
                 active: bool = True):
        super().__init__(ammount, type, category, payee, issuer)
        self.start_date = start_date
        self.end_date = end_date
        self.recurrence_period = recurrence_period
        self.next_due_date = next_due_date
        self.active = active
       
    def is_active(self) -> bool:
        return self.active
    def calculate_next_due_date(self) -> date:
        pass
    def generate_transaction(self) -> Transaction:
        return Transaction(self.amount, self.type, self.category, self.payee, self.issuer)
    