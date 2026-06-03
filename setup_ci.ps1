# This script is for CI/CD environments. It sets up all necessary
# dependencies and assets but does NOT run the main application.

Write-Host "--- CI/CD Setup Started ---"

# --- Stockfish Engine Setup ---
$stockfishExe = "stockfish.exe"
if (-not (Test-Path $stockfishExe)) {
    Write-Host "Stockfish not found. Attempting to download and set up..."
    $stockfishUrl = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64-avx2.zip"
    $zipFile = "stockfish.zip"
    $extractDir = "stockfish_temp"

    try {
        Write-Host "Downloading Stockfish from $stockfishUrl..."
        Invoke-WebRequest -Uri $stockfishUrl -OutFile $zipFile
        Write-Host "Extracting archive..."
        Expand-Archive -Path $zipFile -DestinationPath $extractDir -Force
        $exePath = Get-ChildItem -Path $extractDir -Filter "*.exe" -Recurse | Where-Object { $_.Name -like 'stockfish*.exe' } | Select-Object -First 1
        if ($exePath) {
            Move-Item -Path $exePath.FullName -Destination $stockfishExe -Force
            Write-Host "Stockfish setup complete."
        } else {
            Write-Host "Could not find the Stockfish executable in the archive."
            exit 1
        }
    } catch {
        Write-Host "Failed to download or set up Stockfish."
        Write-Host $_.Exception.Message
        exit 1
    } finally {
        if (Test-Path $zipFile) { Remove-Item $zipFile -Force }
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
    }
} else {
    Write-Host "Stockfish executable found."
}

# --- Asset Management ---
New-Item -ItemType Directory -Force -Path "assets/pieces" | Out-Null
$pngCount = (Get-ChildItem "assets/pieces" -Filter "*.png" | Measure-Object).Count
if ($pngCount -lt 12) {
    Write-Host "Primary PNG assets not fully present. Attempting to download..."
    python download_assets.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PNG download failed. Generating fallback PNG assets..."
        python asset_manager.py
    }
} else {
    Write-Host "Primary PNG assets found."
}

Write-Host "--- CI/CD Setup Complete ---"
