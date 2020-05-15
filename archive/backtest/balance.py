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

        # print no-trade report
        if outcomes.shape[0] == 0:
            return {
                'Starting Balance': self.init_balance,
                'Resulting Balance': self.balance,
            }

        # compute report
        abs_outcomes = np.abs(outcomes[:, 0])
        pos_positions = np.where(outcomes[:, 0] > 0)[0]
        neg_positions = np.where(outcomes[:, 0] <= 0)[0]
        returns = outcomes[:, 0] / outcomes[:, 1] * 100  

        # print trade report
        return {
            'start_balance': self.init_balance,
            'resulting_balance': self.balance,
            'total_profits': np.sum(outcomes[pos_positions, 0]),
            'total_losses': np.sum(outcomes[neg_positions, 0]),
            'total_returns': (self.balance - self.init_balance) / self.init_balance * 100,
            'accuracy': pos_positions.shape[0] / (pos_positions.shape[0] + neg_positions.shape[0]) * 100,
            'weighted_accuracy': np.sum(abs_outcomes[pos_positions]) / (np.sum(abs_outcomes[pos_positions]) + 
                np.sum(abs_outcomes[neg_positions])) * 100,
            'average_return': np.mean(returns),
            'average_positive_return': 0.0 if not pos_positions.shape[0] else np.mean(returns[pos_positions]),
            'average_negative_return': 0.0 if not neg_positions.shape[0] else np.mean(returns[neg_positions]),
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
