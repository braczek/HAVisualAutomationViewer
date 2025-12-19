# Restart Home Assistant via REST API
# This requires a long-lived access token

$haUrl = "http://192.168.1.7:8123"
$token = Read-Host "Enter your Home Assistant Long-Lived Access Token" -MaskInput

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

Write-Host "Restarting Home Assistant at $haUrl..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$haUrl/api/services/homeassistant/restart" -Method Post -Headers $headers -Body "{}"
    Write-Host "✅ Home Assistant restart initiated successfully!" -ForegroundColor Green
    Write-Host "⏳ Please wait about 30-60 seconds for Home Assistant to restart..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After restart, access the updated visualization at:" -ForegroundColor White
    Write-Host "http://192.168.1.7:8123/local/visualautoview/index.html" -ForegroundColor Cyan
}
catch {
    Write-Host "❌ Error restarting Home Assistant: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Restart manually from Home Assistant UI:" -ForegroundColor Yellow
    Write-Host "1. Go to Settings > System > Restart" -ForegroundColor White
    Write-Host "2. Or use Developer Tools > YAML > Restart" -ForegroundColor White
}
