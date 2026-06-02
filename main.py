import pygame
import chess
import threading
import time
from queue import Queue
from config import *
from ui import (load_assets, play_sound, draw_board, draw_pieces, draw_dragged_piece, 
                draw_highlights, draw_game_over, draw_button, get_promotion_choice,
                draw_side_panel, draw_timer_selection, draw_difficulty_selection, 
                save_pgn, TIME_CONTROL_RECTS, DIFFICULTY_RECTS)
from game_state import GameState
from engine import ChessEngine

# --- Custom Events ---
AI_MOVE_EVENT = pygame.USEREVENT + 1
EVAL_UPDATE_EVENT = pygame.USEREVENT + 2

# --- Thread-safe Queue for Engine Communication ---
engine_queue = Queue()

def get_square_from_mouse(pos):
    """Converts mouse coordinates to a chess square index."""
    if pos[0] > BOARD_SIZE or pos[1] > BOARD_SIZE: return None
    return chess.square(pos[0] // SQUARE_SIZE, 7 - (pos[1] // SQUARE_SIZE))

def engine_worker(queue, engine):
    """The main worker function for the engine thread."""
    while True:
        task, board = queue.get()
        if task == 'get_move':
            best_move = engine.get_best_move(board)
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
    else:
        print("WARNING: Stockfish engine not found or not configured. AI will not play.")

    selected_square = None
    dragging = False
    scroll_y = 0
    
    current_eval = None
    last_eval_time = 0
    EVAL_UPDATE_INTERVAL = 2000

    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
    save_pgn_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 125, 200, 50)
    resign_button = pygame.Rect(WIDTH - 160, HEIGHT - 60, 140, 40)
    
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

            if event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * 20
                scroll_y = max(0, scroll_y)

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
                            engine.set_difficulty(DIFFICULTY_LEVELS[diff])
                            gs.reset(time_control=selected_time)
                            app_state = 'PLAYING'
                            play_sound('start')
                            break

            elif app_state == 'GAME_OVER':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        app_state = 'SELECT_TIME'
                        current_eval = None
                        scroll_y = 0
                    elif save_pgn_button.collidepoint(event.pos):
                        save_pgn(gs)
                    elif exit_button.collidepoint(event.pos):
                        pygame.quit()
                        return

            elif app_state == 'PLAYING' and gs.board.turn != AI_PLAYS_AS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if resign_button.collidepoint(pos):
                        gs.resign()
                        app_state = 'GAME_OVER'
                        play_sound('end')
                        continue

                    sq = get_square_from_mouse(pos)
                    if sq is not None:
                        if selected_square is None:
                            piece = gs.board.piece_at(sq)
                            if piece and piece.color == gs.board.turn:
                                selected_square = sq
                        else:
                            if selected_square == sq:
                                selected_square = None
                                continue
                            
                            move = chess.Move(selected_square, sq)
                            is_pawn = gs.board.piece_at(selected_square).piece_type == chess.PAWN
                            is_promo = chess.square_rank(sq) in [0, 7]
                            if is_pawn and is_promo and chess.Move(selected_square, sq, promotion=chess.QUEEN) in gs.board.legal_moves:
                                promo_choice = get_promotion_choice(screen, gs.board.turn)
                                move = chess.Move(selected_square, sq, promotion=promo_choice)

                            if move in gs.board.legal_moves:
                                is_capture = gs.board.is_capture(move)
                                gs.push_move(move)
                                play_sound('capture' if is_capture else 'move')
                                if gs.game_over:
                                    app_state = 'GAME_OVER'
                                    play_sound('end')
                            else:
                                play_sound('error')
                            selected_square = None
                
                elif event.type == pygame.MOUSEMOTION:
                    if selected_square is not None and pygame.mouse.get_pressed()[0]:
                        dragging = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        end_square = get_square_from_mouse(pygame.mouse.get_pos())
                        if end_square is not None and selected_square is not None:
                            move = chess.Move(selected_square, end_square)
                            is_pawn = gs.board.piece_at(selected_square).piece_type == chess.PAWN
                            is_promo = chess.square_rank(end_square) in [0, 7]
                            if is_pawn and is_promo and chess.Move(selected_square, end_square, promotion=chess.QUEEN) in gs.board.legal_moves:
                                promo_choice = get_promotion_choice(screen, gs.board.turn)
                                move = chess.Move(selected_square, end_square, promotion=promo_choice)

                            if move in gs.board.legal_moves:
                                is_capture = gs.board.is_capture(move)
                                gs.push_move(move)
                                play_sound('capture' if is_capture else 'move')
                                if gs.game_over:
                                    app_state = 'GAME_OVER'
                                    play_sound('end')
                        selected_square = None
                    dragging = False

        screen.fill(BG_COLOR)
        
        if app_state == 'MENU':
            draw_board(screen)
            draw_pieces(screen, gs.board, None)
            draw_side_panel(screen, gs, current_eval)
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            screen.blit(s, (0, 0))
            draw_button(screen, "Start Game", start_button)

        elif app_state == 'SELECT_TIME':
            draw_timer_selection(screen)
        
        elif app_state == 'SELECT_DIFFICULTY':
            draw_difficulty_selection(screen)

        else: # PLAYING or GAME_OVER
            draw_board(screen)
            last_move = gs.board.peek() if gs.board.move_stack else None
            draw_highlights(screen, gs.board, selected_square, last_move)
            draw_pieces(screen, gs.board, selected_square if dragging else None)
            if dragging and selected_square:
                piece = gs.board.piece_at(selected_square)
                if piece:
                    piece_key = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().lower()}"
                    draw_dragged_piece(screen, piece_key, pygame.mouse.get_pos())
            
            draw_side_panel(screen, gs, current_eval, scroll_y)
            if app_state == 'PLAYING':
                draw_button(screen, "Resign", resign_button)

            if app_state == 'GAME_OVER':
                result_text = "Draw!"
                if gs.outcome:
                    winner = gs.outcome.winner
                    if winner is not None:
                        result_text = f"{'White' if winner else 'Black'} wins!"
                    else:
                        result_text = "Draw"
                draw_game_over(screen, result_text)
                draw_button(screen, "New Game", start_button)
                draw_button(screen, "Save PGN", save_pgn_button)
                draw_button(screen, "Exit Game", exit_button)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()