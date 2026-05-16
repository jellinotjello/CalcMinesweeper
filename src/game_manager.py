from src.board import Board
from enum import Enum


"""
game_manager.py

GameManager runs the turn-based game loop logic (NOT the pygame loop).

Responsibilities:
- Owns the Board and the two Player objects
- Tracks whose turn it is
- Asks the current player to choose a move
- Applies the move to the board (using board.apply_move)
- Checks for a winner/tie after each valid move
- Switches turns when the game continues
- During AI training: records AI states and feeds rewards when the game ends

Important:
- GameManager contains no rendering or pygame code.
- Player objects only CHOOSE moves. GameManager applies moves and advances the game.
"""



class GameState(Enum):
    PLAYING = 0     # game is active, moves are still being applied
    GAME_OVER = 1   # a player has won the game, or game ended in a tie
    RESET = 2       # waiting to reset (waiting to start a new game)


class GameManager:

    def __init__(self, player1,rows,cols,cell_size):
        self.NUM_ROWS = rows
        self.NUM_COLS = cols
        self.CELL_SIZE = cell_size
        self.board = Board(self.NUM_ROWS,self.NUM_COLS,self.CELL_SIZE)

        # players can either be Human or AI players
        self.player1 = player1

        self.current_player = self.player1
        self.game_state = GameState.PLAYING


    def animate(self, position : tuple, NUM_ROWS : int, NUM_COLS : int, CELL_SIZE : int) -> None:
        tile_pos = self.current_player.is_mouse_on_tile(position, NUM_ROWS, NUM_COLS, CELL_SIZE)
        if not tile_pos:
            return

        self.board.highlight_tile(tile_pos, CELL_SIZE, NUM_ROWS, NUM_COLS)


    def update(self, pending_move):

        """
        Advance the game by at most ONE move.

        pending_move: Human player only - (x, y) mouse click pixels

        Each move follows the following rules:
        1. Ask the current player to choose a move
        2. Apply the chosen move to the board
        3. If move was valid:
            - If current player is AI player record the move state
            - Check for game over (winner or tie)
            - If game over:
                - AI players feed reward
                - restart game
            - If not game over then set current player to other player

        """


        if self.game_state != GameState.PLAYING:
            return

        chosen_move = self.current_player.choose_move(self.board, pending_move,self.NUM_ROWS,self.NUM_COLS,self.CELL_SIZE)


        self.board.winner = self.board.check_winner(chosen_move)
        if self.board.winner is not None:
            self.game_state = GameState.GAME_OVER

        if self.board.apply_move(chosen_move, self.current_player):

            if self.current_player.is_ai_player:
                self.current_player.add_state(self.board)




    def is_player_one_turn(self):
        return self.current_player == self.player1



    def player_one_won(self):
        return self.board.winner != 1



    def reset(self):

        """
        Reset the game back to a fresh starting state.

        - Clears the board
        - Clears AI episode memory (states visited this game)
        - Sets the turn back to player1
        - Returns the game to PLAYING
        """

        self.board.reset()
        if self.player1.is_ai_player:
            self.player1.reset()

        self.game_state = GameState.PLAYING
        self.current_player = self.player1













