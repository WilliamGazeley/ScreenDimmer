<#
    Build script for Screen Dimmer (Windows)
    - Creates a single-file, windowed .exe using PyInstaller
    - Installs dependencies (including pyinstaller) if needed
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Change to the script's directory
Set-Location -Path $PSScriptRoot

# Use python directly (works with GitHub Actions and local environments)
$python = "python"

Write-Host "Using Python launcher: $python"

# Ensure pip is up-to-date
& $python -m pip install --upgrade pip

# Install project requirements (if present)
if (Test-Path ".\requirements.txt") {
    Write-Host "Installing requirements.txt..."
    & $python -m pip install -r requirements.txt
}

# Ensure pyinstaller is available
Write-Host "Installing PyInstaller..."
& $python -m pip install pyinstaller

# Clean previous build artifacts
Write-Host "Cleaning previous build artifacts..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build | Out-Null
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist | Out-Null
Remove-Item -Force -ErrorAction SilentlyContinue *.spec | Out-Null
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__ | Out-Null

$AppName = "ScreenDimmer"
$Entry   = "screen_dimmer.py"

if (-not (Test-Path $Entry)) {
    throw "Entry file '$Entry' not found. Make sure you're running this in the project root."
}

Write-Host "Building $AppName from $Entry ..."
& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name $AppName `
    --hidden-import=tkinter `
    --hidden-import=tkinter.ttk `
    $Entry

$exePath = Join-Path (Resolve-Path ".\\dist") "$AppName.exe"

if (Test-Path $exePath) {
    Write-Host "Build complete:" -ForegroundColor Green
    Write-Host "  $exePath"
} else {
    throw "Build failed - executable not found at $exePath"
}


