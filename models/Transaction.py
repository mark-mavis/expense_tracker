from datetime import datetime

class Transaction:
    counter_file = "data/transaction_counter.txt"
    
    def __init__(self, amount: float, type: str, category: str, payee: str, issuer: str):
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
        from pathlib import Path

        counter_file = Path(cls.counter_file)

        # Read and update counter in a single block
        counter = 0
        if counter_file.exists():
            with counter_file.open("r+") as file:
                counter = int(file.read().strip())
                counter += 1
                file.seek(0)
                file.write(str(counter))
        else:
            with counter_file.open("w") as file:
                counter = 1
                file.write(str(counter))

        # Generate a unique transaction ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TXN-{timestamp}-{counter:06d}"
