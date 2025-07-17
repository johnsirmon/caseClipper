# Build script for CaseClipSaver
# Run this script to create a standalone executable

Write-Host "Building CaseClipSaver..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.11+ and try again." -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install PyInstaller if not already installed
Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow

# Clean previous build
if (Test-Path "build") {
    Write-Host "Cleaning previous build..." -ForegroundColor Gray
    Remove-Item "build" -Recurse -Force
}
if (Test-Path "dist") {
    Write-Host "Cleaning previous dist..." -ForegroundColor Gray
    Remove-Item "dist" -Recurse -Force
}

$buildCmd = "pyinstaller CaseClipSaver.spec"

try {
    Invoke-Expression $buildCmd
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Executable location: dist/CaseClipSaver.exe" -ForegroundColor Cyan
} catch {
    Write-Host "Build failed. Error: $_" -ForegroundColor Red
    exit 1
}

# Create output directory if it doesn't exist
$outputDir = "C:\casedata"
if (-not (Test-Path $outputDir)) {
    Write-Host "Creating output directory: $outputDir" -ForegroundColor Yellow
    New-Item -Path $outputDir -ItemType Directory -Force
}

Write-Host "`nBuild complete! You can now run CaseClipSaver.exe from the dist folder." -ForegroundColor Green
Write-Host "The application will save case data to: $outputDir" -ForegroundColor Cyan
