from random import randint
import random 
import os
import glob
from tqdm import tqdm
import pandas as pd

from arbitrary_games import Game
from fictitious_play import Play
import subprocess


# See `fictitious_play.py` for more details on how to run a single fictitious game
# Example usage: 
if __name__ == "__main__":
    # seed = randint(1, 1000)
    # print(seed)
    # seed = 741

    number_of_experiments = 1000
    epsilon = 1e-4
    max_iterations = 10**5
    output_parquet = os.path.join("outputs", "mega.parquet")

    # Select random (unique) seeds for every experiment
    seeds = random.sample(range(10**9), number_of_experiments)

    for i in tqdm(range(number_of_experiments), desc="Fictitious Play Convergence Experiments"):

        # Load an arbitrary 2x2 zero-sum game
        game = Game(seed=seeds[i])

        fictitious_play = Play(max_iterations=max_iterations,
                            epsilon=epsilon,
                            output_file=output_parquet,
                            seed=seeds[i])

        # Run the fictitious play
        # Ignore the outputs
        _, _, _ = fictitious_play.run_fictitious_play(game, game_id=i)

    
    # Combine all parquet files
    parquet_files = glob.glob(os.path.join("outputs", "*_game_*.parquet"))
    combined_df = pd.concat([pd.read_parquet(f) for f in parquet_files])

    # Write the final combined file if needed
    combined_df.to_parquet(output_parquet, compression="snappy")

    # Clean up the temporary parquet files
    for f in parquet_files:
        os.remove(f)

    # Run `gui/app.py` to visualize the experiments
    subprocess.run(["python", "gui/app.py", "--output_file", output_parquet])
