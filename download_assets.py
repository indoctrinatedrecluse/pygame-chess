import os
import requests
import sys

# URL path to the raw SVGs in the lichess-org/lila repository
base_url = "https://raw.githubusercontent.com/lichess-org/lila/master/public/piece/cburnett/"

# Map our internal filenames to the lichess filenames
pieces = {
    'wp': 'wP', 'wn': 'wN', 'wb': 'wB', 'wr': 'wR', 'wq': 'wQ', 'wk': 'wK',
    'bp': 'bP', 'bn': 'bN', 'bb': 'bB', 'br': 'bR', 'bq': 'bQ', 'bk': 'bK',
}

assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'pieces')

if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)

print(f"Downloading high-quality SVG piece assets to {assets_dir}...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

success = True
for local_name, remote_name in pieces.items():
    file_path = os.path.join(assets_dir, f"{local_name}.svg")
    url = f"{base_url}{remote_name}.svg"
    
    if not os.path.exists(file_path):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {local_name}.svg")
        except Exception as e:
            print(f"Failed to download {local_name}.svg: {e}")
            success = False
            # Clean up the partial file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
            break 
    else:
         print(f"{local_name}.svg already exists.")

if not success:
    print("Download process failed or was incomplete. Initiating fallback asset generation...")
    # Return a non-zero exit code so the calling script knows it failed
    sys.exit(1)
else:
    print("Asset setup complete!")
    sys.exit(0)
