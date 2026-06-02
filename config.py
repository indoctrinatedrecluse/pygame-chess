import pygame
import chess
import os
import sys

# Screen dimensions
WIDTH = 800
HEIGHT = 600
BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
LIGHT_SQUARE = pygame.Color(240, 217, 181)
DARK_SQUARE = pygame.Color(181, 136, 99)
BG_COLOR = pygame.Color("#404040")

# Highlight Colors
HIGHLIGHT_SELECTED = pygame.Color(20, 85, 30, 100)
HIGHLIGHT_LEGAL_MOVE = pygame.Color(20, 85, 30, 100)
HIGHLIGHT_CAPTURE = pygame.Color(200, 50, 50, 150)
HIGHLIGHT_LAST_MOVE = pygame.Color(155, 199, 0, 100)
HIGHLIGHT_INVALID_MOVE = pygame.Color(255, 0, 0, 150)
HIGHLIGHT_CHECK = pygame.Color(255, 0, 0, 120)

# Time Controls (in seconds)
TIME_CONTROLS = {
    '3_MIN': 180,
    '5_MIN': 300,
    '10_MIN': 600,
    '30_MIN': 1800
}
DEFAULT_TIME = TIME_CONTROLS['10_MIN']

# UI Fonts
UI_FONT_SIZE = 24
UI_FONT_LARGE_SIZE = 50
UI_FONT = None
UI_FONT_LARGE = None

# Paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
PIECES_DIR = os.path.join(ASSETS_DIR, 'pieces')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# --- Engine Settings ---
if sys.platform == "win32":
    STOCKFISH_EXECUTABLE = "stockfish.exe"
else:
    STOCKFISH_EXECUTABLE = "stockfish"

STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), STOCKFISH_EXECUTABLE)

# Difficulty levels (0-20).
DIFFICULTY_LEVELS = {
    'Easy': 1,
    'Medium': 5,
    'Hard': 10,
    'Expert': 20
}
DEFAULT_DIFFICULTY = DIFFICULTY_LEVELS['Easy']

AI_PLAYS_AS = chess.BLACK