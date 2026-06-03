from stockfish import Stockfish
from config import STOCKFISH_PATH, DIFFICULTY_LEVELS, CURRENT_DIFFICULTY
import chess
import os
import random

class ChessEngine:
    def __init__(self):
        self.stockfish = None
        self.difficulty_settings = DIFFICULTY_LEVELS[CURRENT_DIFFICULTY]
        
        if os.path.exists(STOCKFISH_PATH):
            try:
                self.stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2, "Minimum Thinking Time": 30})
                self.set_difficulty(CURRENT_DIFFICULTY)
                print(f"Stockfish engine initialized successfully at '{CURRENT_DIFFICULTY}' difficulty.")
            except Exception as e:
                print(f"Error initializing Stockfish: {e}")
        else:
            print(f"Stockfish executable not found at {STOCKFISH_PATH}.")

    def is_ready(self):
        return self.stockfish is not None

    def set_difficulty(self, difficulty_name):
        if self.is_ready():
            self.difficulty_settings = DIFFICULTY_LEVELS[difficulty_name]
            self.stockfish.set_skill_level(self.difficulty_settings['skill'])
            print(f"Stockfish difficulty set to '{difficulty_name}'.")

    def get_humanized_move(self, board):
        if not self.is_ready():
            return None

        # Decide whether to make a blunder
        if random.randint(1, 100) <= self.difficulty_settings['blunder_chance']:
            return self._get_blunder_move(board)
        else:
            return self._get_best_move(board)

    def _get_best_move(self, board):
        self.stockfish.set_fen_position(board.fen())
        best_move_uci = self.stockfish.get_best_move()
        if best_move_uci:
            return chess.Move.from_uci(best_move_uci)
        return None

    def _get_blunder_move(self, board):
        print("AI is making a blunder...")
        legal_moves = list(board.legal_moves)
        
        # Get the top N moves to avoid
        top_n = self.difficulty_settings['top_n']
        top_moves_data = self.stockfish.get_top_moves(top_n)
        
        if not top_moves_data:
            # If stockfish returns no moves, pick any legal move
            return random.choice(legal_moves) if legal_moves else None

        top_moves = [chess.Move.from_uci(move['Move']) for move in top_moves_data]

        # Create a list of "bad" moves by excluding the top N
        blunder_moves = [move for move in legal_moves if move not in top_moves]

        if blunder_moves:
            return random.choice(blunder_moves)
        else:
            # If all legal moves are considered "good", just pick any of them
            return random.choice(legal_moves) if legal_moves else None

    def get_evaluation(self, board):
        """Returns the engine's evaluation of the board from White's perspective."""
        if not self.is_ready():
            return None
            
        self.stockfish.set_fen_position(board.fen())
        return self.stockfish.get_evaluation()
