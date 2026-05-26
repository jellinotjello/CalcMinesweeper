
from src import constants
from src.player_base import Player

"""
human_player.py

HumanPlayer converts mouse input (x, y pixel coordinates) into a board move (row, col).

This class does NOT apply the move to the board. It only returns the move.
The GameManager is responsible for validating and applying the move.
"""


class HumanPlayer(Player):
    def __init__(self, is_player_one):
        super().__init__(is_player_one)
        self.is_ai_player = False


    def is_mouse_on_tile(self, position, NUM_ROWS, NUM_COLS, CELL_SIZE):
        board_origin_x = constants.BOARD_CENTER_X - (CELL_SIZE * int(NUM_COLS / 2))
        board_origin_y = constants.BOARD_CENTER_Y - (CELL_SIZE * int(NUM_ROWS / 2))
        Offset = [0, 0]
        if NUM_COLS != NUM_ROWS:
            Offset = [0.5, 0.5]
        bounds = int(CELL_SIZE / 2), int(CELL_SIZE / 2)
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                row_screen = board_origin_y + (row + Offset[0]) * CELL_SIZE
                col_screen = board_origin_x + (col + Offset[1]) * CELL_SIZE
                if self.move_within_bounds(position, (col_screen, row_screen), bounds):
                    return row, col

        return None


    def choose_move(self, board, move_input,NUM_ROWS,NUM_COLS,CELL_SIZE) -> tuple[int, int]|None:

        """
        Convert move_input (mouse click in pixels) into a board move (row, col).

        Notes:
        - choose_move overrides the base class method.
        - This method uses layout values in constants to map pixels to board (row, col).
        - This method does not apply moved directly to the board.
        - This method does not check if the mapped (row, col) is valid.

        Returns None if the click is outside the board.
        """

        if move_input is None:
            return None

        board_origin_x = constants.BOARD_CENTER_X - (CELL_SIZE * int(NUM_COLS / 2))
        board_origin_y = constants.BOARD_CENTER_Y - (CELL_SIZE * int(NUM_ROWS / 2))
        Offset = [0.5,0.5]
        if NUM_COLS > NUM_ROWS:
            Offset = [0,.5]
        elif NUM_ROWS > NUM_COLS:
            Offset = [.5,0]
        bounds = int(CELL_SIZE / 2), int(CELL_SIZE / 2)
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                row_screen = board_origin_y + (row + Offset[0]) * CELL_SIZE
                col_screen = board_origin_x + (col + Offset[1]) * CELL_SIZE
                if self.move_within_bounds(move_input, (col_screen, row_screen), bounds):
                    print(row, col)
                    return row, col

        return None


    def move_within_bounds(self, move_input, cell_render_center, bounds):

        """
        Return True if the mouse click (x, y) is inside the rectangular bounds of a cell.
        """

        x, y = move_input
        render_x, render_y = cell_render_center
        bounds_x, bounds_y = bounds

        top = render_y - bounds_y
        bottom = render_y + bounds_y
        left = render_x - bounds_x
        right = render_x + bounds_x

        return top < y < bottom and left < x < right
