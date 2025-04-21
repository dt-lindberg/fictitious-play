""" Game object that creates arbitrary 2X2 zero-sum games. """

from collections import OrderedDict
import random
from random import randint
import warnings

class Game:
    def __init__(self, 
                 column_labels = ["E", "O"], 
                 row_labels = ["E", "O"],
                 min_util = -100, 
                 max_util = 100, 
                 seed=132):
        
        if min_util > max_util:
            warnings.warn(f"Minimum utility {min_util} is greater than maximum utility {max_util}. Defaulting to min_util=-100, max_util=100")
            min_util, max_util = -100, 100
        
        if len(row_labels) != 2:
            warnings.warn(f"Expected the number of row labels to be 2 but got {len(row_labels)}. Defaulting to row_labels=['E', 'O']")
            row_labels = ["E", "O"]
        elif len(column_labels) != 2:
            warnings.warn(f"Expected the number of column labels to be 2 but got {len(column_labels)}. Defaulting to column_labels=['E', 'O']")
            column_labels = ["E", "O"]

        self.seed = seed
        self.cl = column_labels
        self.rl = row_labels
        self.min_util = min_util
        self.max_util = max_util
        self.game = self.create_game()

    def __repr__(self):
        # Create header row with column labels
        header = f"{'':8} | {self.cl[0]:^10} | {self.cl[1]:^8}"
        separator = "-" * len(header)
        
        # Create rows for utilities
        p1 = self.game["player_1"]
        p2 = self.game["player_2"]
        
        row1 = f"{self.rl[0]:8} | ({p1[f'{self.rl[0]}{self.cl[0]}']:3}, {p2[f'{self.rl[0]}{self.cl[0]}']:3}) | ({p1[f'{self.rl[0]}{self.cl[1]}']:3}, {p2[f'{self.rl[0]}{self.cl[1]}']:3})"
        row2 = f"{self.rl[1]:8} | ({p1[f'{self.rl[1]}{self.cl[0]}']:3}, {p2[f'{self.rl[1]}{self.cl[0]}']:3}) | ({p1[f'{self.rl[1]}{self.cl[1]}']:3}, {p2[f'{self.rl[1]}{self.cl[1]}']:3})"
        
        return f"\n{header}\n{separator}\n{row1}\n{row2}\n"
    
    def to_list(self):
        # Returns the game as a list
        p1 = self.game["player_1"]
        p2 = self.game["player_2"]
        
        return [
            [p1[f'{self.rl[0]}{self.cl[0]}'], p2[f'{self.rl[0]}{self.cl[0]}']], 
            [p1[f'{self.rl[0]}{self.cl[1]}'], p2[f'{self.rl[0]}{self.cl[1]}']],
            [p1[f'{self.rl[1]}{self.cl[0]}'], p2[f'{self.rl[1]}{self.cl[0]}']], 
            [p1[f'{self.rl[1]}{self.cl[1]}'], p2[f'{self.rl[1]}{self.cl[1]}']]
        ]

    def create_game(self):
        # Set seed
        random.seed(self.seed)

        # Generate random utilities
        a, b, c, d = randint(self.min_util, self.max_util), randint(self.min_util, self.max_util), randint(self.min_util, self.max_util), randint(self.min_util, self.max_util)
        
        game = OrderedDict()
        game["player_1"] = OrderedDict([
            (f"{self.rl[0]}{self.cl[0]}", a),
            (f"{self.rl[0]}{self.cl[1]}", b),
            (f"{self.rl[1]}{self.cl[0]}", c),
            (f"{self.rl[1]}{self.cl[1]}", d)
        ])

        game["player_2"] = OrderedDict([
            (f"{self.rl[0]}{self.cl[0]}", -a),
            (f"{self.rl[0]}{self.cl[1]}", -b),
            (f"{self.rl[1]}{self.cl[0]}", -c),
            (f"{self.rl[1]}{self.cl[1]}", -d)
        ])

        return game

# Example usage
if __name__ == "__main__":
    game = Game()
    print(game)
    print(game.game)
    print(game.to_list())
