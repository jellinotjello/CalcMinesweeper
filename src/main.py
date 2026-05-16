import math
import random
from collections.abc import Sequence
from enum import Enum, Flag
import pygame
from pygame import mouse

import constants
from asrc.Square import Square
from asrc.constants import COLOR_WHITE

from asrc.game_manager import GameManager, GameState
from asrc.human_player import HumanPlayer

from asrc.utilities import load_image, draw_image, draw_polygon, draw_rect_center, draw_ellipse_centered, draw_text, \
    play_music, play_sfx, draw_button


pygame.init()

pygame.display.set_caption('Minesweeper')
Images = {
    "1" : load_image("1.png"),
    "2" : load_image("2.png"),
    "3" : load_image("3.png"),
    "4" : load_image("4.png"),
    "5" : load_image("5.png"),
    "6" : load_image("6.png"),
    "7" : load_image("7.png"),
    "8" : load_image("8.png"),
    "0" : load_image("Zero.png"),
    "Bomb" : load_image("Bomb.png"),
    "Flag" : load_image("Flag.png"),
    "Hidden" : load_image("Hidden.png"),
}

# region Global Gameplay Variables -------------------------------------------------------------------------------------\
NUM_ROWS = 00
NUM_COLS = 00
NUM_MINES = 00
CELL_SIZE = 00
scale = 00
Title = True

have_mines_been_placed = False
mines = []
squares = []
flags = []

player1 = HumanPlayer(True)
player2 = HumanPlayer(False)

game_manager = GameManager(player1, NUM_ROWS, NUM_COLS, CELL_SIZE)
player_move_input = None
first_click = True

board_origin_x = 00
board_origin_y = 00

# Reset button for Human players to restart game
reset_button = None

# endregion ------------------------------------------------------------------------------------------------------------
def startgame(cols,rows,mines):
    global NUM_ROWS
    global NUM_COLS
    global NUM_MINES
    global CELL_SIZE
    global scale
    global board_origin_x
    global board_origin_y
    global game_manager

    NUM_ROWS = rows
    NUM_COLS = cols
    NUM_MINES = mines
    CELL_SIZE = min(((constants.WINDOW_WIDTH - 80) / NUM_COLS), ((constants.WINDOW_HEIGHT - 80) / NUM_ROWS))
    scale = CELL_SIZE / 128
    board_origin_x = constants.BOARD_CENTER_X - (CELL_SIZE * (NUM_COLS / 2))
    board_origin_y = constants.BOARD_CENTER_Y - (CELL_SIZE * (NUM_ROWS / 2))
    game_manager = GameManager(player1, NUM_ROWS, NUM_COLS, CELL_SIZE)

startgame(24,24,99)

def animate() -> None:

    global player_move_input
    global episode_count

    # Update game state via game manager
    game_manager.update(player_move_input)

    # Clear any human player inputs that were applied this frame
    player_move_input = None
    # print(game_manager.board.game_board)
    # print(len(flags))
    # print(first_click)
    # print(len(mines))
    # print(len(squares))

    # If AI is training, automatically restart next game. After all training episodes save the learned AI policy

    # TODO: add highlight shi here
    game_manager.animate(mouse.get_pos(), NUM_ROWS, NUM_COLS, CELL_SIZE)

def paint() -> None:
    global have_mines_been_placed, NUM_MINES
    global Title

    if Title:
        draw_rect_center(constants.window,(constants.BOARD_CENTER_X,constants.BOARD_CENTER_Y),(600,600),constants.COLOR_RED)
        return

    draw_game_board()
    draw_squares()
    flag_counter()

    if not have_mines_been_placed:
        for mine in range(NUM_MINES):
            draw_mine_positions()
    have_mines_been_placed = True

    if game_manager.game_state == GameState.GAME_OVER:
        draw_winner()
        draw_reset_button()


def draw_game_board() -> None:

    """
    Draws the empty Tic-Tac-Toe game board. (two vertical and two horizontal lines)
    """
    # getting the mouse position
    # x, y = pyautogui.position()

    half_cell_size = CELL_SIZE / 2
    vertical_line = (1, CELL_SIZE * NUM_ROWS)
    horizontal_line = (CELL_SIZE * NUM_COLS, 1)

    for i in range(0, NUM_COLS+1):
        draw_rect_center(constants.window,
                         (constants.BOARD_CENTER_X - CELL_SIZE * (i - (NUM_COLS ) / 2),
                          constants.BOARD_CENTER_Y), vertical_line, constants.COLOR_WHITE)
    for i in range(0, NUM_ROWS+1):
        draw_rect_center(constants.window, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y - CELL_SIZE * (
                i - (NUM_ROWS) / 2)), horizontal_line, constants.COLOR_WHITE)

def random_square():
    rand_row = random.randint(0, NUM_ROWS-1)
    rand_col = random.randint(0, NUM_COLS-1)
    move = (rand_row, rand_col)
    return move

def in_safe_zone(r, c, center_r, center_c):
    return abs(r - center_r) <= 1 and abs(c - center_c) <= 1

def generate_mines(first_row, first_col, mine_count):
    global mines , board_origin_y, board_origin_x

    mines.clear()
    game_manager.board.game_board = [[0 for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]

    placed = 0
    while placed < mine_count:
        r = random.randint(0, NUM_ROWS - 1)
        c = random.randint(0, NUM_COLS - 1)

        if in_safe_zone(r, c, first_row, first_col):
            continue

        if game_manager.board.game_board[r][c] == 2:
            continue

        game_manager.board.game_board[r][c] = 2

        x = board_origin_x + (c + 0.5) * CELL_SIZE
        y = board_origin_y + (r + 0.5) * CELL_SIZE
        mines.append(Square(y, x, "Mine", Images["Bomb"]))

        placed += 1

def draw_mine_positions():
    global mines, board_origin_y, board_origin_x
    move = None
    unique = False
    while not unique:
        a1 = random_square()
        unique = True
        for mine in mines:
            actual_row = ((mine.getRow() - board_origin_y) / CELL_SIZE) - 0.5
            actual_col = ((mine.getCol() - board_origin_x) / CELL_SIZE) - 0.5
            if a1[0] == round(actual_row) and a1[1] == round(actual_col):
                unique = False
                break
        move = a1
    col_screen = board_origin_x + (move[1] + 0.5) * CELL_SIZE
    row_screen = board_origin_y + (move[0] + 0.5) * CELL_SIZE
    mine = Square(row_screen, col_screen, "Mine", Images["Bomb"])
    game_manager.board.game_board[move[0]][move[1]] = 2
    mines.append(mine)
def draw_squares():
    if game_manager.game_state == GameState.GAME_OVER:
        for mine in mines:
            mine.draw(scale)
    for square in squares:
        square.draw(scale)
    # for mine in mines:
    #     mine.draw(scale)
    for flag in flags:
        flag.draw(scale)

def is_flagged(row, col):
    global board_origin_y, board_origin_x
    for flag in flags:
        actual_row = ((flag.getRow() - board_origin_y) / CELL_SIZE) - 0.5
        actual_col = ((flag.getCol() - board_origin_x) / CELL_SIZE) - 0.5

        if row == round(actual_row) and col == round(actual_col):
            return True

    return False

def create_normal_squares(x , y) -> None:
    """
    Draw all moves from both players on the board.
    """
    global player_move_input, first_click , board_origin_y, board_origin_x

    actual_y = math.floor((y - board_origin_y) / CELL_SIZE) * CELL_SIZE + board_origin_y + 1 / 2 * CELL_SIZE
    actual_x = math.floor((x - board_origin_x) / CELL_SIZE) * CELL_SIZE + board_origin_x + 1 / 2 * CELL_SIZE
    row = math.floor((y - board_origin_y) / CELL_SIZE)
    col = math.floor((x - board_origin_x) / CELL_SIZE)
    if row > NUM_ROWS - 1 or row < 0 or col > NUM_COLS - 1 or col < 0:
        return
    if first_click:
        generate_mines(row, col, NUM_MINES)
        first_click = False

    if game_manager.board.game_board[row][col] == 2 and first_click == False:
        game_manager.game_state = GameState.GAME_OVER
        game_manager.board.winner = 1
        return

    elif game_manager.board.game_board[row][col] == 1:
        return
    game_manager.board.game_board[row][col] = 1
    mine_count = mine_counter(row, col)
    if mine_count == 0:
        for r in range(-1, 2):
            for c in range(-1, 2):
                if r == 0 and c == 0:
                    continue
                new_row = row + r
                new_col = col + c
                if 0 <= new_row < NUM_ROWS and 0 <= new_col < NUM_COLS:
                    new_x = board_origin_x + (new_col + 0.5) * CELL_SIZE
                    new_y = board_origin_y + (new_row + 0.5) * CELL_SIZE
                    if game_manager.board.game_board[new_row][new_col] == 0:
                        create_normal_squares(new_x, new_y)
    square = Square(actual_y, actual_x, "Normal", Images[f"{mine_count}"])
    squares.append(square)
    first_click = False

def mine_counter(row, col):
    mine_counter = 0
    for r in range(-1, 2):
        for c in range(-1,2):
            if 0 <= row + r < NUM_ROWS and 0 <= col + c < NUM_COLS:
                if game_manager.board.game_board[row + r][col + c] == 2:
                    mine_counter += 1
    return mine_counter

def chording(row, col):
    global board_origin_y, board_origin_x
    flag_count = 0
    for r in range(-1, 2):
        for c in range(-1, 2):
            if r == 0 and c == 0:
                continue
            if is_flagged(row + r, col + c):
                flag_count += 1
    if flag_count == mine_counter(row, col):
        for r in range(-1, 2):
            for c in range(-1, 2):
                if r == 0 and c == 0:
                    continue
                new_row = row + r
                new_col = col + c
                if 0 <= new_row < NUM_ROWS and 0 <= new_col < NUM_COLS:
                    new_x = board_origin_x + (new_col + 0.5) * CELL_SIZE
                    new_y = board_origin_y + (new_row + 0.5) * CELL_SIZE
                    if not is_flagged(new_row, new_col):
                        create_normal_squares(new_x, new_y)


def create_flag(x, y) -> None:
    global board_origin_y, board_origin_x
    unique = False
    actual_y = math.floor((y - board_origin_y) / CELL_SIZE) * CELL_SIZE + board_origin_y + 1 / 2 * CELL_SIZE
    actual_x = math.floor((x - board_origin_x) / CELL_SIZE) * CELL_SIZE + board_origin_x + 1 / 2 * CELL_SIZE
    flag_row = math.floor((y - board_origin_y) / CELL_SIZE)
    flag_col = math.floor((x - board_origin_x) / CELL_SIZE)

    while not unique:
        unique = True

        for flag in flags:
            actual_row = ((flag.getRow() - board_origin_y) / CELL_SIZE) - 0.5
            actual_col = ((flag.getCol() - board_origin_x) / CELL_SIZE) - 0.5
            if flag_row == round(actual_row) and flag_col == round(actual_col):
                flags.remove(flag)
                return
    if unique:
        flag = Square(actual_y, actual_x, "Flag", Images["Flag"])
        flags.append(flag)



def draw_winner() -> None:

    if game_manager.player_one_won():
        winner_text = "Player One Wins!"
        color = constants.PLAYER_1_COLOR
    else:
        winner_text = "You Lose!"
        color = constants.COLOR_WHITE

    draw_text(constants.window, winner_text, 50, color, (int(constants.WINDOW_WIDTH * 0.5), 100))

def flag_counter():
    draw_text(constants.window, f"Number of Flags {NUM_MINES - len(flags)}", 30, COLOR_WHITE, (int(constants.WINDOW_WIDTH * 0.5), 20))

def draw_reset_button() -> None:

    global reset_button
    reset_button = draw_button(constants.window, "Reset",(int(constants.WINDOW_WIDTH * 0.5), constants.WINDOW_HEIGHT - 100), 20, constants.COLOR_RED, constants.COLOR_GREEN)



# region User Input ----------------------------------------------------------------------------------------------------

def process_mouse_event(event: pygame.event.Event) -> None:

    """
    This method is called when a mouse event occurs.

    :param event: The Pygame mouse event to process (MOUSEBUTTONDOWN, or MOUSEMOTION)
    """

    global player_move_input
    global reset_button
    global board_origin_y
    global board_origin_x

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if game_manager.game_state == GameState.GAME_OVER:
            if reset_button is not None and reset_button.collidepoint(event.pos):
                reset()
        elif game_manager.game_state == GameState.PLAYING and Title is False:
            x_pos, y_pos = mouse.get_pos()
            row = math.floor((y_pos - board_origin_y) / CELL_SIZE)
            col = math.floor((x_pos - board_origin_x) / CELL_SIZE)
            if 0 <= row < NUM_ROWS and 0 <= col < NUM_COLS:
                if game_manager.board.game_board[row][col] == 0 or game_manager.board.game_board[row][col] == 2:
                    create_normal_squares(x_pos, y_pos)
                elif game_manager.board.game_board[row][col] == 1:
                    chording(row, col)


def process_key_event(event: pygame.event.Event) -> None:
    global Title

    """
    This method is only called when a key event occurs.

    :param event: The Pygame key KEYDOWN event to process
    """
    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        reset()
    if pygame.key.get_pressed()[pygame.K_f]:
        x_pos, y_pos = mouse.get_pos()
        create_flag(x_pos, y_pos)
    if pygame.key.get_pressed()[pygame.K_p]:
        Title = False
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        x_pos, y_pos = mouse.get_pos()
        create_normal_squares(x_pos , y_pos)



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
    global have_mines_been_placed, mines, squares, flags, first_click
    # pass is what we put in a function when we have not implemented it yet.
    # After you add code to this method, delete the pass line of code.
    have_mines_been_placed = False
    mines = []
    squares = []
    flags = []
    first_click = True
    game_manager.reset()
    #print("///////////////")

########################################################################################################################
# You should not have to edit any of the code in the game update loop below
########################################################################################################################

def play_game():
    reset()
    
    # If training in headless mode then no rendering (pygame) is needed
        
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
        constants.window.fill(constants.COLOR_BLACK)
        animate()

        # Render visuals
        paint()

        pygame.display.flip()

    pygame.quit()


# endregion

if __name__ == '__main__':
    play_game()
