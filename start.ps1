# Finance Chatbot Startup Script
# This script starts the backend server and opens the frontend in your default browser

Write-Host "Starting Personal Finance Chatbot..." -ForegroundColor Green
Write-Host ""

# Open the frontend in default browser
Write-Host "Opening frontend at http://localhost:8000" -ForegroundColor Cyan
Start-Process "http://localhost:8000"

# Wait a moment for browser to open
Start-Sleep -Seconds 1

# Start the backend server
Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
