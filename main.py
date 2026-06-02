import pygame
import chess
from config import *
from ui import (load_assets, play_sound, draw_board, draw_pieces, draw_dragged_piece, 
                draw_highlights, draw_game_over, draw_button, get_promotion_choice,
                draw_side_panel)
from game_state import GameState
from engine import ChessEngine

def get_square_from_mouse(pos):
    """Converts mouse coordinates to a chess square index."""
    if pos[0] > BOARD_SIZE or pos[1] > BOARD_SIZE: return None
    return chess.square(pos[0] // SQUARE_SIZE, 7 - (pos[1] // SQUARE_SIZE))

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Chess vs Stockfish")
    load_assets()

    app_state = 'MENU'
    gs = GameState()
    engine = ChessEngine()
    
    selected_square = None
    dragging = False
    
    # Store the latest evaluation
    current_eval = None
    last_eval_time = 0
    EVAL_UPDATE_INTERVAL = 1000 # Update eval every 1000ms
    
    # Center the start button in the right panel or over the board
    start_button = pygame.Rect(BOARD_SIZE + (WIDTH - BOARD_SIZE) // 2 - 100, HEIGHT // 2 - 25, 200, 50)
    
    clock = pygame.time.Clock()

    while True:
        current_time = pygame.time.get_ticks()
        
        if app_state == 'PLAYING':
            gs.update_timer()
            if gs.game_over:
                app_state = 'GAME_OVER'
                play_sound('end')
            
            # --- AI Turn ---
            if not gs.game_over and gs.board.turn == AI_PLAYS_AS and engine.is_ready():
                # Get the best move from the engine
                ai_move = engine.get_best_move(gs.board)
                if ai_move:
                    is_capture = gs.board.is_capture(ai_move)
                    gs.push_move(ai_move)
                    play_sound('capture' if is_capture else 'move')
                    
                    if gs.game_over:
                        app_state = 'GAME_OVER'
                        play_sound('end')
                        
            # --- Periodic Evaluation Update ---
            # We don't want to freeze the UI asking stockfish for eval every frame.
            if not gs.game_over and engine.is_ready():
                if current_time - last_eval_time > EVAL_UPDATE_INTERVAL:
                    current_eval = engine.get_evaluation(gs.board)
                    last_eval_time = current_time

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if app_state == 'MENU':
                if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                    app_state = 'PLAYING'
                    gs.reset()
                    play_sound('start')
                    # Get initial eval
                    if engine.is_ready():
                        current_eval = engine.get_evaluation(gs.board)
                        last_eval_time = pygame.time.get_ticks()
            
            elif app_state == 'GAME_OVER':
                if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                    app_state = 'PLAYING'
                    gs.reset()
                    play_sound('start')
                    current_eval = None

            elif app_state == 'PLAYING' and gs.board.turn != AI_PLAYS_AS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    start_square = get_square_from_mouse(pos)
                    # Only allow selecting pieces of the player's color
                    if start_square is not None:
                        piece = gs.board.piece_at(start_square)
                        if piece and piece.color == gs.board.turn:
                            selected_square = start_square
                            dragging = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging:
                        end_square = get_square_from_mouse(pygame.mouse.get_pos())
                        move = None
                        if end_square is not None:
                            is_pawn = gs.board.piece_at(selected_square).piece_type == chess.PAWN
                            is_promo = chess.square_rank(end_square) in [0, 7]
                            promo_choice = None
                            
                            # Check if it's a legal promotion move before showing the dialog
                            test_promo_move = chess.Move(selected_square, end_square, promotion=chess.QUEEN)
                            if is_pawn and is_promo and test_promo_move in gs.board.legal_moves:
                                promo_choice = get_promotion_choice(screen, gs.board.turn)
                                
                            if is_promo and promo_choice:
                                move = chess.Move(selected_square, end_square, promotion=promo_choice)
                            else:
                                move = chess.Move(selected_square, end_square)
                        
                        if move and move in gs.board.legal_moves:
                            is_capture = gs.board.is_capture(move)
                            gs.push_move(move)
                            play_sound('capture' if is_capture else 'move')
                            selected_square = None
                            
                            # Instantly update eval after a player move to feel responsive
                            if engine.is_ready():
                                current_eval = engine.get_evaluation(gs.board)
                                last_eval_time = pygame.time.get_ticks()
                                
                            if gs.game_over:
                                app_state = 'GAME_OVER'
                                play_sound('end')
                        else:
                            if end_square != selected_square:
                                play_sound('error')
                    dragging = False

        # --- Drawing ---
        screen.fill(BG_COLOR)
        
        if app_state != 'MENU':
            draw_board(screen)
            last_move = gs.board.peek() if gs.board.move_stack else None
            draw_highlights(screen, gs.board, selected_square, last_move)
            draw_pieces(screen, gs.board, selected_square if dragging else None)
            if dragging and selected_square:
                piece_key = f"{'w' if gs.board.turn == gs.board.turn else 'b'}{gs.board.piece_at(selected_square).symbol().lower()}"
                draw_dragged_piece(screen, piece_key, pygame.mouse.get_pos())
            
            draw_side_panel(screen, gs, current_eval)

        if app_state == 'GAME_OVER':
            result_text = "Draw!"
            if gs.outcome:
                if gs.outcome.winner is not None:
                    result_text = f"{'White' if gs.outcome.winner else 'Black'} wins!"
                elif gs.outcome.termination == chess.Termination.TIMEOUT:
                    result_text = f"{'Black' if gs.board.turn == chess.WHITE else 'White'} wins on time!"
            
            draw_game_over(screen, result_text)
            
            game_over_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
            draw_button(screen, "New Game", game_over_btn_rect)
            start_button = game_over_btn_rect
        
        if app_state == 'MENU':
            draw_board(screen)
            draw_pieces(screen, gs.board, None)
            draw_side_panel(screen, gs, current_eval)
            
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            screen.blit(s, (0, 0))
            
            menu_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
            draw_button(screen, "Start Game", menu_btn_rect)
            start_button = menu_btn_rect

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
