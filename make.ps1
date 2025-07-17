# Make-like script for CaseClipSaver development tasks
# Usage: .\make.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "CaseClipSaver Development Commands" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Setup Commands:" -ForegroundColor Cyan
    Write-Host "  setup         - Set up virtual environment and install dependencies" -ForegroundColor White
    Write-Host "  setup-dev     - Set up development environment with dev dependencies" -ForegroundColor White
    Write-Host "  clean         - Clean build artifacts and cache files" -ForegroundColor White
    Write-Host ""
    Write-Host "Development Commands:" -ForegroundColor Cyan
    Write-Host "  format        - Format code with black and isort" -ForegroundColor White
    Write-Host "  lint          - Run linting with flake8" -ForegroundColor White
    Write-Host "  type-check    - Run type checking with mypy" -ForegroundColor White
    Write-Host "  test          - Run all tests" -ForegroundColor White
    Write-Host "  test-cov      - Run tests with coverage report" -ForegroundColor White
    Write-Host "  security      - Run security checks" -ForegroundColor White
    Write-Host ""
    Write-Host "Build Commands:" -ForegroundColor Cyan
    Write-Host "  build         - Build standalone executable" -ForegroundColor White
    Write-Host "  install       - Install package in development mode" -ForegroundColor White
    Write-Host ""
    Write-Host "Run Commands:" -ForegroundColor Cyan
    Write-Host "  run           - Run the application" -ForegroundColor White
    Write-Host "  demo          - Run with demo/sample data" -ForegroundColor White
    Write-Host "  test-exe      - Test standalone executable" -ForegroundColor White
    Write-Host ""
    Write-Host "Quality Commands:" -ForegroundColor Cyan
    Write-Host "  check-all     - Run all quality checks (format, lint, type-check, test)" -ForegroundColor White
    Write-Host "  pre-commit    - Run pre-commit checks" -ForegroundColor White
}

function Invoke-Setup {
    Write-Host "Setting up development environment..." -ForegroundColor Green
    .\setup-venv.ps1
}

function Invoke-SetupDev {
    Write-Host "Setting up development environment with dev dependencies..." -ForegroundColor Green
    .\setup-venv.ps1 -Dev
}

function Invoke-Clean {
    Write-Host "Cleaning build artifacts and cache files..." -ForegroundColor Yellow
    
    $itemsToRemove = @(
        "__pycache__",
        "*.pyc",
        "*.pyo", 
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "build",
        "dist",
        "*.egg-info",
        ".mypy_cache",
        ".tox"
    )
    
    foreach ($item in $itemsToRemove) {
        Get-ChildItem -Path . -Recurse -Name $item | ForEach-Object {
            $fullPath = Join-Path (Get-Location) $_
            if (Test-Path $fullPath) {
                Write-Host "Removing: $_" -ForegroundColor Gray
                Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
    
    Write-Host "✓ Cleanup complete" -ForegroundColor Green
}

function Invoke-Format {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    
    Write-Host "Running isort..." -ForegroundColor Gray
    python -m isort src tests
    
    Write-Host "Running black..." -ForegroundColor Gray
    python -m black src tests
    
    Write-Host "✓ Code formatting complete" -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host "Running linting..." -ForegroundColor Yellow
    python -m flake8 src tests
    Write-Host "✓ Linting complete" -ForegroundColor Green
}

function Invoke-TypeCheck {
    Write-Host "Running type checking..." -ForegroundColor Yellow
    python -m mypy src
    Write-Host "✓ Type checking complete" -ForegroundColor Green
}

function Invoke-Test {
    Write-Host "Running tests..." -ForegroundColor Yellow
    python -m pytest tests/ -v
}

function Invoke-TestCoverage {
    Write-Host "Running tests with coverage..." -ForegroundColor Yellow
    python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
    Write-Host "Coverage report generated in htmlcov/" -ForegroundColor Cyan
}

function Invoke-Security {
    Write-Host "Running security checks..." -ForegroundColor Yellow
    
    Write-Host "Running bandit..." -ForegroundColor Gray
    python -m bandit -r src/
    
    Write-Host "Running safety..." -ForegroundColor Gray
    python -m safety check
    
    Write-Host "✓ Security checks complete" -ForegroundColor Green
}

function Invoke-Build {
    Write-Host "Building standalone executable..." -ForegroundColor Yellow
    .\build.ps1
}

function Invoke-Install {
    Write-Host "Installing package in development mode..." -ForegroundColor Yellow
    pip install -e .
    Write-Host "✓ Package installed in development mode" -ForegroundColor Green
}

function Invoke-Run {
    Write-Host "Running CaseClipSaver..." -ForegroundColor Green
    python src\main.py
}

function Invoke-Demo {
    Write-Host "Running CaseClipSaver with demo instructions..." -ForegroundColor Green
    Write-Host "Demo data is available in sample_data.txt" -ForegroundColor Cyan
    Write-Host "Copy any of the valid test cases to test the application" -ForegroundColor Cyan
    python src\main.py
}

function Invoke-TestExecutable {
    Write-Host "Testing standalone executable..." -ForegroundColor Yellow
    .\test-executable.ps1
}

function Invoke-CheckAll {
    Write-Host "Running all quality checks..." -ForegroundColor Green
    
    $checks = @(
        { Invoke-Format },
        { Invoke-Lint },
        { Invoke-TypeCheck },
        { Invoke-Test }
    )
    
    $failed = $false
    foreach ($check in $checks) {
        try {
            & $check
        } catch {
            Write-Host "✗ Check failed: $_" -ForegroundColor Red
            $failed = $true
        }
    }
    
    if (-not $failed) {
        Write-Host "✓ All quality checks passed!" -ForegroundColor Green
    } else {
        Write-Host "✗ Some quality checks failed!" -ForegroundColor Red
        exit 1
    }
}

function Invoke-PreCommit {
    Write-Host "Running pre-commit checks..." -ForegroundColor Yellow
    
    # Run quick checks that should pass before committing
    Invoke-Format
    Invoke-Lint
    Invoke-TypeCheck
    python -m pytest tests/ -x  # Stop on first failure
    
    Write-Host "✓ Pre-commit checks complete" -ForegroundColor Green
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Invoke-Setup }
    "setup-dev" { Invoke-SetupDev }
    "clean" { Invoke-Clean }
    "format" { Invoke-Format }
    "lint" { Invoke-Lint }
    "type-check" { Invoke-TypeCheck }
    "test" { Invoke-Test }
    "test-cov" { Invoke-TestCoverage }
    "security" { Invoke-Security }
    "build" { Invoke-Build }
    "install" { Invoke-Install }
    "run" { Invoke-Run }
    "demo" { Invoke-Demo }
    "test-exe" { Invoke-TestExecutable }
    "check-all" { Invoke-CheckAll }
    "pre-commit" { Invoke-PreCommit }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\make.ps1 help' to see available commands" -ForegroundColor Yellow
        exit 1
    }
}
