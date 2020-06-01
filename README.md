# Sudoku Solver - Visualization tool

Sudoku Solver allows you to quickly visualize a Sudoku board as it is being solved. It utilizes a classical backtracking algorithm;  therefore, some difficult grids might take more time. The purpose of this program is to visualize the execution of backtracking step-by-step, and not to efficiently solve the puzzle using more sophisticated algorithms.

## Features

 - Random Sudoku grid generator
 - Sudoku grid validation
 - Visualization's speed control
 - Custom grid input through GUI
 - Generate multiple solutions 
 - Graphical User Interface
 - Command line arguments
 
## Usage
Prerequisite:
 - Python 3

To solve a your own custom Sudoku grid simply run the following command in the terminal:

    $ python solver.py
Additional command line arguments:

    $ python solver.py --help
    
    usage: solver.py [-h] [-r | -e] [-s {0,1,2,3}]
    optional arguments:
      -h, --help            show this help message and exit
      -r, --random          solve a randomly generated 9 x 9 sudoku grid.
      -e, --empty           generate an unsolved sudoku grid.
      -s {0,1,2,3}, --speed {0,1,2,3}
						    controls the speed at which the sudoku is solved.
						    choices: 0: fast, 1: slow, 2: slower, 3: slowest.

## License
This project is licensed under the MIT License - see the [LICENSE.md](/LICENSE.md) file for details