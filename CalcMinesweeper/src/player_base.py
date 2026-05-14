
"""
player_base.py

Base class for AI and human players.
"""

class Player:
    def __init__(self, is_player_one: bool):

        self.is_player_one = is_player_one

        # These identifiers are used by Board to store moves in a numpy grid.
        self.identifier = None
        if is_player_one:
            self.identifier = 1
        else:
            self.identifier = -1

        # Intended to be set by derived classes (HumanPlayer / AIPlayer)
        self.is_ai_player = None


    def choose_move(self, board, move_input):

        """
        Choose a move to apply to the board.
        This method must be implemented by subclasses.
        """

        raise NotImplementedError("Derived classes must implement choose_move().")




