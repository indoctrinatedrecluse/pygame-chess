# Create a virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

# Activate the virtual environment
. .venv/Scripts/Activate.ps1

# Install/update dependencies
pip install -r requirements.txt

# --- Asset Management ---
# Check if we have a full set of SVG assets
$svgCount = 0
if (Test-Path "assets/pieces") {
    $svgCount = (Get-ChildItem "assets/pieces" -Filter "*.svg" | Measure-Object).Count
}

if ($svgCount -lt 12) {
    Write-Host "Primary SVG assets not fully present. Attempting to download..."
    python download_assets.py

    # If download fails, check for/generate PNG fallbacks
    if ($LASTEXITCODE -ne 0) {
        $pngCount = (Get-ChildItem "assets/pieces" -Filter "*.png" | Measure-Object).Count
        if ($pngCount -lt 12) {
            Write-Host "SVG download failed and fallbacks missing. Generating PNG fallbacks..."
            python asset_manager.py
        } else {
            Write-Host "SVG download failed, but fallback PNGs are present."
        }
    }
} else {
    Write-Host "Primary SVG assets found."
}

# Run the main application
python main.py
