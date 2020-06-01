import random
import turtle
import argparse
from copy import deepcopy
from time import sleep


WIDTH, HEIGHT = 480, 480
SIDE_LEN = WIDTH - 20
BOLD_BORDER_SIZE = 3
NORMAL_BORDER_SIZE = 1
BOARD_SIZE = 9

TOP_LEFT = (-SIDE_LEN - 4)/ 2 - BOLD_BORDER_SIZE/2, (SIDE_LEN + 12)/ 2 - BOLD_BORDER_SIZE/ 2
pen = turtle.Turtle(visible=False)
turtle.tracer(False)
#each cell in the board has its own turtle to make erasing text easier
writers = [[turtle.Turtle(visible=False) 
            for _ in range(BOARD_SIZE)] 
            for _ in range(BOARD_SIZE)
            ]

def draw_board():
    """
    Displays an empty 9 x 9 sudoku board divided in groups of 3 x 3 cells.
    """
    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.title("Sudoku Solver - Visualization Tool")
    pen.speed(0)
    cell_size = SIDE_LEN / BOARD_SIZE
    for row in range(BOARD_SIZE + 1):
        pen.penup()
        pen.goto(TOP_LEFT[0], TOP_LEFT[1] - row * cell_size)
        if row % 3 == 0:
            pen.pensize(BOLD_BORDER_SIZE)
        else:
            pen.pensize(NORMAL_BORDER_SIZE)
        pen.pendown()
        pen.forward(SIDE_LEN)

    pen.right(90)
    for col in range(BOARD_SIZE + 1):
        pen.penup()
        pen.goto(TOP_LEFT[0] + col * cell_size, TOP_LEFT[1])
        if col % 3 == 0:
            pen.pensize(BOLD_BORDER_SIZE)
        else:
            pen.pensize(NORMAL_BORDER_SIZE)
        pen.pendown()
        pen.forward(SIDE_LEN)
    
    pen.penup()


def draw_text(text, row, col, *,font_size=20, color=None):
    """ 
    Draws text in the corresponding sudoku grid cell, and returns the turtle
    instance asociated with the text.
    Assuming draw_board() has already been called.
    
    Args:
        board_size (int): the size of the sudoku board.
        text: the text to be written on the cell.
        row (int): row index starting at 0.
        col (int): col index starting at 0.
        font_size (int): optional, defaults to 20.
    """
    writer = writers[row][col]
    if color:
        writer.pencolor(color)

    cell_size = SIDE_LEN / BOARD_SIZE
    x = (TOP_LEFT[0] + col * cell_size) + cell_size / 2
    y = (TOP_LEFT[1] - row * cell_size) - cell_size / 2 - font_size 
    writer.up()
    writer.goto(x, y)
    writer.write(text, font=('Arial',font_size,'normal'), align="center")


def isvalid_sudoku(board):
    """
    Verifies that the board complies with the following conditions:

    -Each row must contain the digits 1-9 without repetition.
    -Each column must contain the digits 1-9 without repetition.
    -Each of the 9 3x3 sub-boxes of the grid must contain the digits 1-9 
    without repetition
    
    Args:
        board (List[List[int]]): 9 x 9 sudoku grid with 0s or
        None at empty locations.
    """
    if not board or len(board) != 9 or not all(len(row) == 9 for row in board):
        return False

    #This can be simplified to use only one set, but it would hurt readability
    row = set()
    blocks = set()
    col = set()
    for i, r in enumerate(board):
        for j, num in enumerate(r):
            if (num, j) in col or (i, num) in row \
                or (num, i//3, j//3) in blocks:
                return False
            if num:
                col.add((num, j))
                row.add((i, num))
                blocks.add((num, i//3, j//3))
    
    return True


def generate_sudoku():
    """
    returns a valid empty sudoku board that contains at least 17 clues. 
    """
    MIN_CLUES = 17 # reference: https://arxiv.org/abs/1201.0749
    board = _fill_board()
    locations = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(locations)
    while len(locations) > MIN_CLUES:
        row, col = locations.pop()
        tmp = board[row][col]
        # remove a number and check to see if it creates a unique solution
        board[row][col] = None
        solutions = []
        count_solutions(deepcopy(board), solutions)
        if len(solutions) > 1:
            #removing this number creates multiple solutions so we put it back
            board[row][col] = tmp

    update_screen(board)

    return board


def count_solutions(board, solutions, start_row=0, max_solutions=1):
    """
    Finds multiple solutions if possible. Given an empty 9 x 9 it is possible to
    generate all sudoku board solutions.

    Args:
        solutions (list): empty list passed by reference (see example)
        max_solutions (int): the solver would try to keep finding solutions
        until len(solutions) > this parameter
    
    Example:
        Generate the first 501 solutions and store them in "a"

    >>> a = []
    >>> board = [[None] * 9 for _ in range(9)]
    >>> count_solutions(board, a, max_solutions=500)
    >>> print(a[300])
    """
    if len(solutions) > max_solutions:
        return
    for i in range(start_row, BOARD_SIZE):
        for j, cell in enumerate(board[i]):
            if cell is None:
                for guess in range(1, BOARD_SIZE + 1):
                    if _isvalid_guess(board, i, j, guess):
                        board[i][j] = guess
                        count_solutions(board, solutions, i, max_solutions)
                        board[i][j] = None
                return
    solutions.append(deepcopy(board))


def update_screen(board):
    """
    Draws the contents of board into the screen. The current text is
    cleared before writting the new text.
    """
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell:
                writers[i][j].clear()
                draw_text(cell, i, j)


def _fill_board(board=None):
    """
    Returns a randomly solved 9 x 9 sudoku grid
    """
    if board is None:
        board = [[None] * 9 for i in range(9)]

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if not cell:
                random_guess = random.sample(range(1, 10), 9)
                for guess in random_guess:
                    if _isvalid_guess(board, i, j, guess):
                        board[i][j] = guess
                        if _fill_board(board) is not None:
                            return board
                        board[i][j] = None
                return None
    return board


def solve(board, draw_speed=0):
    """
    Solves a 9 x 9 sudoku in-place returns True if the board contains at least
    one valid solution. The solver stops immediately after finding 1 solution.
    
    Args:
        board (List[List[int]]): 9 x 9 sudoku grid with 0s or
        None at empty locations.
    
    Raises:
        TypeError if board doesn't obey sudoku rules.
    """
    if not isvalid_sudoku(board):
        raise TypeError("Invalid sudoku board")
    
    sleep_time = 0
    if draw_speed == 1:
        sleep_time = 0.1
    elif draw_speed == 2:
        sleep_time = 0.3
    elif draw_speed == 3:
        sleep_time = 0.7

    return _solve(board, timeout=sleep_time)


def _solve(board, start_row=0, display=True, timeout=0):
    """
    Args:
        start_row (int): starting row for the current function call.

        display (boolean): draws solution into the board if true

        find_multiple (boolean): find multiple solutions and return False if the
        board doesn't have an unique solution.
    """
    for i in range(start_row, BOARD_SIZE):
        for j, cell in enumerate(board[i]):
            if cell is None:
                sol_count = 0
                for guess in range(1, BOARD_SIZE + 1):
                    if _isvalid_guess(board, i, j, guess):
                        board[i][j] = guess
                        if display:
                            draw_text(guess, i, j, color="red")
                            sleep(timeout)
                        solution = _solve(board, i, display, timeout)
                        if solution:
                            return True
                        else:
                            board[i][j] = None
                            if display:
                                writers[i][j].clear()
                #None of the guesses worked 
                return False

    return True


def _isvalid_guess(board, row, col, guess):
    """
    Checks if guess is not repeated in neither of the given row, col or block.
    """
    #position of current block
    blk_row = 3 * (row // 3)
    blk_col = 3 * (col // 3)

    for i in range(BOARD_SIZE):
        if guess == board[i][col]: return False
        if guess == board[row][i]: return False
        if guess == board[blk_row + i // 3][blk_col + i % 3]:
            return False
    
    return True


def _get_cell_position(x, y):
    """
    Returns the corresponding row and column index for a cell located at (x, y)
    coordinates.
    """
    #translating x, y coordinates from center to top left of the screen
    x -= TOP_LEFT[0]
    y -= TOP_LEFT[1]

    cell_size = WIDTH // BOARD_SIZE
    
    i = abs(y // cell_size) - 1 #FIXME row number is always off by 1
    j = x // cell_size

    return (int(i), int(j))


def _set_cell_value(x, y):
    global custom_board
    screen = pen.getscreen()
    row, col = _get_cell_position(x, y)
    cell_val = screen.numinput("Sudoku Solver", "specify value for this cell "\
                              "or press cancel to delete:", minval=1, maxval=9)
    
    if not cell_val:
        custom_board[row][col] = None
        writers[row][col].clear()
    else:
        cell_val = int(cell_val)
        if not _isvalid_guess(custom_board, row, col, cell_val):
            print(cell_val, "is already present in the same column, row, or box.")
            return
        
        if custom_board[row][col] is not None:
            #clear the old text before drawing the new one
            writers[row][col].clear()
        custom_board[row][col] = cell_val
        draw_text(cell_val, row, col)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-r", "--random", action="store_true", 
                    help="solve a randomly generated 9 x 9 sudoku grid.")
    group.add_argument("-e", "--empty", action="store_true", 
                    help="generate an unsolved sudoku grid.")
    parser.add_argument("-s", "--speed", type=int, choices={0, 1, 2, 3}, 
                    help="controls the speed at which the sudoku is solved."
                         " choices: 0: fast, 1: slow, 2: slower, 3: slowest.")
    
    args = parser.parse_args()
    draw_board()
    draw_speed = 0 if args.speed is None else args.speed
    if args.random:
        board = generate_sudoku()
        sleep(3)
        solve(board, draw_speed)

    elif args.empty:
        generate_sudoku()
    
    else: #no arguments or only speed was specified, solve a custom sudoku board
        custom_board = [[None] * 9 for i in range(9)]
        screen = pen.getscreen()
        screen.onclick(_set_cell_value)

        print("\nClick on any cell to specify its value")
        print("- - - - - - - - - - - - - - - - - - - ")
        q = input("Press ENTER once you are done. The program would begin " 
                 "to solve your sudoku. Or type QUIT to exit.\n ")
        if q.lower() == "quit": 
            exit()
        solve(custom_board,draw_speed)        
        screen.onclick(None)

    turtle.done()
