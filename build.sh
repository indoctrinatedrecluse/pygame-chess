#!/bin/bash

# This script packages the Pygame Chess application into a single executable for Linux/macOS.

# Ensure PyInstaller is installed
pip install pyinstaller

# --- PyInstaller Command ---
# --name: The name of the final executable
# --onefile: Bundle everything into a single executable file
# --windowed: Prevents a console window from appearing when the game runs
# --add-data: Bundles assets into the executable. The format is "source:destination".
#             On Linux/macOS, the separator is ':'.
#             We are telling PyInstaller to take the 'assets' folder and place it in the root of the bundled app.
#             We do the same for the Stockfish executable.

pyinstaller --name "PygameChess" \
            --onefile \
            --windowed \
            --add-data "assets:assets" \
            --add-data "stockfish:." \
            main.py
