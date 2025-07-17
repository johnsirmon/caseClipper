# CaseClipSaver Setup Script
# Installs dependencies and sets up the application following best practices

param(
    [switch]$Dev,
    [switch]$Build,
    [switch]$Test,
    [switch]$VirtualEnv = $true
)

Write-Host "CaseClipSaver Setup (Best Practices)" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found Python: $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.11+
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($matches) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "⚠ Warning: Python 3.11+ recommended. Current version: $pythonVersion" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Recommend using virtual environment
if ($VirtualEnv) {
    Write-Host "`nSetting up virtual environment (recommended)..." -ForegroundColor Yellow
    if ($Dev) {
        .\setup-venv.ps1 -Dev
    } else {
        .\setup-venv.ps1
    }
    Write-Host "✓ Virtual environment setup complete" -ForegroundColor Green
    Write-Host "Note: Activate with .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    exit 0
}

# Legacy global installation (not recommended)
Write-Host "`n⚠ WARNING: Installing globally (not recommended)" -ForegroundColor Yellow
Write-Host "Consider using: .\setup.ps1 -VirtualEnv for better isolation" -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Install requirements
Write-Host "`nInstalling requirements..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ Requirements installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install requirements!" -ForegroundColor Red
    exit 1
}

# Create icon
Write-Host "`nCreating application icon..." -ForegroundColor Yellow
try {
    python src/create_icon.py
    Write-Host "✓ Icon created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Failed to create icon, will use default" -ForegroundColor Yellow
}

# Create output directory
$outputDir = "C:\casedata"
Write-Host "`nSetting up output directory..." -ForegroundColor Yellow
try {
    if (-not (Test-Path $outputDir)) {
        New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
        Write-Host "✓ Created output directory: $outputDir" -ForegroundColor Green
    } else {
        Write-Host "✓ Output directory already exists: $outputDir" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Could not create output directory. Will be created at runtime." -ForegroundColor Yellow
}

# Run tests if requested
if ($Test) {
    Write-Host "`nRunning tests..." -ForegroundColor Yellow
    try {
        .\run_tests.ps1
    } catch {
        Write-Host "⚠ Some tests failed, but setup can continue" -ForegroundColor Yellow
    }
}

# Build executable if requested
if ($Build) {
    Write-Host "`nBuilding executable..." -ForegroundColor Yellow
    try {
        .\build.ps1
    } catch {
        Write-Host "✗ Build failed!" -ForegroundColor Red
        exit 1
    }
}

# Development setup
if ($Dev) {
    Write-Host "`nInstalling development dependencies..." -ForegroundColor Yellow
    try {
        pip install pytest pytest-cov black flake8 mypy
        Write-Host "✓ Development dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Failed to install development dependencies" -ForegroundColor Yellow
    }
}

# Final instructions
Write-Host "`nSetup Complete!" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
Write-Host ""
Write-Host "To run CaseClipSaver:" -ForegroundColor Cyan
Write-Host "  python src/main.py" -ForegroundColor White
Write-Host ""
Write-Host "To build executable:" -ForegroundColor Cyan
Write-Host "  .\build.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run tests:" -ForegroundColor Cyan
Write-Host "  .\run_tests.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Output directory: $outputDir" -ForegroundColor Cyan
Write-Host "The application will save case files there automatically." -ForegroundColor Gray
