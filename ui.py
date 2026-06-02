import pygame
import chess
import os
import chess.pgn
import time
from config import *

IMAGES = {}
SOUNDS = {}
TIME_CONTROL_RECTS = {}
DIFFICULTY_RECTS = {}

def load_assets():
    """Loads all game assets, including images and sounds."""
    global UI_FONT, UI_FONT_LARGE
    UI_FONT = pygame.font.SysFont(None, UI_FONT_SIZE)
    UI_FONT_LARGE = pygame.font.SysFont(None, UI_FONT_LARGE_SIZE)
    load_images()
    load_sounds()

def load_images():
    """Loads piece images, preferring SVG over PNG."""
    pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
    for piece in pieces:
        svg_path = os.path.join(PIECES_DIR, f"{piece}.svg")
        png_path = os.path.join(PIECES_DIR, f"{piece}.png")
        
        try:
            if os.path.exists(svg_path):
                image = pygame.image.load(svg_path)
                IMAGES[piece] = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
            elif os.path.exists(png_path):
                IMAGES[piece] = pygame.transform.smoothscale(pygame.image.load(png_path), (SQUARE_SIZE, SQUARE_SIZE))
        except pygame.error as e:
            print(f"Failed to load asset for {piece}: {e}")
            if os.path.exists(png_path):
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
    for i in range(8):
        label = UI_FONT.render(str(8 - i), True, DARK_SQUARE if i % 2 == 0 else LIGHT_SQUARE)
        screen.blit(label, (5, i * SQUARE_SIZE + 5))
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
        img = IMAGES[piece_key]
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
    pygame.draw.rect(screen, (40, 40, 40), bar_rect)
    
    if not eval_data:
        pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(BOARD_SIZE, BOARD_SIZE // 2, bar_width, BOARD_SIZE // 2))
        return

    fill_percent = 0.5
    if eval_data['type'] == 'cp':
        cp = max(-1000, min(1000, eval_data['value']))
        fill_percent = 0.5 + (cp / 2000.0)
    elif eval_data['type'] == 'mate':
        fill_percent = 1.0 if eval_data['value'] > 0 else 0.0
            
    fill_percent = max(0.0, min(1.0, fill_percent))
    white_height = int(BOARD_SIZE * fill_percent)
    white_rect = pygame.Rect(BOARD_SIZE, BOARD_SIZE - white_height, bar_width, white_height)
    pygame.draw.rect(screen, (220, 220, 220), white_rect)

def draw_side_panel(screen, game_state, eval_data=None, scroll_y=0):
    """Draws the right-side panel with timers, info, and move history."""
    panel_start_x = BOARD_SIZE + 20
    panel_width = WIDTH - panel_start_x
    panel_rect = pygame.Rect(panel_start_x, 0, panel_width, HEIGHT)
    pygame.draw.rect(screen, BG_COLOR, panel_rect)

    draw_eval_bar(screen, eval_data)

    black_time_str = format_time(game_state.timers[chess.BLACK])
    white_time_str = format_time(game_state.timers[chess.WHITE])
    black_color = HIGHLIGHT_LAST_MOVE if game_state.board.turn == chess.BLACK and not game_state.game_over else (200, 200, 200)
    white_color = HIGHLIGHT_LAST_MOVE if game_state.board.turn == chess.WHITE and not game_state.game_over else (200, 200, 200)
    black_timer = UI_FONT_LARGE.render(black_time_str, True, black_color)
    white_timer = UI_FONT_LARGE.render(white_time_str, True, white_color)
    screen.blit(black_timer, (panel_start_x + 30, 50))
    screen.blit(white_timer, (panel_start_x + 30, HEIGHT - 100))

    if eval_data:
        eval_text = f"{eval_data['value'] / 100.0:+.2f}" if eval_data['type'] == 'cp' else f"M{abs(eval_data['value'])}"
        if eval_data['type'] == 'mate' and eval_data['value'] < 0: eval_text = "-" + eval_text
        eval_label = UI_FONT.render(eval_text, True, (200, 200, 200))
        screen.blit(eval_label, (panel_start_x + 20, HEIGHT // 2 + 40))
    
    move_history_y_start = 120
    move_area_height = HEIGHT - 240
    move_surface = pygame.Surface((panel_width, move_area_height))
    move_surface.fill(BG_COLOR)

    y_offset = 0
    for i, san_move in enumerate(game_state.san_moves):
        move_number = i // 2 + 1
        if i % 2 == 0:
            text = f"{move_number}. {san_move}"
            move_label = UI_FONT.render(text, True, (200, 200, 200))
            move_surface.blit(move_label, (10, y_offset - scroll_y))
        else:
            text = f"{san_move}"
            move_label = UI_FONT.render(text, True, (200, 200, 200))
            move_surface.blit(move_label, (110, y_offset - scroll_y))
            y_offset += 30
    
    screen.blit(move_surface, (panel_start_x, move_history_y_start))

def draw_timer_selection(screen):
    """Draws the timer selection screen."""
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))
    
    title = UI_FONT_LARGE.render("Select Time Control", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH / 2, 100)))

    for i, (text, time) in enumerate(TIME_CONTROLS.items()):
        rect = pygame.Rect(WIDTH // 2 - 100, 200 + i * 70, 200, 50)
        TIME_CONTROL_RECTS[text] = rect
        draw_button(screen, text.replace('_', ' '), rect)

def draw_difficulty_selection(screen):
    """Draws the difficulty selection screen."""
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0, 0))
    
    title = UI_FONT_LARGE.render("Select Difficulty", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH / 2, 100)))

    for i, (text, level) in enumerate(DIFFICULTY_LEVELS.items()):
        rect = pygame.Rect(WIDTH // 2 - 100, 200 + i * 70, 200, 50)
        DIFFICULTY_RECTS[text] = rect
        draw_button(screen, text, rect)

def save_pgn(game_state):
    """Saves the game to a PGN file."""
    game = chess.pgn.Game()
    game.headers["Event"] = "Pygame Chess Match"
    game.headers["White"] = "Player"
    game.headers["Black"] = "Stockfish"
    game.headers["Date"] = time.strftime("%Y.%m.%d")
    
    board = chess.Board()
    for move in game_state.board.move_stack:
        board.push(move)
    
    game.add_line(game_state.board.move_stack)

    with open("last_game.pgn", "w") as f:
        print(game, file=f, end="\n\n")
    print("Game saved to last_game.pgn")