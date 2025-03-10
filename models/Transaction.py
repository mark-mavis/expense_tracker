from datetime import date, datetime, timezone
import os

class Transaction:
    counter_file = "data/transaction_counter.txt"
    
    def __init__(self, amount: str, type: str, category: str, payee: str, issuer: str):
        self.id = self.generate_transaction_id()
        self.date = datetime.now()
        self.amount = amount
        self.type = type
        self.category = category
        self.payee = payee
        self.issuer = issuer
       
    def display_transaction(self) -> str:
        return f"date: {self.date}\nid: {self.id}\namount: {self.amount}\ntype: {self.type}\ncategory: {self.category}\npayee: {self.payee}\nissuer: {self.issuer}"

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
   
       
transaction: Transaction = Transaction(100, "debit", "groceries", "Whole Foods", "Mastercard")
print(transaction.display_transaction())
