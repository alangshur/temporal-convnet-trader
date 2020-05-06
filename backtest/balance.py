class BalanceManager:
    def __init__(self, init_balance):
        self.balance = init_balance

    def get_balance(self):
        return self.balance

    def update(self, change):
        self.balance += change
