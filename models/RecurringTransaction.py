import models.Transaction as Transaction

class RecurringTransaction(Transaction):
    def __init__(self, ammount: str, type: str, category: str, payee: str, issuer: str, start_date: date, end_date: date, recurrence_period: str, next_due_date: date, is_active: bool = True):
        super().__init__(ammount, type, category, payee, issuer)
        self.start_date = start_date
        self.end_date = end_date
        self.recurrence_period = recurrence_period
        self.next_due_date = next_due_date
       
    def is_active(self) -> bool:
        return self.is_active
    def calculate_next_due_date(self) -> date:
        pass
    def generate_next_transaction(self) -> Transaction:
        pass
    