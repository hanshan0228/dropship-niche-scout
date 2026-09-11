# Launch Dropship Niche Scout Web Cockpit
$PythonExe = "C:\Users\hanzhe1\AppData\Local\Programs\Python\Python313\python.exe"
$AppScript = Join-Path $PSScriptRoot "web_app.py"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "🚀 Launching Dropship Niche Scout Web Cockpit..." -ForegroundColor Green
Write-Host "🌐 Local URL: http://127.0.0.1:8088" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Cyan

& $PythonExe $AppScript
