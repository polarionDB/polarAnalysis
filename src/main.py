import chess.pgn
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import copy
from typing import Dict, Tuple
from matplotlib import pyplot as plt 
import matplotlib.colors as mcolors

positions_queue: (int, chess.Board) = []
average_moves: (Dict[int, Tuple[int, float]], Dict[int, Tuple[int, float]]) = ({}, {})

def positions_wrapper(args: chess.pgn.Game):
    board = args.board()

    n: int = 1

    for move in args.mainline_moves():
        positions_queue.append((n, copy.copy(board)))
        board.push(move)
        n += 1

def average_moves_wrapper(args: Tuple[int, chess.Board]):
    n: int = args[0]
    board: chess.Board = args[1]

    moves = list(board.generate_legal_moves())

    if n % 2 == 1:
        if not (n in average_moves[0]):
            average_moves[0][n] = (1, len(moves))
        else:
            average_moves[0][n] = (average_moves[0][n][0] + 1, (average_moves[0][n][1] * average_moves[0][n][0] + len(moves)) / (average_moves[0][n][0] + 1))
    else:
        if not (n in average_moves[1]):
            average_moves[1][n] = (1, len(moves))
        else:
            average_moves[1][n] = (average_moves[1][n][0] + 1, (average_moves[1][n][1] * average_moves[1][n][0] + len(moves)) / (average_moves[1][n][0] + 1))

def gpr_approximation(average_moves_dict, label, plot, color):
    x = np.array(list(average_moves_dict.keys())).reshape(-1, 1)
    y = np.array([value[1] for value in average_moves_dict.values()])

    # Define the kernel for the Gaussian Process Regression
    kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))

    # Create and fit the Gaussian Process Regression model
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=0)
    gpr.fit(x, y)

    print(f"Approximation Function for {label}:")
    print(f"Kernel Parameters: {gpr.kernel_}")

    # Plot the regression line
    x_pred = np.arange(min(x), max(x) + 1).reshape(-1, 1)
    y_pred, sigma = gpr.predict(x_pred, return_std=True)

    if plot is None:
        plt.plot(x_pred, y_pred, label=f'Approximation for {label}', color=color)
        plt.fill_between(x_pred.flatten(), y_pred - sigma, y_pred + sigma, alpha=0.2, color=color)
    else:
        plot.plot(x_pred, y_pred, label=f'Approximation for {label}', color=color)
        plot.fill_between(x_pred.flatten(), y_pred - sigma, y_pred + sigma, alpha=0.2, color=color)

def main():
    pgn = open("data/twic1300.pgn")
    
    print("Parsing games")

    game = chess.pgn.read_game(pgn)
    games = []
    
    while game is not None:
        games.append(game)
        game = chess.pgn.read_game(pgn)

    print(f"DONE parsed {len(games)} games")

    global positions_queue
    global average_moves

    positions_list = positions_queue

    print("Generating positions")

    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(positions_wrapper, games)
        executor.shutdown()

    games = []
    print(f"DONE Generated {len(positions_queue)} positions")

    print("Calculating average legal moves per ply")

    n: int = 1

    for position in positions_list:
        if n % 1000 == 0:
            print(f"\tON POSITION {n}")
        average_moves_wrapper(position)
        positions_list.pop()
        n += 1

    positions_queue = []  # Clear the queue

    plt.xlabel("Ply Number")
    plt.ylabel("Legal Moves Avaliable")

    whitesub = plt.subplot(211)
    blacksub = plt.subplot(212)

    gpr_approximation(average_moves[0], 'White', whitesub, mcolors.CSS4_COLORS['royalblue'])
    gpr_approximation(average_moves[1], 'Black', blacksub, mcolors.CSS4_COLORS['royalblue'])
    
    whitesub.scatter(average_moves[0].keys(), [value[1] for value in average_moves[0].values()], label = 'White', c=mcolors.CSS4_COLORS['orange'], alpha=1)
    blacksub.scatter(average_moves[1].keys(), [value[1] for value in average_moves[1].values()], label = 'Black', c=mcolors.CSS4_COLORS['orange'], alpha=1)

    whitesub.legend()
    blacksub.legend()
    plt.legend()

    plt.savefig("graph_.png")

if __name__ == "__main__":
    main()
