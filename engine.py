from stockfish import Stockfish
from config import STOCKFISH_PATH, ENGINE_DIFFICULTY
import chess
import os

class ChessEngine:
    def __init__(self):
        self.stockfish = None
        if os.path.exists(STOCKFISH_PATH):
            try:
                # Basic parameters to ensure smooth performance
                self.stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2, "Minimum Thinking Time": 10})
                self.stockfish.set_skill_level(ENGINE_DIFFICULTY)
                print("Stockfish engine initialized successfully.")
            except Exception as e:
                print(f"Error initializing Stockfish: {e}")
        else:
            print(f"Stockfish executable not found at {STOCKFISH_PATH}.")
            print("Please download Stockfish from stockfishchess.org and place it in the project root.")

    def is_ready(self):
        return self.stockfish is not None

    def get_best_move(self, board):
        if not self.is_ready():
            return None
        
        self.stockfish.set_fen_position(board.fen())
        best_move_uci = self.stockfish.get_best_move()
        
        if best_move_uci:
            return chess.Move.from_uci(best_move_uci)
        return None

    def get_evaluation(self, board):
        """Returns the engine's evaluation of the board from White's perspective."""
        if not self.is_ready():
            return None
            
        self.stockfish.set_fen_position(board.fen())
        eval_data = self.stockfish.get_evaluation()
        
        # In stockfish python library, 'cp' (centipawns) is positive for white advantage,
        # negative for black advantage, regardless of whose turn it is. 
        # Same for 'mate' (positive = white mates, negative = black mates).
        # We just need to return it directly.
        return eval_data
