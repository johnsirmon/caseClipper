# Virtual Environment Setup for CaseClipSaver
# This script creates and configures a proper Python virtual environment

param(
    [switch]$Force,
    [switch]$Dev
)

Write-Host "Setting up Python Virtual Environment for CaseClipSaver" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green

# Get project directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Check if virtual environment already exists
$venvPath = ".\.venv"
if (Test-Path $venvPath) {
    if ($Force) {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item $venvPath -Recurse -Force
    } else {
        Write-Host "Virtual environment already exists at $venvPath" -ForegroundColor Yellow
        Write-Host "Use -Force to recreate it" -ForegroundColor Gray
        $response = Read-Host "Do you want to continue with the existing environment? (y/n)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Host "Aborted by user" -ForegroundColor Red
            exit 1
        }
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    try {
        python -m venv .venv
        Write-Host "✓ Virtual environment created successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to create virtual environment!" -ForegroundColor Red
        Write-Host "Make sure Python 3.11+ is installed and in your PATH" -ForegroundColor Yellow
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to find activation script!" -ForegroundColor Red
    exit 1
}

# Upgrade pip in virtual environment
Write-Host "Upgrading pip..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    Write-Host "✓ pip upgraded successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Failed to upgrade pip, continuing..." -ForegroundColor Yellow
}

# Install requirements
Write-Host "Installing production requirements..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ Production requirements installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install production requirements!" -ForegroundColor Red
    exit 1
}

# Install development requirements if requested
if ($Dev) {
    Write-Host "Installing development requirements..." -ForegroundColor Yellow
    try {
        pip install -r requirements-dev.txt
        Write-Host "✓ Development requirements installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Failed to install some development requirements" -ForegroundColor Yellow
    }
}

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
try {
    python -c "import pyperclip, pystray, PIL; print('✓ Core dependencies verified')"
    Write-Host "✓ All core dependencies are working" -ForegroundColor Green
} catch {
    Write-Host "✗ Some dependencies may not be properly installed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Virtual Environment Setup Complete!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the environment manually:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate when done:" -ForegroundColor Cyan
Write-Host "  deactivate" -ForegroundColor White
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  python src\main.py" -ForegroundColor White
Write-Host ""

if ($Dev) {
    Write-Host "Development tools available:" -ForegroundColor Cyan
    Write-Host "  pytest          - Run tests" -ForegroundColor White
    Write-Host "  black .         - Format code" -ForegroundColor White
    Write-Host "  flake8 src      - Lint code" -ForegroundColor White
    Write-Host "  mypy src        - Type checking" -ForegroundColor White
    Write-Host ""
}
