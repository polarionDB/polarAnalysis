import chess.pgn
from concurrent.futures import ThreadPoolExecutor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import sys
from typing import Dict, Tuple
from matplotlib import pyplot as plt 
import matplotlib.colors as mcolors
from tqdm import tqdm

positions_queue: (int, str) = []
average_moves: (Dict[int, Tuple[int, float]], Dict[int, Tuple[int, float]]) = ({}, {})

def positions_wrapper(args: chess.pgn.Game):
    board = args.board()

    n: int = 1

    for move in args.mainline_moves():
        positions_queue.append((n, board.fen()))
        board.push(move)
        n += 1

def average_moves_wrapper(args: Tuple[int, str]):
    n: int = args[0]
    board: chess.Board = chess.Board(args[1])

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

def main():
    pgn = open("data/twic_full.pgn", encoding="utf-8")
    
    print("Parsing games")

    game = chess.pgn.read_game(pgn)
    games = []
    
    while game is not None:
        games.append(game)
        try:
            game = chess.pgn.read_game(pgn)
        except:
            continue

    print(f"DONE parsed {len(games)} games", file=sys.stderr)

    global positions_queue
    global average_moves

    positions_list = positions_queue

    print("Generating positions")

    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(positions_wrapper, games)
        executor.shutdown()

    games = []
    print(f"DONE Generated {len(positions_queue)} positions", file=sys.stderr)

    print("Calculating average legal moves per ply")

    n: int = 1

    for position in position_list:
        average_moves_wrapper(position)
        positions_list.pop()
        n += 1

    positions_queue = []  # Clear the queue

    fig, (whitesub, blacksub) = plt.subplots(2, 1, sharex=True)

    fig.suptitle("Average Legal Moves per Ply")
    whitesub.set_ylabel("Legal Moves Available (White)", fontsize=8)
    blacksub.set_xlabel("Ply Number")
    blacksub.set_ylabel("Legal Moves Available (Black)", fontsize=8)

    p1 = whitesub.scatter(average_moves[0].keys(), [value[1] for value in average_moves[0].values()], label='White', c=mcolors.CSS4_COLORS['orange'], alpha=1)
    p2 = blacksub.scatter(average_moves[1].keys(), [value[1] for value in average_moves[1].values()], label='Black', c=mcolors.CSS4_COLORS['orange'], alpha=1)

    plt.savefig("average_legal_moves.png")
    plt.savefig("average_legal_moves.eps")

if __name__ == "__main__":
    main()
