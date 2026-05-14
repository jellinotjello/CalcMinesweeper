

import numpy as np

from src import constants

"""
Board is the rules and state for a turn-based game.

- State: the grid of cell values (0 = empty, non-zero = a player's identifier)
- Rules: what moves are legal, how moves are applied, and how to detect win/tie

When changing this class to create new game you must:
- Define how a move is applied and verify the move is legal
- Update the game state after each move is applied
- Define how a winner, and or tie is determined

Note: All rendering should be done elsewhere. This class just contains the rules and state of the game

"""

class Board:
    def __init__(self):
        self.rows = constants.NUM_ROWS
        self.cols = constants.NUM_COLS

        self.game_board = np.zeros((self.rows, self.cols))
        self.last_player = None

        # last move as a tuple (row, col) on game_board
        self.last_move = None
        self.winner = None


    def apply_move(self, move: tuple[int, int], player) -> bool:

        """
        Try to place a player's move on the board at (row, col) specified by move.
        Returns True if move was successfully applied to the board, otherwise False.
        """

        if self.is_move_valid(move):
            self.game_board[move[0], move[1]] = player.identifier
            self.last_move = move
            self.last_player = player
            return True

        return False


    def reset(self):

        """
        Clear the game board and reset winner, last_move, and last_player for new game
        """

        self.game_board = np.zeros((self.rows, self.cols))
        self.winner = None
        self.last_move = None
        self.last_player = None

    def is_move_valid(self, move: tuple[int, int]) -> bool:

        """
        Return True if the move (row, col) specified by move is valid. A move is valid if
        (row, col) is a valid index on the game board and (row, col) does not already have a move
        """

        if move is None:
            return False

        row, col = move
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False

        # An open spot on the game board is marked with 0
        return self.game_board[row][col] == 0


    def check_winner(self) -> None:

        """
        Check whether the most recent move ended the game (win or tie).
        - Sets self.winner to the winning Player if the last move created a win.
        - Sets self.winner to "Tie" if the board is full and there is no winner.
        - Leaves self.winner as None if the game should continue. (No winner, or tie)
        """

        if self.last_move is None:
            return


        win_directions = [
            (1, 0),  # vertical win (same column different rows)
            (0, 1),  # horizontal win (same row different columns)
            (1, 1),  # diagonal win (top left to bottom right)
            (1, -1),  # diagonal win (top right to bottom left)
        ]

        # For each direction, count how many of the last player's pieces are connected in a straight line through the last move.
        # Example for (1, 0) = vertical:
        #   - Start at the last move.
        #   - Walk down (1, 0) while the same identifier continues.
        #   - Walk up (-1, 0) while the same identifier continues.
        # If the total connected count reaches the required length, we found a winner.

        for row_dir, col_dir in win_directions:
            same_identifier_count = 1

            current_row = self.last_move[0] + row_dir
            current_col = self.last_move[1] + col_dir

            while 0 <= current_row < self.rows and 0 <= current_col < self.cols:
                if self.game_board[current_row][current_col] == self.last_player.identifier:
                    same_identifier_count += 1
                    current_row = current_row + row_dir
                    current_col = current_col + col_dir
                else:
                    break

            current_row = self.last_move[0] - row_dir
            current_col = self.last_move[1] - col_dir

            while 0 <= current_row < self.rows and 0 <= current_col < self.cols:
                if self.game_board[current_row][current_col] == self.last_player.identifier:
                    same_identifier_count += 1
                    current_row = current_row - row_dir
                    current_col = current_col - col_dir
                else:
                    break

            if same_identifier_count == self.rows:
                self.winner = self.last_player
                return

        # If no winner, then check for tie
        if len(self.get_possible_moves()) == 0:
            self.winner = "Tie"
            return


    def get_possible_moves(self) -> list[tuple[int, int]]:

        """
        Returns a list of all empty (row, col) cells
        """

        possible_moves = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.game_board[row][col] == 0:
                    possible_moves.append((row, col))
        return possible_moves




