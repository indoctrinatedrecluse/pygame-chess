# Pygame Chess

A chess game built with Python, featuring a Pygame UI, `python-chess` for game logic, and Stockfish as the opponent engine.

## Features

*   **Play Against AI**: Play a full game against the Stockfish engine.
*   **Graphical UI**: A clean and simple chessboard with drag-and-drop controls.
*   **Move Highlights**: Visual feedback for selected pieces, legal moves, captures, and checks.
*   **Game State Management**: Start menu, game over screens, and pawn promotion dialogs.
*   **Timers & Move Counter**: Timed games and a 50-move rule counter.
*   **Automated Asset Management**: Automatically downloads high-quality SVG piece images, with a built-in fallback generator for offline use.

## Technology Stack

*   **UI**: [Pygame-CE](https://pyga.me/)
*   **Game Logic**: [python-chess](https://github.com/niklasf/python-chess)
*   **Engine**: [Stockfish](https://stockfishchess.org/)
*   **Dependencies**: `pygame-svg`, `requests`, `stockfish`

## Setup and Run

### 1. Download Stockfish

Before running the game, you must download the Stockfish chess engine.

1.  Go to the [Stockfish download page](https://stockfishchess.org/download/).
2.  Download the appropriate version for your operating system (e.g., Windows x64, macOS Apple Silicon).
3.  Extract the zip file.
4.  Place the Stockfish executable (e.g., `stockfish.exe` on Windows) into the root directory of this project, or update the `STOCKFISH_PATH` in `config.py` to point to its location.

### 2. Run the Game

The project includes convenient scripts to set up the environment and run the application.

#### On Windows

Open a PowerShell terminal and run:

```powershell
.\runfile.ps1
```

#### On macOS / Linux

Open a terminal and run:

```bash
chmod +x runfile.sh
./runfile.sh
```

These scripts will:
1.  Create a Python virtual environment (`.venv`).
2.  Install all the required dependencies from `requirements.txt`.
3.  Check for and download the required chess piece assets.
4.  Launch the game.
