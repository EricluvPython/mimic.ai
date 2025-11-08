# Test Visualizations - Quick Run Script
# This script runs the visualization test and opens the results in your browser

Write-Host "🎨 Mimic.AI Visualization Test" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if server is running
Write-Host "Checking if server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Server is running!" -ForegroundColor Green
} catch {
    Write-Host "❌ Server is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start the server in another terminal:" -ForegroundColor Yellow
    Write-Host "  python -m app.main" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Running visualization tests..." -ForegroundColor Yellow
Write-Host ""

# Run the test script
python test_visualizations.py

# Check if successful
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Visualizations generated successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Open the index page in default browser
    $indexPath = "visualizations_output\index.html"
    if (Test-Path $indexPath) {
        Write-Host "🌐 Opening visualizations in your browser..." -ForegroundColor Cyan
        Start-Process $indexPath
    }
} else {
    Write-Host ""
    Write-Host "❌ Test script failed!" -ForegroundColor Red
}
