import numpy as np
class Dice:
    def __init__(self):
        self.dice_sum = 0

    def roll_the_dice(self):
        roll_num = np.random.choice(np.arange(1, 7), 2)
        self.dice_sum = roll_num.sum()
        print(f"Dice 1: {roll_num[0]} & Dice 2: {roll_num[1]}\n")