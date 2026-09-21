$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$python = Join-Path $root "backend\venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

Write-Host "Building frontend..."
Push-Location frontend
npm run build
Pop-Location

$hasPyInstaller = (& $python -c "import importlib.util; print(importlib.util.find_spec('PyInstaller') is not None)") -eq "True"
if (-not $hasPyInstaller) {
    Write-Host "Installing PyInstaller..."
    & $python -m pip install pyinstaller
}

Write-Host "Building Windows executable..."
& $python -m PyInstaller --noconfirm --clean --onefile `
    --name IntelligentWritingAssistant `
    --add-data "frontend/dist;frontend_dist" `
    --hidden-import aiosqlite `
    --collect-all uvicorn `
    app_launcher.py

Write-Host "Done: dist\IntelligentWritingAssistant.exe"