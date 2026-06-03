import pygame
import chess
import threading
import time
import random
from queue import Queue
from config import *
from ui import (load_assets, play_sound, draw_board, draw_pieces, draw_dragged_piece, 
                draw_highlights, draw_game_over, draw_button, get_promotion_choice,
                draw_side_panel, draw_timer_selection, draw_difficulty_selection, 
                draw_side_selection, SIDE_RECTS, TIME_CONTROL_RECTS, DIFFICULTY_RECTS)
from game_state import GameState
from engine import ChessEngine

AI_MOVE_EVENT = pygame.USEREVENT + 1
EVAL_UPDATE_EVENT = pygame.USEREVENT + 2
engine_queue = Queue()

def get_square_from_mouse(pos, board_flipped):
    """Converts mouse coordinates to a chess square index, handling a flipped board."""
    if pos[0] > BOARD_SIZE or pos[1] > BOARD_SIZE: return None
    col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
    if board_flipped:
        return chess.square(7 - col, row)
    else:
        return chess.square(col, 7 - row)

def engine_worker(queue, engine):
    """The main worker function for the engine thread."""
    while True:
        task, board = queue.get()
        if task == 'get_move':
            best_move = engine.get_humanized_move(board)
            pygame.event.post(pygame.event.Event(AI_MOVE_EVENT, {'move': best_move}))
        elif task == 'get_eval':
            eval_data = engine.get_evaluation(board)
            pygame.event.post(pygame.event.Event(EVAL_UPDATE_EVENT, {'eval': eval_data}))
        queue.task_done()

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Chess vs Stockfish")
    load_assets()

    app_state = 'MENU'
    gs = GameState()
    engine = ChessEngine()
    
    if engine.is_ready():
        threading.Thread(target=engine_worker, args=(engine_queue, engine), daemon=True).start()

    selected_square = None
    dragging = False
    board_flipped = False
    current_eval = None
    last_eval_time = 0
    EVAL_UPDATE_INTERVAL = 2000

    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
    flip_button = pygame.Rect(WIDTH - 160, HEIGHT - 120, 140, 40)
    
    clock = pygame.time.Clock()
    selected_time = DEFAULT_TIME

    while True:
        if app_state == 'PLAYING' and not gs.game_over:
            gs.update_timer()
            if gs.timers[gs.board.turn] <= 0:
                gs.game_over = True
                gs.outcome = gs.board.outcome(claim_draw=True)
                play_sound('end')
                app_state = 'GAME_OVER'

            if gs.board.turn == AI_PLAYS_AS and engine.is_ready() and engine_queue.empty():
                engine_queue.put(('get_move', gs.board.copy()))

            if time.time() * 1000 - last_eval_time > EVAL_UPDATE_INTERVAL and engine.is_ready() and engine_queue.empty():
                last_eval_time = time.time() * 1000
                engine_queue.put(('get_eval', gs.board.copy()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == AI_MOVE_EVENT:
                if event.move and not gs.game_over and gs.board.turn == AI_PLAYS_AS:
                    is_capture = gs.board.is_capture(event.move)
                    gs.push_move(event.move)
                    play_sound('capture' if is_capture else 'move')
                    if gs.game_over:
                        app_state = 'GAME_OVER'
                        play_sound('end')
            
            if event.type == EVAL_UPDATE_EVENT:
                current_eval = event.eval

            if app_state == 'MENU':
                if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                    app_state = 'SELECT_TIME'
            
            elif app_state == 'SELECT_TIME':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for time_control, rect in TIME_CONTROL_RECTS.items():
                        if rect.collidepoint(event.pos):
                            selected_time = TIME_CONTROLS[time_control]
                            app_state = 'SELECT_DIFFICULTY'
                            break
            
            elif app_state == 'SELECT_DIFFICULTY':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for diff, rect in DIFFICULTY_RECTS.items():
                        if rect.collidepoint(event.pos):
                            engine.set_difficulty(diff)
                            app_state = 'SELECT_SIDE'
                            break
            
            elif app_state == 'SELECT_SIDE':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for side_text, rect in SIDE_RECTS.items():
                        if rect.collidepoint(event.pos):
                            if side_text == 'White':
                                PLAYER_PLAYS_AS = chess.WHITE
                            elif side_text == 'Black':
                                PLAYER_PLAYS_AS = chess.BLACK
                            else: # Random
                                PLAYER_PLAYS_AS = random.choice([chess.WHITE, chess.BLACK])
                            
                            AI_PLAYS_AS = not PLAYER_PLAYS_AS
                            board_flipped = (PLAYER_PLAYS_AS == chess.BLACK)
                            
                            gs.reset(time_control=selected_time)
                            app_state = 'PLAYING'
                            play_sound('start')
                            break

            elif app_state == 'GAME_OVER':
                if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                    app_state = 'SELECT_TIME'
                    current_eval = None

            elif app_state == 'PLAYING':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if flip_button.collidepoint(pos):
                        board_flipped = not board_flipped
                        continue

                    if gs.board.turn == PLAYER_PLAYS_AS:
                        sq = get_square_from_mouse(pos, board_flipped)
                        if sq is not None:
                            piece = gs.board.piece_at(sq)
                            if piece and piece.color == gs.board.turn:
                                selected_square = sq
                                dragging = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        end_square = get_square_from_mouse(pygame.mouse.get_pos(), board_flipped)
                        move = None
                        if end_square is not None:
                            is_pawn = gs.board.piece_at(selected_square).piece_type == chess.PAWN
                            is_promo = chess.square_rank(end_square) in [0, 7]
                            promo_choice = None
                            
                            test_promo_move = chess.Move(selected_square, end_square, promotion=chess.QUEEN)
                            if is_pawn and is_promo and test_promo_move in gs.board.legal_moves:
                                promo_choice = get_promotion_choice(screen, gs.board.turn)
                                
                            move = chess.Move(selected_square, end_square, promotion=promo_choice)
                        
                        if move and move in gs.board.legal_moves:
                            is_capture = gs.board.is_capture(move)
                            gs.push_move(move)
                            play_sound('capture' if is_capture else 'move')
                            if gs.game_over:
                                app_state = 'GAME_OVER'
                                play_sound('end')
                        else:
                            if end_square != selected_square:
                                play_sound('error')
                    dragging = False
                    selected_square = None

        screen.fill(BG_COLOR)
        
        if app_state == 'MENU':
            draw_board(screen, board_flipped)
            draw_pieces(screen, gs.board, None, board_flipped)
            draw_side_panel(screen, gs, current_eval)
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            screen.blit(s, (0, 0))
            draw_button(screen, "Start Game", start_button)

        elif app_state == 'SELECT_TIME':
            draw_timer_selection(screen)
        
        elif app_state == 'SELECT_DIFFICULTY':
            draw_difficulty_selection(screen)
            
        elif app_state == 'SELECT_SIDE':
            draw_side_selection(screen)

        else: # PLAYING or GAME_OVER
            draw_board(screen, board_flipped)
            last_move = gs.board.peek() if gs.board.move_stack else None
            draw_highlights(screen, gs.board, selected_square, last_move, board_flipped)
            draw_pieces(screen, gs.board, selected_square if dragging else None, board_flipped)
            if dragging and selected_square:
                piece = gs.board.piece_at(selected_square)
                if piece:
                    piece_key = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().lower()}"
                    draw_dragged_piece(screen, piece_key, pygame.mouse.get_pos())
            
            draw_side_panel(screen, gs, current_eval)
            if app_state == 'PLAYING':
                draw_button(screen, "Flip Board", flip_button)

            if app_state == 'GAME_OVER':
                result_text = "Draw!"
                if gs.outcome:
                    winner = gs.outcome.winner
                    if winner is not None:
                        result_text = f"{'White' if winner else 'Black'} wins!"
                draw_game_over(screen, result_text)
                draw_button(screen, "New Game", start_button)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
