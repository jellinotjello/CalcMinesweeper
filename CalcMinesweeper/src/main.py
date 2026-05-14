########################################################################################################################
###                                            ML RL Tic-Tac-Toe                                                     ###
########################################################################################################################
from collections.abc import Sequence
from enum import Enum
import pygame
from pygame import mouse

import constants
from src.ai_player import AIPlayer
from src.game_manager import GameManager, GameState
from src.human_player import HumanPlayer

from src.utilities import load_image, draw_image, draw_polygon, draw_rect_center, draw_ellipse_centered, draw_text, \
    play_music, play_sfx, draw_button


pygame.init()
window = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
pygame.display.set_caption('Tic-Tac-Toe')

# region Global Gameplay Variables -------------------------------------------------------------------------------------

# Application modes
class Mode(Enum):
    # Two AI players train by playing against each other. No visuals are rendered to the screen.
    # This is the fastest training method and should be used when developing.
    HEADLESS_TRAINING = 0

    # Two AI players train by playing against each other. Visuals are rendered to the screen.
    # AI player will choose a move each frame. The see the training set FRAME_RATE in constants
    # file to a low number, (example FRAME_RATE = 2),
    # This training method should only be used to see the training in action (showcasing).
    TRAINING = 1

    # One human player (player 1) and one AI player (player 2). AI player will use policy defined by
    # POLICY_FILE in constants file. AI will not train.
    HUMAN_PLAY_AI = 2

    # Two Human players
    HUMAN_PLAY_HUMAN = 3

# Set the current mode here
mode = Mode.HUMAN_PLAY_HUMAN

if mode == Mode.HEADLESS_TRAINING:
    player1 = AIPlayer(True)
    player2 = AIPlayer(False)
elif mode == Mode.TRAINING:
    player1 = AIPlayer(True)
    player2 = AIPlayer(False)
elif mode == Mode.HUMAN_PLAY_AI:
    player1 = HumanPlayer(True)
    player2 = AIPlayer(False)
    player2.load_policy()
else:
    player1 = HumanPlayer(True)
    player2 = HumanPlayer(False)

game_manager = GameManager(player1, player2)
episode_count = 0
player_move_input = None

# Reset button for Human players to restart game
reset_button = None

# endregion ------------------------------------------------------------------------------------------------------------


def animate() -> None:

    global player_move_input
    global episode_count

    # Update game state via game manager
    game_manager.update(player_move_input)

    # Clear any human player inputs that were applied this frame
    player_move_input = None

    # If AI is training, automatically restart next game. After all training episodes save the learned AI policy
    if (mode == Mode.HEADLESS_TRAINING or mode == Mode.TRAINING) and game_manager.game_state == GameState.GAME_OVER:
        game_manager.reset()
        episode_count += 1
        if episode_count >= constants.EPISODES:
            if game_manager.player1.is_ai_player:
                game_manager.player1.save_policy()
            if game_manager.player2.is_ai_player:
                game_manager.player2.save_policy()


def paint() -> None:
    draw_game_board()
    draw_player_moves()

    if game_manager.game_state == GameState.PLAYING:
        if game_manager.is_player_one_turn():
            draw_player_one_turn()
        else:
            draw_player_two_turn()

    elif game_manager.game_state == GameState.GAME_OVER:
        draw_winner()
        draw_reset_button()


def draw_game_board() -> None:

    """
    Draws the empty Tic-Tac-Toe game board. (two vertical and two horizontal lines)
    """

    half_cell_size = constants.CELL_SIZE / 2
    vertical_line = (1, constants.CELL_SIZE * constants.NUM_ROWS)
    horizontal_line = (constants.CELL_SIZE * constants.NUM_COLS, 1)

    draw_rect_center(window, (constants.BOARD_CENTER_X - half_cell_size, constants.BOARD_CENTER_Y), vertical_line, constants.COLOR_WHITE)
    draw_rect_center(window, (constants.BOARD_CENTER_X + half_cell_size, constants.BOARD_CENTER_Y), vertical_line, constants.COLOR_WHITE)
    draw_rect_center(window, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y - half_cell_size), horizontal_line, constants.COLOR_WHITE)
    draw_rect_center(window, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y + half_cell_size), horizontal_line, constants.COLOR_WHITE)


def draw_player_moves() -> None:

    """
    Draw all moves from both players on the board.
    """

    # Convert board coordinates (row, col) into screen coordinates for drawing.
    # The board is centered at (BOARD_CENTER_X, BOARD_CENTER_Y).
    board_origin_x = constants.BOARD_CENTER_X - (constants.CELL_SIZE * int(constants.NUM_COLS / 2))
    board_origin_y = constants.BOARD_CENTER_Y - (constants.CELL_SIZE * int(constants.NUM_ROWS / 2))

    for row in range(constants.NUM_ROWS):
        for col in range(constants.NUM_COLS):
            row_screen = board_origin_y + row * constants.CELL_SIZE
            col_screen = board_origin_x + col * constants.CELL_SIZE

            if game_manager.board.game_board[row][col] == game_manager.player1.identifier:
                draw_text(window, "X", 50, constants.PLAYER_1_COLOR, (col_screen, row_screen))
            elif game_manager.board.game_board[row][col] == game_manager.player2.identifier:
                draw_text(window, "O", 50, constants.PLAYER_2_COLOR, (col_screen, row_screen))


def draw_player_one_turn() -> None:
    draw_text(window, "Player One", 50, constants.PLAYER_1_COLOR, (int(constants.WINDOW_WIDTH * 0.25), 100))


def draw_player_two_turn() -> None:
    draw_text(window, "Player Two", 50, constants.PLAYER_2_COLOR, (int(constants.WINDOW_WIDTH * 0.75), 100))


def draw_winner() -> None:

    if game_manager.player_one_won():
        winner_text = "Player One Wins!"
        color = constants.PLAYER_1_COLOR
    elif game_manager.player_two_won():
        winner_text = "Player Two Wins!"
        color = constants.PLAYER_2_COLOR
    else:
        winner_text = "Tie!"
        color = constants.COLOR_WHITE

    draw_text(window, winner_text, 50, color, (int(constants.WINDOW_WIDTH * 0.5), 100))

def draw_reset_button() -> None:

    global reset_button
    reset_button = draw_button(window, "Reset",(int(constants.WINDOW_WIDTH * 0.5), constants.WINDOW_HEIGHT - 100), 20, constants.COLOR_RED, constants.COLOR_GREEN)



# region User Input ----------------------------------------------------------------------------------------------------

def process_mouse_event(event: pygame.event.Event) -> None:

    """
    This method is called when a mouse event occurs.

    :param event: The Pygame mouse event to process (MOUSEBUTTONDOWN, or MOUSEMOTION)
    """

    global player_move_input
    global reset_button


    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if game_manager.game_state == GameState.GAME_OVER:
            if reset_button is not None and reset_button.collidepoint(event.pos):
                game_manager.reset()
        elif game_manager.game_state == GameState.PLAYING:
            x_pos, y_pos = mouse.get_pos()
            player_move_input = x_pos, y_pos


def process_key_event(event: pygame.event.Event) -> None:

    """
    This method is only called when a key event occurs.

    :param event: The Pygame key KEYDOWN event to process
    """
    pass


def process_keys_held(keys: Sequence[bool]) -> None:

    """
    This method is called every frame. Used to get keys that are held over sequential frames
    :param keys:
    :return:
    """
    pass


# endregion

# region Game Update Loop ----------------------------------------------------------------------------------------------

def reset() -> None:
    # pass is what we put in a function when we have not implemented it yet.
    # After you add code to this method, delete the pass line of code.
    pass

########################################################################################################################
# You should not have to edit any of the code in the game update loop below
########################################################################################################################

def play_game():
    reset()
    
    # If training in headless mode then no rendering (pygame) is needed
    if mode == Mode.HEADLESS_TRAINING:
        while episode_count < constants.EPISODES:
            # episode_count is updated in animate
            animate()
        return
        
    run = True
    frame_rate = int(constants.FRAME_RATE)
    frame_rate = frame_rate if frame_rate > 0 else 15
    while run:

        # Limit the game to FRAME_RATE frames per second (delay in milliseconds).
        pygame.time.delay(int(1000 / frame_rate))


        # Handle all events from the previous frame.
        # Quit event - exit game loop
        # Mouse events: pass to mouse event input handler
        # Key events: pass to keyboard even input handler
        pygame_events = pygame.event.get()
        for pygame_event in pygame_events:
            if pygame_event.type == pygame.QUIT:
                run = False
            else:
                if pygame_event.type == pygame.MOUSEBUTTONDOWN or pygame_event.type == pygame.MOUSEBUTTONUP or pygame_event.type == pygame.MOUSEMOTION:
                    process_mouse_event(pygame_event)

                if pygame_event.type == pygame.KEYDOWN or pygame_event.type == pygame.KEYUP:
                    process_key_event(pygame_event)

        # Keys held: pass to keys held input handler
        process_keys_held(pygame.key.get_pressed())

        # Update the game state (position, collisions, and timers)
        window.fill(constants.COLOR_BLACK)
        animate()

        # Render visuals
        paint()

        pygame.display.flip()

    pygame.quit()


# endregion

if __name__ == '__main__':
    play_game()
