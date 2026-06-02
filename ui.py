import pygame
import chess
import pygame_svg
import os
from config import *

IMAGES = {}
SOUNDS = {}

def load_assets():
    """Loads all game assets, including images and sounds."""
    global UI_FONT, UI_FONT_LARGE
    UI_FONT = pygame.font.SysFont(None, UI_FONT_SIZE)
    UI_FONT_LARGE = pygame.font.SysFont(None, UI_FONT_LARGE_SIZE)
    load_images()
    load_sounds()

def load_images():
    """Loads piece images."""
    pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
    for piece in pieces:
        svg_path = os.path.join(PIECES_DIR, f"{piece}.svg")
        png_path = os.path.join(PIECES_DIR, f"{piece}.png")
        if os.path.exists(svg_path):
            IMAGES[piece] = pygame_svg.Svg(svg_path, size=(SQUARE_SIZE, SQUARE_SIZE))
        elif os.path.exists(png_path):
            IMAGES[piece] = pygame.transform.smoothscale(pygame.image.load(png_path), (SQUARE_SIZE, SQUARE_SIZE))

def load_sounds():
    """Loads sound effects."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    sound_files = {'start': 'start.wav', 'end': 'end.wav', 'move': 'move.wav', 'capture': 'capture.wav', 'error': 'error.wav'}
    for name, filename in sound_files.items():
        path = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(path):
            SOUNDS[name] = pygame.mixer.Sound(path)

def play_sound(name):
    if name in SOUNDS:
        SOUNDS[name].play()

def draw_board(screen):
    """Draws the chessboard and coordinates."""
    for r in range(8):
        for c in range(8):
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    # Draw rank/file labels
    for i in range(8):
        # Ranks (1-8)
        label = UI_FONT.render(str(8 - i), True, DARK_SQUARE if i % 2 == 0 else LIGHT_SQUARE)
        screen.blit(label, (5, i * SQUARE_SIZE + 5))
        # Files (a-h)
        label = UI_FONT.render(chr(ord('a') + i), True, LIGHT_SQUARE if i % 2 == 0 else DARK_SQUARE)
        screen.blit(label, (i * SQUARE_SIZE + SQUARE_SIZE - 15, BOARD_SIZE - 25))

def draw_pieces(screen, board, dragging_square):
    """Draws the pieces."""
    for square in chess.SQUARES:
        if square == dragging_square: continue
        piece = board.piece_at(square)
        if piece:
            key = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().lower()}"
            if key in IMAGES:
                screen.blit(IMAGES[key], pygame.Rect(chess.square_file(square) * SQUARE_SIZE, (7 - chess.square_rank(square)) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_dragged_piece(screen, piece_key, pos):
    if piece_key in IMAGES:
        img = IMAGES[piece_key].surface if isinstance(IMAGES[piece_key], pygame_svg.Svg) else IMAGES[piece_key]
        screen.blit(img, img.get_rect(center=pos))

def draw_highlights(screen, board, selected_square, last_move):
    """Draws highlights for moves, selection, and checks."""
    if board.is_check():
        king_square = board.king(board.turn)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(HIGHLIGHT_CHECK)
        screen.blit(s, (chess.square_file(king_square) * SQUARE_SIZE, (7 - chess.square_rank(king_square)) * SQUARE_SIZE))

    if last_move:
        for square in [last_move.from_square, last_move.to_square]:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(HIGHLIGHT_LAST_MOVE)
            screen.blit(s, (chess.square_file(square) * SQUARE_SIZE, (7 - chess.square_rank(square)) * SQUARE_SIZE))

    if selected_square is not None:
        for move in board.legal_moves:
            if move.from_square == selected_square:
                center = (chess.square_file(move.to_square) * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - chess.square_rank(move.to_square)) * SQUARE_SIZE + SQUARE_SIZE // 2)
                if board.is_capture(move):
                    pygame.draw.circle(screen, HIGHLIGHT_CAPTURE, center, SQUARE_SIZE // 3, 5)
                else:
                    pygame.draw.circle(screen, HIGHLIGHT_LEGAL_MOVE, center, SQUARE_SIZE // 6)

def draw_game_over(screen, text):
    """Draws the game over message."""
    s = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))
    label = UI_FONT_LARGE.render(text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=(BOARD_SIZE / 2, BOARD_SIZE / 2)))

def draw_button(screen, text, rect):
    pygame.draw.rect(screen, DARK_SQUARE, rect)
    pygame.draw.rect(screen, LIGHT_SQUARE, rect, 3)
    label = UI_FONT.render(text, True, LIGHT_SQUARE)
    screen.blit(label, label.get_rect(center=rect.center))

def get_promotion_choice(screen, turn):
    """Displays promotion choice and returns the selected piece type."""
    choices = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    choice_rects = []
    
    for i, piece_type in enumerate(choices):
        rect = pygame.Rect(BOARD_SIZE + 50, 100 + i * (SQUARE_SIZE + 10), SQUARE_SIZE, SQUARE_SIZE)
        choice_rects.append(rect)
        key = f"{'w' if turn == chess.WHITE else 'b'}{chess.piece_symbol(piece_type).lower()}"
        if key in IMAGES:
            screen.blit(IMAGES[key], rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(choice_rects):
                    if rect.collidepoint(event.pos):
                        return choices[i]

def format_time(seconds):
    """Formats seconds into MM:SS."""
    m, s = divmod(int(max(0, seconds)), 60)
    return f"{m:02d}:{s:02d}"

def draw_eval_bar(screen, eval_data):
    """Draws the evaluation bar beside the board."""
    bar_width = 20
    bar_rect = pygame.Rect(BOARD_SIZE, 0, bar_width, BOARD_SIZE)
    
    # Background is black advantage
    pygame.draw.rect(screen, (40, 40, 40), bar_rect)
    
    if not eval_data:
        # Draw a neutral bar if no eval
        pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(BOARD_SIZE, BOARD_SIZE // 2, bar_width, BOARD_SIZE // 2))
        return

    # Calculate fill percentage for white (0.0 to 1.0)
    # A standard way is to map centipawns to a win probability or a simple clamp
    # Let's map -1000 to 1000 cp (or mates) to 0.0 - 1.0
    fill_percent = 0.5
    
    if eval_data['type'] == 'cp':
        cp = eval_data['value']
        # Clamp between -1000 and 1000
        cp = max(-1000, min(1000, cp))
        # Map to 0-1 (e.g. 0 cp -> 0.5, 1000 cp -> 1.0)
        # Using a non-linear scale is better, but linear is fine for now
        # Actually, let's use a standard scaling where 1 pawn = small shift, 5 pawns = big shift
        fill_percent = 0.5 + (cp / 2000.0)
    elif eval_data['type'] == 'mate':
        mate_in = eval_data['value']
        if mate_in > 0:
            fill_percent = 1.0 # White is mating
        elif mate_in < 0:
            fill_percent = 0.0 # Black is mating
            
    fill_percent = max(0.0, min(1.0, fill_percent))
            
    white_height = int(BOARD_SIZE * fill_percent)
    white_rect = pygame.Rect(BOARD_SIZE, BOARD_SIZE - white_height, bar_width, white_height)
    pygame.draw.rect(screen, (220, 220, 220), white_rect)

def draw_side_panel(screen, game_state, eval_data=None):
    """Draws the right-side panel with timers and info."""
    # Start drawing panel *after* the eval bar
    panel_start_x = BOARD_SIZE + 20
    panel_rect = pygame.Rect(panel_start_x, 0, WIDTH - panel_start_x, HEIGHT)
    pygame.draw.rect(screen, BG_COLOR, panel_rect)

    draw_eval_bar(screen, eval_data)

    # Timers
    black_time_str = format_time(game_state.timers[chess.BLACK])
    white_time_str = format_time(game_state.timers[chess.WHITE])

    # Highlight active timer
    black_color = HIGHLIGHT_LAST_MOVE if game_state.board.turn == chess.BLACK and not game_state.game_over else (200, 200, 200)
    white_color = HIGHLIGHT_LAST_MOVE if game_state.board.turn == chess.WHITE and not game_state.game_over else (200, 200, 200)

    black_timer = UI_FONT_LARGE.render(black_time_str, True, black_color)
    white_timer = UI_FONT_LARGE.render(white_time_str, True, white_color)

    screen.blit(black_timer, (panel_start_x + 30, 50))
    screen.blit(white_timer, (panel_start_x + 30, HEIGHT - 100))

    # 50-move rule counter
    halfmove_clock = game_state.board.halfmove_clock
    rule_text = f"50-Move Rule: {halfmove_clock}/100"
    rule_label = UI_FONT.render(rule_text, True, (150, 150, 150))
    screen.blit(rule_label, (panel_start_x + 20, HEIGHT // 2))
    
    # Display numeric eval text
    if eval_data:
        if eval_data['type'] == 'cp':
            eval_text = f"{eval_data['value'] / 100.0:+.2f}"
        else:
            eval_text = f"M{abs(eval_data['value'])}"
            if eval_data['value'] < 0: eval_text = "-" + eval_text
        eval_label = UI_FONT.render(eval_text, True, (200, 200, 200))
        screen.blit(eval_label, (panel_start_x + 20, HEIGHT // 2 + 40))
