# Pygame Chess

A feature-rich, single-player chess game built with Python and Pygame. Play against a configurable Stockfish AI opponent and analyze your games.

![Gameplay Screenshot](https://i.imgur.com/your_screenshot.png) 
*(You can replace this with a real screenshot of your game)*

## Features

- **Play Against AI**: Challenge the powerful Stockfish chess engine.
- **Configurable Difficulty**: Choose from multiple skill levels (Easy, Medium, Hard, Expert) to match your ability.
- **Selectable Time Controls**: Play games with 3, 5, 10, or 30-minute timers.
- **Live Evaluation Bar**: See a real-time analysis of the current position from the engine's perspective.
- **Move History**: A scrollable list of all moves made during the game.
- **PGN Export**: Save your completed games to a `.pgn` file for analysis in other chess software.
- **Multiple Input Methods**: Move pieces using either drag-and-drop or click-to-move.
- **Automatic Setup**: The required chess engine (Stockfish) is downloaded automatically when you first run the game.
- **High-Quality Assets**: Uses SVG-based assets for crisp visuals, with a fallback to generated PNGs if needed.

## How to Run

This project is designed to be run from a local development environment.

### Prerequisites

- Python 3.x
- `pip` for package management

### Setup and Execution

Two run scripts are provided for convenience: `runfile.ps1` for Windows (PowerShell) and `runfile.sh` for macOS and Linux.

**On Windows:**
```powershell
.\runfile.ps1
```

**On macOS/Linux:**
```bash
chmod +x runfile.sh
./runfile.sh
```

When you run the script for the first time, it will:
1. Create a local Python virtual environment (`.venv`).
2. Install all the required Python packages from `requirements.txt`.
3. Download and set up the Stockfish chess engine executable.
4. Download high-quality SVG piece assets.
5. Launch the game.

Subsequent runs will be much faster as they will use the existing environment and assets.

## Project Structure

- `main.py`: The main application entry point, containing the game loop and event handling.
- `engine.py`: Manages the Stockfish chess engine process.
- `game_state.py`: Handles the chess board logic, timers, and move history.
- `ui.py`: Contains all functions related to drawing the game board, pieces, menus, and other UI elements.
- `config.py`: Central configuration for screen dimensions, colors, fonts, and engine settings.
- `runfile.ps1` / `runfile.sh`: Scripts to automate setup and execution.
- `requirements.txt`: A list of all Python dependencies.
- `assets/`: Contains game assets like piece images and sounds.
- `download_assets.py`: A script to download primary SVG piece assets.
- `asset_manager.py`: A fallback script to generate PNG piece assets if the download fails.
