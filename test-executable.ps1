# Test script to verify the standalone executable works
# This creates a simple test without requiring the system tray

Write-Host "Testing CaseClipSaver Standalone Executable..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if executable exists
$exePath = ".\dist\CaseClipSaver.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "❌ Executable not found at $exePath" -ForegroundColor Red
    Write-Host "Run .\build.ps1 first to create the executable" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Executable found: $exePath" -ForegroundColor Green

# Get file info
$fileInfo = Get-Item $exePath
Write-Host "📁 File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host "📅 Created: $($fileInfo.CreationTime)" -ForegroundColor Cyan

Write-Host ""
Write-Host "🚀 Starting CaseClipSaver executable..." -ForegroundColor Yellow
Write-Host "   (Look for the clipboard icon in your system tray)" -ForegroundColor Gray

# Start the executable
try {
    Start-Process -FilePath $exePath -NoNewWindow
    Write-Host "✅ Executable started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Test Instructions:" -ForegroundColor Cyan
    Write-Host "1. Look for clipboard icon in system tray" -ForegroundColor White
    Write-Host "2. Copy this test data:" -ForegroundColor White
    Write-Host "   ICM 635658889 - Critical production incident" -ForegroundColor Yellow
    Write-Host "   Support Request Number: 2505160020000588" -ForegroundColor Yellow
    Write-Host "3. Check C:\casedata\ for auto-saved file" -ForegroundColor White
    Write-Host "4. Right-click tray icon for menu options" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 Expected result: 635658889_2505160020000588.txt" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to start executable: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Test completed! CaseClipSaver should now be running." -ForegroundColor Green
