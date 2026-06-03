import os
import requests
import sys

# Using highly reliable PNG URLs from chess.com's neo piece set.
base_url = "https://images.chesscomfiles.com/chess-themes/pieces/neo/150/"

pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']

assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'pieces')
os.makedirs(assets_dir, exist_ok=True)

print(f"Downloading high-quality PNG piece assets to {assets_dir}...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

success = True
for piece in pieces:
    file_path = os.path.join(assets_dir, f"{piece}.png")
    url = f"{base_url}{piece}.png"
    
    if not os.path.exists(file_path):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {piece}.png")
        except Exception as e:
            print(f"Failed to download {piece}.png: {e}")
            success = False
            if os.path.exists(file_path):
                os.remove(file_path)
            break 
    else:
         print(f"{piece}.png already exists.")

if not success:
    print("\nDownload process failed. Initiating fallback asset generation...")
    sys.exit(1)
else:
    print("\nAsset setup complete!")
    sys.exit(0)
