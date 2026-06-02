# Create a virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

# Activate the virtual environment
. .venv/Scripts/Activate.ps1

# Install/update dependencies
pip install -r requirements.txt

# --- Stockfish Engine Setup ---
$stockfishExe = "stockfish.exe"
if (-not (Test-Path $stockfishExe)) {
    Write-Host "Stockfish not found. Attempting to download and set up..."
    # Use a reliable, modern Stockfish link
    $stockfishUrl = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64-avx2.zip"
    $zipFile = "stockfish.zip"
    $extractDir = "stockfish_temp"

    try {
        Write-Host "Downloading Stockfish from $stockfishUrl..."
        Invoke-WebRequest -Uri $stockfishUrl -OutFile $zipFile

        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
        New-Item -ItemType Directory -Path $extractDir

        Write-Host "Extracting archive..."
        Expand-Archive -Path $zipFile -DestinationPath $extractDir -Force

        # Find the executable within the extracted folder (e.g., stockfish/stockfish.exe)
        $exePath = Get-ChildItem -Path $extractDir -Filter "*.exe" -Recurse | Where-Object { $_.Name -like 'stockfish*.exe' } | Select-Object -First 1

        if ($exePath) {
            Write-Host "Found executable at $($exePath.FullName)"
            # Rename and move the executable to the project root
            Move-Item -Path $exePath.FullName -Destination $stockfishExe -Force
            Write-Host "Stockfish setup complete."
        } else {
            Write-Host "Could not find the Stockfish executable in the archive."
        }

    } catch {
        Write-Host "Failed to download or set up Stockfish. Please install it manually."
        Write-Host $_.Exception.Message
    } finally {
        # Clean up the zip and extracted folder
        if (Test-Path $zipFile) { Remove-Item $zipFile -Force }
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
    }
} else {
    Write-Host "Stockfish executable found."
}


# --- Asset Management ---
New-Item -ItemType Directory -Force -Path "assets/pieces" | Out-Null
$svgCount = (Get-ChildItem "assets/pieces" -Filter "*.svg" | Measure-Object).Count
if ($svgCount -lt 12) {
    Write-Host "Primary SVG assets not fully present. Attempting to download..."
    python download_assets.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "SVG download failed. Generating fallback PNG assets..."
        python asset_manager.py
    }
} else {
    Write-Host "Primary SVG assets found."
}

# Run the main application
python main.py