import math
import random
from collections.abc import Sequence
from enum import Enum, Flag
import pygame
from pygame import mouse

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


import constants
from src.Square import Square

from src.game_manager import GameManager, GameState
from src.human_player import HumanPlayer

from src.utilities import load_image, load_gif_frames,draw_image, draw_polygon, draw_rect_center, draw_ellipse_centered, draw_text, \
    play_music, play_sfx, draw_button


pygame.init()

pygame.display.set_caption('Minesweeper')
Title_sequence = {
    "Title" : load_image("Title_screen.png"),
    "Open1" : load_gif_frames("Open1.gif"),
    "Open2" : load_gif_frames("Open2.gif"),
    "Set" : load_image("Set.png"),
    "0" : load_image("00.png"),
    "1" : load_image("01.png"),
    "2" : load_image("02.png"),
    "3" : load_image("03.png"),
    "4" : load_image("04.png"),
    "5" : load_image("05.png"),
    "6" : load_image("06.png"),
    "7" : load_image("07.png"),
    "8" : load_image("08.png"),
    "9" : load_image("09.png"),
}
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
NUM_ROWS = 10
NUM_COLS = 10
NUM_MINES = 20
CELL_SIZE = 00
scale = 00
Opening = True
Title = True
GameSet = False
frame_index = 0
clock = pygame.time.Clock()
FPS = 24
FRAME_DELAY = 5
tick = 0

have_mines_been_placed = False
mines = []
squares = []
flags = []

player1 = HumanPlayer(True)
player2 = HumanPlayer(False)

game_manager = GameManager(player1, NUM_ROWS, NUM_COLS, CELL_SIZE)
player_move_input = None

# Reset button for Human players to restart game
reset_button = None
play_button = None

# endregion ------------------------------------------------------------------------------------------------------------
def startgame():
    global NUM_ROWS
    global NUM_COLS
    global NUM_MINES
    global CELL_SIZE
    global scale
    global game_manager


    CELL_SIZE = min(((constants.WINDOW_WIDTH - 20) / NUM_COLS), ((constants.WINDOW_HEIGHT - 20) / NUM_ROWS))
    scale = CELL_SIZE / 128
    game_manager = GameManager(player1, NUM_ROWS, NUM_COLS, CELL_SIZE)

startgame()

def animate() -> None:

    global player_move_input
    global episode_count

    # Update game state via game manager
    game_manager.update(player_move_input)

    # Clear any human player inputs that were applied this frame
    player_move_input = None
    # print(len(flags))
    # print(len(mines))
    # print(len(squares))

    # If AI is training, automatically restart next game. After all training episodes save the learned AI policy

    # TODO: add highlight shi here
    game_manager.animate(mouse.get_pos(), NUM_ROWS, NUM_COLS, CELL_SIZE)

def paint() -> None:
    global have_mines_been_placed, NUM_MINES
    global Title

    if Title:
        draw_play_button()
        draw_title()
        return

    draw_game_board()
    draw_squares()

    if not have_mines_been_placed:
        for mine in range(NUM_MINES):
            draw_mine_positions()
    have_mines_been_placed = True

    if game_manager.game_state == GameState.GAME_OVER:
        draw_winner()
        draw_reset_button()

def draw_title() -> None:
    global Title, Opening, tick, frame_index,GameSet, NUM_ROWS,NUM_COLS,NUM_MINES
    FRAME_DELAY = 2
    if tick < 15 * FRAME_DELAY:
        frames = Title_sequence["Open1"]
        frames = [pygame.transform.scale(frame, (1000, 600)) for frame in frames]
        constants.window.blit(frames[frame_index], (0, 0))
        tick += 1
        if tick % FRAME_DELAY == 0:
            frame_index = (frame_index + 1) % len(frames)
        pygame.display.flip()
        clock.tick(FPS)
    elif 15 * FRAME_DELAY <= tick < 20 * FRAME_DELAY:
        frames = Title_sequence["Open2"]
        frames = [pygame.transform.scale(frame, (1000, 600)) for frame in frames]
        constants.window.blit(frames[frame_index], (0, 0))
        tick += 1
        if tick % FRAME_DELAY == 0:
            frame_index = (frame_index + 1) % len(frames)
        pygame.display.flip()
        clock.tick(FPS)
    elif GameSet:
        draw_image(constants.window, Title_sequence["Set"], (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y))
        mines = split_num(NUM_MINES)
        cols = split_num(NUM_COLS)
        rows = split_num(NUM_ROWS)
        draw_image(constants.window, Title_sequence[f"{cols[0]}"], (180, 115))
        draw_image(constants.window, Title_sequence[f"{cols[1]}"], (230, 115))
        draw_image(constants.window, Title_sequence[f"{cols[2]}"], (280, 115))
        draw_image(constants.window, Title_sequence[f"{rows[0]}"], (180, 225))
        draw_image(constants.window, Title_sequence[f"{rows[1]}"], (230, 225))
        draw_image(constants.window, Title_sequence[f"{rows[2]}"], (280, 225))
        draw_image(constants.window, Title_sequence[f"{mines[0]}"], (180, 335))
        draw_image(constants.window, Title_sequence[f"{mines[1]}"], (230, 335))
        draw_image(constants.window, Title_sequence[f"{mines[2]}"], (280, 335))
    else:
        Opening = False
        draw_image(constants.window,Title_sequence["Title"],(constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y))

def split_num(num):
    return [int(num/100),int(num/10)-10*int(num/100),num-10*int(num/10)-100*int(num/100)]

def draw_game_board() -> None:

    """
    Draws the empty Tic-Tac-Toe game board. (two vertical and two horizontal lines)
    """


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



def draw_mine_positions():
    global mines

    board_origin_x = constants.BOARD_CENTER_X - (CELL_SIZE * (NUM_COLS / 2))
    board_origin_y = constants.BOARD_CENTER_Y - (CELL_SIZE * (NUM_ROWS / 2))
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
    # if game_manager.game_state == GameState.GAME_OVER:
    for mine in mines:
        mine.draw(scale)
    for square in squares:
        square.draw(scale)

    for flag in flags:
        flag.draw(scale)

def show_latex(LaTeX_string: str, correct_answer=5) -> bool|None:
    # TODO: If a window is open, prevent future windows from opening by clicking more tiles
    # TODO: Remove string errors
    # TODO: Add overall database of integral equations in LaTeX string form + other problems
    # TODO: Implement SYM.doIt for solving equations automatically
    # TODO: Convert from text-answer format to answer-choice format (FRQ --> MCQ)
    # TODO: Improve Window UI...
    # TODO: Notify player if answer is correct/incorrect
    # TODO: Keep track of num correct and num incorrect for future

    result = {"correct": None}

    def submit():
        user_input = float(entry.get())
        if abs(user_input - correct_answer) < 1e-4:
            result["correct"] = True
        else:
            result["correct"] = False
        root.destroy() # can make it so that they have multiple tries ??

    root = tk.Tk()
    root.title("Solve the Integral (ANSWER IS 5 ALWAYS")

    fig = plt.figure(figsize=(4, 1), dpi=100)
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, LaTeX_string, fontsize=25, ha='center', va='center')
    ax.axis('off')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=20, pady=20)

    # Entry box for user answer
    entry = tk.Entry(root, font=("Arial", 14))
    entry.pack(pady=10)
    entry.focus()

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=5)

    root.mainloop()
    return result["correct"]

def create_normal_squares(x , y) -> None:

    """
    Draw all moves from both players on the board.
    """
    global player_move_input

    # Convert board coordinates (row, col) into screen coordinates for drawing.
    # The board is centered at (BOARD_CENTER_X, BOARD_CENTER_Y).
    board_origin_x = constants.BOARD_CENTER_X - (CELL_SIZE * (NUM_COLS / 2))
    board_origin_y = constants.BOARD_CENTER_Y - (CELL_SIZE * (NUM_ROWS / 2))
    actual_y = math.floor((y - board_origin_y) / CELL_SIZE) * CELL_SIZE + board_origin_y + 1 / 2 * CELL_SIZE
    actual_x = math.floor((x - board_origin_x) / CELL_SIZE) * CELL_SIZE + board_origin_x + 1 / 2 * CELL_SIZE
    row = math.floor((y - board_origin_y) / CELL_SIZE)
    col = math.floor((x - board_origin_x) / CELL_SIZE)
    mine_count = 0
    if row > NUM_ROWS - 1 or row < 0 or col > NUM_COLS - 1 or col < 0:
        return

    correct : bool = show_latex(r'$\int_2^7 xdx$')
    if not correct:
        return
    if game_manager.board.game_board[row][col] == 2:
        game_manager.game_state = GameState.GAME_OVER
        game_manager.board.winner = 1
        return
    elif game_manager.board.game_board[row][col] == 1:
        return
    for r in range(-1, 2):
        for c in range(-1,2):
            if 0 <= row + r < NUM_ROWS and 0 <= col + c < NUM_COLS:
                if game_manager.board.game_board[row + r][col + c] == 2:
                    mine_count += 1

    square = Square(actual_y, actual_x, "Normal", Images[f"{mine_count}"])
    game_manager.board.game_board[row][col] = 1
    squares.append(square)




def create_flag(x, y) -> None:
    board_origin_x = constants.BOARD_CENTER_X - (CELL_SIZE * (NUM_COLS / 2))
    board_origin_y = constants.BOARD_CENTER_Y - (CELL_SIZE * (NUM_ROWS / 2))
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
                unique = False
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

def draw_reset_button() -> None:
    global reset_button

    reset_button = draw_button(constants.window, "Reset",(int(constants.WINDOW_WIDTH * 0.5), constants.WINDOW_HEIGHT - 100), 20, constants.COLOR_RED, constants.COLOR_GREEN)

def draw_play_button() -> None:
    global play_button, GameSet

    if GameSet:
        play_button = draw_button(constants.window, "xxxx",(761, 200), 40, constants.COLOR_RED, constants.COLOR_GREEN,(103,63))
    else:
        play_button = draw_button(constants.window, "xxxx",(771, 255), 40, constants.COLOR_RED, constants.COLOR_GREEN,(65,30))



# region User Input ----------------------------------------------------------------------------------------------------

def process_mouse_event(event: pygame.event.Event) -> None:

    """
    This method is called when a mouse event occurs.

    :param event: The Pygame mouse event to process (MOUSEBUTTONDOWN, or MOUSEMOTION)
    """

    global player_move_input
    global reset_button, play_button
    global Title, GameSet, Opening


    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if Title:
            if GameSet:
                if play_button is not None and play_button.collidepoint(event.pos):
                    GameSet = False
                    Title = False
            elif play_button is not None and play_button.collidepoint(event.pos) and not Opening:
                GameSet = True
        elif game_manager.game_state == GameState.GAME_OVER:
            if reset_button is not None and reset_button.collidepoint(event.pos):
                reset()
        elif game_manager.game_state == GameState.PLAYING and Title is False:
            x_pos, y_pos = mouse.get_pos()
            create_normal_squares(x_pos, y_pos)


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
    global have_mines_been_placed, mines, squares, flags,NUM_ROWS,NUM_COLS,NUM_MINES,CELL_SIZE,scale,Opening,Title,Title_sequence,frame_index,clock,FPS,FRAME_DELAY,tick
    # pass is what we put in a function when we have not implemented it yet.
    # After you add code to this method, delete the pass line of code.
    have_mines_been_placed = False
    mines = []
    squares = []
    flags = []
    game_manager.reset()
    NUM_ROWS = 00
    NUM_COLS = 00
    NUM_MINES = 00
    CELL_SIZE = 00
    scale = 00
    Opening = True
    Title = True
    frame_index = 0
    clock = pygame.time.Clock()
    FPS = 24
    FRAME_DELAY = 5
    tick = 0


########################################################################################################################
# You should not have to edit any of the code in the game update loop below

# I did anyway
########################################################################################################################

def play_game():
    
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
