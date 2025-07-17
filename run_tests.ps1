# CaseClipSaver - Test Runner
# Run all unit tests

Write-Host "Running CaseClipSaver Tests..." -ForegroundColor Green

# Change to project directory
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Run individual test files
$testFiles = @(
    "tests/test_data_parser.py",
    "tests/test_file_manager.py"
)

$allPassed = $true

foreach ($testFile in $testFiles) {
    if (Test-Path $testFile) {
        Write-Host "`nRunning $testFile..." -ForegroundColor Yellow
        try {
            python -m unittest $testFile.Replace('/', '.').Replace('.py', '') -v
            if ($LASTEXITCODE -ne 0) {
                $allPassed = $false
            }
        } catch {
            Write-Host "Failed to run $testFile" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "Test file not found: $testFile" -ForegroundColor Red
        $allPassed = $false
    }
}

if ($allPassed) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed!" -ForegroundColor Red
}

Write-Host "`nTest run complete." -ForegroundColor Cyan
