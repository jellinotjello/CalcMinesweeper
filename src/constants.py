

from pathlib import Path
import pygame

# File paths (where AI policies are stored)
BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE_DIR / 'policies'

# File name of policy used when in Human play AI mode
POLICY_FILE = "policy_player2_20260217-1127.pkl"

# ----------------------------------------------------------------------------------------------------------------------

# AI Training Constants

# How strong to update a states value when learning new information
#   Higher value (ex > 0.5)  - learns faster but can become unstable
#   Lower values (ex < 0.05) - learns more smoothly but will take longer to train
# Choose a value between 0.01 and 0.3 for state based Reinforcement Learning
#
# When you are making your new game in your team you will want to experiment with different values
LEARNING_RATE = 0.2

# Discount factor: how much the AI should care about future rewards compared to immediate rewards
# Closer to 0: Care more about immediate rewards.
# Closer to 1: Care more about future (long term rewards)
# For tic-tac-toe this means care more about making the best more each turn (closer to 0), or care more about winning (closer to 1)
# If too small the AI will not learn multistep strategies that take more than one turn to develop.
DECAY_GAMMA = 0.9

# The starting value for our exploration vs exploitation. For exploration the AI will choose a random valid move.
# For exploitation the AI will choose the move has a better change in eventually winning.
EXPLORATION_RATE = 1.0

# How much the exploration rate decreases each episode (games played). The new exploration rate is calculated by
# new_exploration = EXPLORATION_RATE * EXPLORATION_DECAY_RATE
# When training we should start by exploring a lot. Then over the duration of time explore less and less
EXPLORATION_DECAY_RATE = 0.99987

# The minimum probability the AI will choose to explore
MIN_EXPLORATION_RATE = 0.05

# Total number of training episodes. Each episode is one game complete game.
EPISODES = 25000

# How often to print training diagnostics to the console
TRAINING_DIAGNOSTICS_INTERVAL = 100

# ----------------------------------------------------------------------------------------------------------------------

# Graphics Constants
FRAME_RATE = 60
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_ORANGE = (255, 94, 14)

PLAYER_1_COLOR = COLOR_YELLOW
PLAYER_2_COLOR = COLOR_RED

# Game Board
BOARD_CENTER_X = int(WINDOW_WIDTH / 2)
BOARD_CENTER_Y = int(WINDOW_HEIGHT / 2)

# Calculus Stuff
INTEGRALS = [
    r'\int_2^7 x \, dx',
    r'\int_1^4 (3x^2 + 2) \, dx',
    r'\int_0^3 (5 - x) \, dx',
    r'\int_1^2 (x^3 - 2x) \, dx',
    r'\int_2^5 (2x + 1) \, dx',
    r'\int_0^1 (4x^2) \, dx',
    r'\int_3^6 (x^2 + 1) \, dx',
    r'\int_1^3 (x^4 - 3x^2 + 2) \, dx',
    r'\int_5^{10} x \, dx',
    r'\int_3^{8} (4x^2 + 3) \, dx',
    r'\int_1^{6} (10 - 2x) \, dx',
    r'\int_2^{5} (2x^3 - 3x) \, dx',
    r'\int_4^{9} (3x + 2) \, dx',
    r'\int_1^{4} (5x^2) \, dx',
    r'\int_2^{7} (2x^2 + 1) \, dx'
]