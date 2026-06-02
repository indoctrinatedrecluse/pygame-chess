import chess
import pygame
from config import DEFAULT_TIME, AI_PLAYS_AS

class GameState:
    def __init__(self):
        self.board = chess.Board()
        self.timers = {chess.WHITE: DEFAULT_TIME, chess.BLACK: DEFAULT_TIME}
        self.current_turn_start_time = pygame.time.get_ticks()
        self.game_over = False
        self.outcome = None
        self.san_moves = []

    def reset(self, time_control=DEFAULT_TIME):
        self.board.reset()
        self.timers = {chess.WHITE: time_control, chess.BLACK: time_control}
        self.current_turn_start_time = pygame.time.get_ticks()
        self.game_over = False
        self.outcome = None
        self.san_moves = []

    def update_timer(self):
        if not self.game_over:
            elapsed = (pygame.time.get_ticks() - self.current_turn_start_time) / 1000
            self.timers[self.board.turn] -= elapsed
            self.current_turn_start_time = pygame.time.get_ticks()
            if self.timers[self.board.turn] <= 0:
                self.game_over = True
                self.outcome = self.board.outcome(claim_draw=True)

    def push_move(self, move):
        if move in self.board.legal_moves:
            self.update_timer()
            self.san_moves.append(self.board.san(move))
            self.board.push(move)
            self.current_turn_start_time = pygame.time.get_ticks()
            self.check_game_over()
        else:
            # This case should ideally not be reached if UI logic is correct
            print(f"Error: Illegal move {move} was attempted.")


    def check_game_over(self):
        if self.board.is_game_over():
            self.game_over = True
            self.outcome = self.board.outcome()

    def resign(self):
        self.game_over = True
        # The winner is the player whose turn it is NOT
        winner = not self.board.turn
        self.outcome = chess.Outcome(termination=chess.Termination.CHECKMATE, winner=winner)