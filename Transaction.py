from datetime import date, datetime, timezone
import os

class Transaction:
    counter_file = "transaction_counter.txt"
    
    def __init__(self, amount: str, type: str, category: str, payee: str, issuer: str):
        self.id = self.generate_transaction_id()
        self.date = datetime.now(timezone.utc)
        self.amount = amount
        self.type = type
        self.category = category
        self.payee = payee
        self.issuer = issuer
       
    def display_transaction(self) -> str:
        return f"{self.date} {self.id} {self.amount} {self.type} {self.category} {self.payee} {self.issuer}"

    @classmethod
    def generate_transaction_id(cls):
        # Read the last transaction number from the file
        if os.path.exists(cls.counter_file):
            with open(cls.counter_file, "r") as file:
                counter = int(file.read().strip())
        else:
            counter = 0  # Start from 0 if no file exists

        # Increment the counter
        counter += 1

        # Save the new counter back to the file
        with open(cls.counter_file, "w") as file:
            file.write(str(counter))

        # Generate a transaction ID with timestamp + counter
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TXN-{timestamp}-{counter:06d}"
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
       
       
transaction: Transaction = Transaction(100, "debit", "groceries", "Whole Foods", "Mastercard")
print(transaction.display_transaction())
