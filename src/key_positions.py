import chess.pgn
import subprocess
from stockfish import Stockfish
from typing import List, Dict, Tuple
from tqdm import tqdm

positions_table: Dict[str, Tuple[float, List[int]]] = dict()

def identify_key_positions(pgn_file: str, stockfish_path: str = subprocess.check_output(['which', 'stockfish'])[:-1], threshold_lower: float = 2.5, threshold_upper: float = -1.0):
    global positions_table
    
    if threshold_upper == -1:
        threshold_upper: float = __import__("math").sqrt(threshold_lower + 1) * (threshold_lower - 1)

    print(threshold_upper)

    engine = Stockfish(path=stockfish_path, depth=13)

    games: List[chess.pgn.Game] = []

    with open(pgn_file) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
        
            games.append(game)
    
    gn: int = 0

    for game in games:
        gn += 1
        
        board = game.board()
            
        n: int = 0
        moves = list(game.mainline_moves().__iter__())

        for i in tqdm(range(0, len(moves)), desc=f"Parsing game N{gn}"):
            move = moves[i]
            n += 1

            if board.fen() in positions_table:
                eval: float = positions_table[board.fen()][0]
                if eval >= threshold_lower and eval <= threshold_upper:
                    positions_table[board.fen()][1].append(board.fen())
                
                board.push(move)
                continue

            engine.set_fen_position(board.fen())
            
            top_moves = engine.get_top_moves(2)
            if len(top_moves) < 2:
                board.push(move)
                continue
    
            second_best = top_moves[1]["Move"]
            besteval = engine.get_evaluation()["value"]
            
            engine.make_moves_from_current_position([second_best])
            eval: float = (besteval - engine.get_evaluation()["value"]) / 10
            
            if eval >= threshold_lower and eval <= threshold_upper:
                positions_table[board.fen()] = (eval, [n])
            
            board.push(move)

identify_key_positions("data/twic1300.pgn", threshold_lower=4)

print(positions_table)

for i, fen in enumerate(positions_table.keys(), start=1):
    with open(f"svgs/key_position_{i}.svg", "w+") as svg:
        svg.write(chess.svg.board(chess.Board(fen)))
    print(f"Key Position {i}: {fen}")


