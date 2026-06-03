#!/bin/bash

# This script is for CI/CD environments. It sets up all necessary
# dependencies and assets but does NOT run the main application.

echo "--- CI/CD Setup Started ---"

# --- Stockfish Engine Setup ---
STOCKFISH_EXE="stockfish"
if [ ! -f "$STOCKFISH_EXE" ]; then
    echo "Stockfish not found. Attempting to download and set up..."
    STOCKFISH_URL="https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64-avx2.tar"
    ARCHIVE_FILE="stockfish.tar"
    EXTRACT_DIR="stockfish_temp"

    echo "Downloading Stockfish from $STOCKFISH_URL..."
    if curl -L "$STOCKFISH_URL" -o "$ARCHIVE_FILE"; then
        rm -rf "$EXTRACT_DIR"
        mkdir "$EXTRACT_DIR"
        echo "Extracting archive..."
        if tar -xf "$ARCHIVE_FILE" -C "$EXTRACT_DIR"; then
            find "$EXTRACT_DIR" -type f -name 'stockfish*' -exec chmod +x {} \; -exec mv {} "./$STOCKFISH_EXE" \;
            if [ -f "$STOCKFISH_EXE" ]; then
                echo "Stockfish setup complete."
            else
                echo "Could not find the Stockfish executable in the archive."
                exit 1
            fi
        else
            echo "Failed to extract Stockfish."
            exit 1
        fi
    else
        echo "Failed to download Stockfish."
        exit 1
    fi
    rm -f "$ARCHIVE_FILE"
    rm -rf "$EXTRACT_DIR"
else
    echo "Stockfish executable found."
fi

# --- Asset Management ---
mkdir -p assets/pieces
PNG_COUNT=$(ls -1 assets/pieces/*.png 2>/dev/null | wc -l)
if [ "$PNG_COUNT" -lt 12 ]; then
    echo "Primary PNG assets not fully present. Attempting to download..."
    python download_assets.py
    if [ $? -ne 0 ]; then
        echo "PNG download failed. Generating fallback PNG assets..."
        python asset_manager.py
    fi
else
    echo "Primary PNG assets found."
fi

echo "--- CI/CD Setup Complete ---"
