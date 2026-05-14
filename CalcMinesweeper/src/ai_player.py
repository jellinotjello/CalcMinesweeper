import pickle
import sys

from player_base import Player
import numpy as np
import constants
import datetime

"""
ai_player.py

AIPlayer chooses moves automatically.
This class does not apply moved directly to the board. The move is returned and applied in the GameManager class.

Training mode (inference == False):
- Exploration: sometimes choose a random valid move.
- Exploitation: choose the move that leads to the highest learned state value.

Inference mode (inference == True):
- Always exploit (choose the best known move from the learned policy).

The policy is stored as a Python dictionary.
Keys are different board positions (a snapshot of where the X’s and O’s are).
Values are “how good” that position is. This is an estimate of the reward the AI expects in the future if it reaches that position.
When choosing a move, the AI simulates each possible move, looks up the value of the resulting board position, and picks the move with the highest value.
"""

class AIPlayer(Player):
    def __init__(self, is_player_one):
        super().__init__(is_player_one)
        self.is_ai_player = True

        self.states = []
        self.state_values = {}

        # AI is training or playing using a learned policy
        # If training then self.inference is false
        # (this is set automatically when a policy file is loaded)
        self.inference = False

        self.current_exploration_rate = constants.EXPLORATION_RATE

        self.training_diagnostics = {
            "episodes" : 0,
            "wins" : 0,
            "losses" : 0,
            "ties" : 0,
            "exp_rate" : 0.0,
        }


    def choose_move(self, board, move_input) -> tuple[None, None] | None:

        """
        Choose a move for the current board.

        Note: choose_move overrides the base class method. The move_input argument is ignored.

        If training (inference == False):
        - Exploration: sometimes pick a random valid move.
        - Exploitation: pick the move that leads to the highest learned state value.

        If inference (inference == True):
        - Always exploit (pick the best known move).
        """

        available_moves = board.get_possible_moves()
        if len(available_moves) == 0:
            return None

        # If training choose a random move if
        if not self.inference and ((np.random.uniform() <= self.current_exploration_rate) or len(self.state_values) == 0):
            move_index = np.random.choice(len(available_moves))
            return available_moves[move_index]
        else:

            # Get all possible moves left on the game board. Simulate making each possible move on a copy of the game board
            # For each simulation keep track of which moved results in the highest value. The highest value is more likly to
            # lead to a win. See fee_reward for how different moves and board states values are set.
            max_value = float('-inf')
            best_move = []
            for move in available_moves:
                board_copy = board.game_board.copy()
                board_copy[move[0]][move[1]] = self.identifier

                # Convert the board into a tuple so it is immutable.
                # The board state can now be used as a key for the state_values dictionary.
                state_key = tuple(board_copy.flatten())
                value = self.state_values.get(state_key, 0)

                if value > max_value:
                    max_value = value
                    best_move = [move]
                elif value == max_value:
                    best_move.append(move)

            best_move_index = np.random.choice(len(best_move))
            return best_move[best_move_index]


    def add_state(self, board) ->None:

        """Record the current board state (as a tuple key) for learning later."""

        board_copy = board.game_board.copy()
        state_key = tuple(board_copy.flatten())
        self.states.append(state_key)

    def feed_reward(self, reward):

        """
        Update values for all moves made this game (training episode) states using the final reward.
        Each move will be updated according to the reward.

        Called once at the end of a game.
        """

        for state in reversed(self.states):
            if self.state_values.get(state) is None:
                self.state_values[state] = 0

            self.state_values[state] += constants.LEARNING_RATE * (constants.DECAY_GAMMA * reward - self.state_values[state])
            reward = self.state_values[state]


    def reset(self) -> None:

        """
        Clear all states for a new game.
        Note: self.state_values should not be reset between each training episode

        If training:
            - decay exploration rate
            - after each training diagnostics interval print the training diagnostics.
        """

        self.states = []

        if not self.inference:
            self.decay_exploration_rate()
            self.training_diagnostics["exp_rate"] = self.current_exploration_rate

            self.training_diagnostics["episodes"] += 1
            if  self.training_diagnostics["episodes"] % constants.TRAINING_DIAGNOSTICS_INTERVAL == 0:
                self.print_training_diagnostics()


    def decay_exploration_rate(self):

        """
        Multiply exploration rate by EXPLORATION_DECAY_RATE, clamped to a minimum.
        """

        self.current_exploration_rate = max(constants.MIN_EXPLORATION_RATE, self.current_exploration_rate * constants.EXPLORATION_DECAY_RATE)


    def update_game_over_training_diagnostics(self, last_episode_result) -> None:

        """
        Update the diagnostics dictionary. (wins, ties, losses)
        """

        if last_episode_result in self.training_diagnostics:
            self.training_diagnostics[last_episode_result] += 1


    def print_training_diagnostics(self) -> None:

        """
        Print the training diagnostics to the console
        """

        print("---------------------------------------------")
        player = "player1" if self.is_player_one else "player2"
        print(f"Training Diagnostics: ({player})")
        print(f"Training Episodes complete: {self.training_diagnostics["episodes"]} of {constants.EPISODES}")
        print(f"Wins: {self.training_diagnostics["wins"]}, Losses: {self.training_diagnostics["losses"]}, Ties: {self.training_diagnostics["ties"]}")
        print(f"Total explored states: {len(self.state_values)}, Estimate Memory used: {self.estimate_policy_size():.2f} MB")
        print(f"Exp Rate: {self.training_diagnostics["exp_rate"]}")


    def estimate_policy_size(self) -> float:

        """
        Calculate the estimated policy size in memory.
        Return the estimated policy size in Megabytes.
        """

        # Size of dictionary container
        total_bytes = sys.getsizeof(self.state_values)

        # Size of each key and value inside state_values dictionary
        for key, value in self.state_values.items():
            total_bytes += sys.getsizeof(key)
            total_bytes += sys.getsizeof(value)

        total_megabytes = total_bytes / 1024 / 1024
        return total_megabytes


    def save_policy(self):

        """
        After training is complete save the learned policy to the disk.
        Policies are saved to the policies' folder.
        """

        policy_data_path = constants.POLICY_DIR
        policy_data_path.mkdir(parents=True, exist_ok=True)
        current_time = datetime.datetime.now()
        player = "player1" if self.is_player_one else "player2"
        policy_file_name = f"policy_{player}_{current_time.strftime('%Y%m%d-%H%M')}.pkl"
        policy_file = policy_data_path / policy_file_name
        with open(policy_file, 'wb') as file:
            pickle.dump(self.state_values, file)
        return policy_file


    def load_policy(self) -> None:

        """
        Load the AI policy specified in constants file (POLICY_FILE)
        If policy file is loaded AI will only exploit (choose best known move)
        """

        policy_data_path = constants.POLICY_DIR
        policy_file = policy_data_path / constants.POLICY_FILE
        if policy_file.exists() and policy_file.is_file():
            with open(policy_file, 'rb') as file:
                self.state_values = pickle.load(file)
                self.inference = True

