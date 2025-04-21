import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.arbitrary_games import Game


# Change `file_path` to point to the desired parquet file
file_path = os.path.join("HW3", "outputs", "mega.parquet")
pd_df = pd.read_parquet(file_path)
# pd_df.shape (n_rows, 8)
# Available columns are:
# 'iteration', 'game_id', 'seed', 'max_iteration', 'epsilon', 
# 'window_size', 'rowena_probabilities', 'colin_probabilities'
pd_23 = pd_df[pd_df["game_id"] == 787 ]
print(pd_23)

seed = int(pd_23["seed"].unique())

game = Game(seed=seed)
print(game)