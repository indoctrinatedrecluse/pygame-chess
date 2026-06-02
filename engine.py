from stockfish import Stockfish
from config import STOCKFISH_PATH, DEFAULT_DIFFICULTY
import chess
import os

class ChessEngine:
    def __init__(self):
        self.stockfish = None
        if os.path.exists(STOCKFISH_PATH):
            try:
                self.stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2, "Minimum Thinking Time": 10})
                self.set_difficulty(DEFAULT_DIFFICULTY)
                print("Stockfish engine initialized successfully.")
            except Exception as e:
                print(f"Error initializing Stockfish: {e}")
        else:
            print(f"Stockfish executable not found at {STOCKFISH_PATH}.")

    def is_ready(self):
        return self.stockfish is not None

    def set_difficulty(self, skill_level):
        if self.is_ready():
            self.stockfish.set_skill_level(skill_level)
            print(f"Stockfish skill level set to {skill_level}.")

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
        return eval_data