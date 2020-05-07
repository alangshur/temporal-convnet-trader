import numpy as np



class BalanceManager:
    def __init__(self, init_balance):
        self.init_balance = init_balance
        self.balance = init_balance

        # init position
        self.position_value = 0
        self.position_cost = 0

        # init position stats
        self.position_outcomes = []

    def get_balance(self):
        return self.balance

    def get_report(self):
        outcomes = np.array(self.position_outcomes)
        pos_positions = np.where(outcomes[:, 0] > 0)[0]
        neg_positions = np.where(outcomes[:, 0] <= 0)[0]
        returns = outcomes[:, 0] / outcomes[:, 1] * 100
        
        return {
            'Starting Balance': str(round(self.init_balance, 3)) + ' USD',
            'Resulting Balance': str(round(self.balance, 3)) + ' USD',
            'Total Return': str(round((self.balance - self.init_balance) / self.init_balance * 100, 3)) + '%',
            'Accuracy': str(round(pos_positions.shape[0] / (pos_positions.shape[0] + neg_positions.shape[0]) * 100, 3)) + '%',
            'Average Return': str(round(np.mean(returns), 3)) + '%',
            'Average Positive Return': str(round(np.mean(returns[pos_positions]), 3)) + '%',
            'Average Negative Return': str(round(np.mean(returns[neg_positions]), 3)) + '%'
        }

    def update(self, change, position_closed=False):

        # update position
        self.position_value += change
        if self.position_value < self.position_cost:
            self.position_cost = self.position_value

        # update position stats
        if position_closed:
            self.position_outcomes.append((self.position_value, -self.position_cost))
            self.position_value = 0
            self.position_cost = 0
        
        self.balance += change
