#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# --- Asset Management ---
# Check if we have a full set of SVG assets
SVG_COUNT=0
if [ -d "assets/pieces" ]; then
    SVG_COUNT=$(ls -1 assets/pieces/*.svg 2>/dev/null | wc -l)
fi

if [ "$SVG_COUNT" -lt 12 ]; then
    echo "Primary SVG assets not fully present. Attempting to download..."
    python download_assets.py

    # If download fails, check for/generate PNG fallbacks
    if [ $? -ne 0 ]; then
        PNG_COUNT=$(ls -1 assets/pieces/*.png 2>/dev/null | wc -l)
        if [ "$PNG_COUNT" -lt 12 ]; then
            echo "SVG download failed and fallbacks missing. Generating PNG fallbacks..."
            python asset_manager.py
        else
            echo "SVG download failed, but fallback PNGs are present."
        fi
    fi
else
    echo "Primary SVG assets found."
fi

# Run the main application
python main.py
