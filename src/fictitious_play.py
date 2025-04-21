import random
from random import randint
from collections import deque
import pandas as pd
import os

from arbitrary_games import Game

class Play:
    def __init__(self,
                 max_iterations=1000,
                 window_size=10,
                 epsilon=1e-3,
                 output_file=None,
                 seed=132):
        
        # `max_iterations + 1` ensures that we play up to and including the specified maximum
        self.max_iterations = max_iterations + 1
        self.W = window_size
        self.epsilon = epsilon
        self.output_file = output_file
        self.seed = seed

    def best_response(self,
                      game : Game,
                      player,
                      opponent_strategy):
        """ 
        Compute the player's best response to the opponents strategy. 

            The best response for player i is:
                argmax_{a_i } \\in A_i}  u_i(a_i, s_{-i})

                where A_i is the set of actions available to player i, u_i is their utility function, and s_{-i} is the opponents strategy.

        To compute player's best (pure) response, we can compute their actions expected utility and select the one with higher expected utility.
        Let a,b,c, and d denote the player's utilities so that 'a' corresponds to cell (0,0), 'b' to (0,1), 'c' to (1,0) and 'd' to (1,1) and 
        let q = opponent_strategy, then, the expected utility of player's actions are:
            
                a * q + b * (1-q)       (first action expected utility)
                c * q + d * (1-q)       (second action expected utility)

        """
        # Get the (ordered) list of utilities for player
        player_utilities = list(game.game[player].values())

        # Compute the expected utility of each player's action
        # Note that for the row player (`player_1`), the first action corresponds to indices 0 and 1.
        # However, for the column player, the first action corresponds to indices 0 and 2. 
        if player == "player_1":
            first_action_expected_utility = (player_utilities[0] * opponent_strategy) + (player_utilities[1] * (1-opponent_strategy))
            second_action_expected_utility =  (player_utilities[2] * opponent_strategy) + (player_utilities[3] * (1-opponent_strategy))
        else:
            first_action_expected_utility = (player_utilities[0] * opponent_strategy) + (player_utilities[2] * (1-opponent_strategy))
            second_action_expected_utility =  (player_utilities[1] * opponent_strategy) + (player_utilities[3] * (1-opponent_strategy))

        # If the two utilities are identical, then we can deterministically choose to play the first action, this will not affect the game in any meaningful way
        if first_action_expected_utility >= second_action_expected_utility:
            return 0
        else:
            return 1
        
    def run_fictitious_play(self, game, game_id=None):
        # Set seed
        random.seed(self.seed)

        # If an output path is specified, run so that it saves the data to that location 
        if self.output_file:
            return self.run_fictitious_play_with_output(game, game_id)

        # Let a_0 denote the action of the first player in round 0 and b_0 the second player's
        a_0, b_0 = randint(0, 1), randint(0, 1)

        # Track each player's empirical mixed strategy
        # Keep a counter of how many times each player has played their first action
        # For iteration i, their empirical mixed strategy is this number divided by i
        # if a_0 is 0, then Rowena played her first action, otherwise her second action
        rowena_strategy = 1 if a_0 == 0 else 0
        colin_strategy = 1 if b_0 == 0 else 0

        # Keep track of the players last `W` empirical mixed strategy to determine convergence
        # Initialize an empty deque and add the first actions
        rowena_deque = deque(maxlen=self.W)
        colin_deque = deque(maxlen=self.W)
        rowena_deque.append(rowena_strategy)
        colin_deque.append(colin_strategy)
        
        # For printing
        print_ten_times = self.max_iterations // 10

        # Begin the iterated fictitious play until the convergence criteria is met or until
        # the maximum number of iterations are exceeded
        for i in range(1, self.max_iterations):

            # Compute what each player's best response is to their opponents latest empirical mixed strategy
            rowena_action = self.best_response(game, "player_1", colin_strategy/i)
            colin_action = self.best_response(game, "player_2", rowena_strategy/i)

            # Update the players action counters
            rowena_strategy += rowena_action
            colin_strategy += colin_action

            # Update the last `W` empirical mixed strategies
            # Pop the leftmost element only after `self.W` many iterations
            # Because the deque does not contain a history of `self.W` many elements until then
            if i > self.W:
                _ = rowena_deque.popleft()
                _ = colin_deque.popleft()
            rowena_deque.append(rowena_strategy/(i+1))
            colin_deque.append(colin_strategy/(i+1))

            # Check if convergence criteria is met 
            # Only start checking once the deque's are filled
            # Otherwise the game trivially converges when the deques contain a single element 
            if (i > self.W) and (max(rowena_deque) - min(rowena_deque) < self.epsilon) and (max(colin_deque) - min(colin_deque) < self.epsilon):
                # Return the players action counters and on which iteration it converged
                return rowena_strategy, colin_strategy, i+1
                
            if i % print_ten_times == 0:
                print(f"\t\t\t\tRowena | Colin \t(Iteration {i})\nEmpirical Mixed Strategy: \t {rowena_strategy/i:.4f}\t  {colin_strategy/i:.4f}")

        
        # If the loop terminates without returning it must be because the maximum number
        # of iterations were exceeded
        return "did not converge", "did not converge", self.max_iterations
    
    def run_fictitious_play_with_output(self, game, game_id):
        if game_id is None:
            raise AssertionError(f"Expected a game_id but got game_id={game_id}")
        
        # Set seed
        random.seed(self.seed)

        # Store the empirical mixed strategies throughout fictitious play
        # i.e. the estimated probability of a player's first action
        rowena_list = []
        colin_list = []

        # Let a_0 denote the action of the first player in round 0 and b_0 the second player's
        a_0, b_0 = randint(0, 1), randint(0, 1)

        # Track each player's empirical mixed strategy
        # Keep a counter of how many times each player has played their first action
        # For iteration i, their empirical mixed strategy is this number divided by i
        # if a_0 is 0, then Rowena played her first action, otherwise her second action
        rowena_strategy = 1 if a_0 == 0 else 0
        colin_strategy = 1 if b_0 == 0 else 0

        # Keep track of the players last `W` empirical mixed strategy to determine convergence
        # Initialize an empty deque and add the first actions
        rowena_deque = deque(maxlen=self.W)
        colin_deque = deque(maxlen=self.W)
        rowena_deque.append(rowena_strategy)
        colin_deque.append(colin_strategy)

        # Store the first action probability
        # Each probability is estimated as the number of times they have played that action
        # divided by the number of iterations
        rowena_list.append(rowena_strategy/1)
        colin_list.append(colin_strategy/1)
        
        # For printing
        print_ten_times = self.max_iterations // 10

        # Begin the iterated fictitious play until the convergence criteria is met or until
        # the maximum number of iterations are exceeded
        for i in range(1, self.max_iterations):

            # Compute what each player's best response is to their opponents latest empirical mixed strategy
            rowena_action = self.best_response(game, "player_1", colin_strategy/i)
            colin_action = self.best_response(game, "player_2", rowena_strategy/i)

            # Update the players action counters
            rowena_strategy += rowena_action
            colin_strategy += colin_action

            # Update the last `W` empirical mixed strategies
            # Pop the leftmost element only after `self.W` many iterations
            # Because the deque does not contain a history of `self.W` many elements until then
            if i > self.W:
                _ = rowena_deque.popleft()
                _ = colin_deque.popleft()
            # Divide by the counters by i+1 because index i is initialized to 1,
            # but this loop begins at the second iteration of the fictitious play
            rowena_deque.append(rowena_strategy/(i+1))
            colin_deque.append(colin_strategy/(i+1))

            # Store their latest empirical mixed strategy
            rowena_list.append(rowena_strategy/(i+1))
            colin_list.append(colin_strategy/(i+1))

            # Check if convergence criteria is met 
            # Only start checking once the deque's are filled
            # Otherwise the game trivially converges when the deques contain a single element 
            if (i > self.W) and (max(rowena_deque) - min(rowena_deque) < self.epsilon) and (max(colin_deque) - min(colin_deque) < self.epsilon):
                # Create a list of the iterations
                iteration_list = list(range(i+1))
                
                # Check the the lengths of the lists to be saved are the same
                if (len(iteration_list) != len(rowena_list)) or (len(rowena_list) != len(colin_list)):
                    raise AssertionError(f"""Expected all lists to be of the same length but got 
                                         len(iteration_list)={len(iteration_list)}, len(rowena_list))={len(rowena_list)},
                                         len(colin_list)={len(colin_list)}.""")
                
                # Quit fictitious play and write the empirical mixed strategies to the output file
                df = pd.DataFrame({
                    'iteration': iteration_list,
                    'game_id': [game_id for _ in range(i+1)],
                    'game': [game.to_list() for _ in range(i+1)],
                    'seed': [self.seed for _ in range(i+1)],
                    'max_iteration': self.max_iterations,
                    'epsilon': self.epsilon,
                    'window_size': self.W,
                    'rowena_probabilities': rowena_list,
                    'colin_probabilities': colin_list
                })
                # Create a new parquet file for each game_id
                output_file = f"{self.output_file.split('.parquet')[0]}_game_{game_id}.parquet"
                df.to_parquet(output_file, compression="snappy")

                # Return `None` to ensure the same format as `self.run_fictitious_play` 
                return None, None, None

                     


        # If the loop terminates without returning it must be because the maximum number
        # of iterations were exceeded
        iteration_list = list(range(i+1))
        df = pd.DataFrame({
            'iteration': iteration_list,
            'game_id': [game_id for _ in range(i+1)],
            'game': [game.to_list() for _ in range(i+1)],
            'seed': [self.seed for _ in range(i+1)],
            'max_iteration': self.max_iterations,
            'epsilon': self.epsilon,
            'window_size': self.W,
            'rowena_probabilities': rowena_list,
            'colin_probabilities': colin_list
        })
        # Create a new parquet file for each game_id
        output_file = f"{self.output_file.split('.parquet')[0]}_game_{game_id}.parquet"
        df.to_parquet(output_file, compression="snappy")

        # Return `None` to ensure the same format as `self.run_fictitious_play` 
        return None, None, None


# Example usage, running one fictitious play:
if __name__ == "__main__":
    # seed = randint(1, 1000)
    # print(seed)
    seed = 104754894

    # Load an arbitrary 2x2 zero-sum game
    game = Game(seed=seed)
    # Pretty-print the game
    print(game)

    # Specify the number of maximum iterations and convergence requirement.
    # Lower values of epsilon imply a stricter convergence criteria and might require more
    # iterations. A heuristic you can use is to select a max_iterations that is at least 
    # 10 times larger than the value of epsilon. 
    epsilon = 1e-3
    max_iterations = 10**4
    fictitious_play = Play(max_iterations=max_iterations, epsilon=epsilon, seed=seed)
    # Run the fictitious play
    rowena_actions, colin_actions, iteration = fictitious_play.run_fictitious_play(game)

    # Analyze the output
    if isinstance(rowena_actions, str):
        print(rowena_actions, "after ", iteration, " iterations")
    else:
        print(f"Converged after {iteration} iterations: ({rowena_actions/iteration:.3f}, {colin_actions/iteration:.3f}), epsilon = {epsilon}")
