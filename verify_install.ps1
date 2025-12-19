#!/usr/bin/env pwsh
# Visual AutoView Installation Verification Script
# Run this after installation to verify everything is working correctly

param(
    [Parameter(Mandatory = $false)]
    [string]$HAUrl = "http://localhost:8123",
    
    [Parameter(Mandatory = $false)]
    [string]$Token
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($message) { Write-ColorOutput Green "✓ $message" }
function Write-Info($message) { Write-ColorOutput Cyan "ℹ $message" }
function Write-Warning($message) { Write-ColorOutput Yellow "⚠ $message" }
function Write-Error($message) { Write-ColorOutput Red "✗ $message" }

Write-Info "Visual AutoView Installation Verification"
Write-Info "=========================================`n"

# Check if Home Assistant is accessible
Write-Info "Checking Home Assistant connectivity..."
try {
    $response = Invoke-WebRequest -Uri "$HAUrl/api/" -Method GET -TimeoutSec 5 -SkipCertificateCheck -ErrorAction Stop
    Write-Success "Home Assistant is accessible at $HAUrl"
}
catch {
    Write-Error "Cannot reach Home Assistant at $HAUrl"
    Write-Warning "Please ensure Home Assistant is running and the URL is correct"
    exit 1
}

# Get token if not provided
if (-not $Token) {
    Write-Info "`nTo verify API access, we need a long-lived access token."
    Write-Info "Create one in Home Assistant: Profile → Long-Lived Access Tokens"
    $Token = Read-Host "`nEnter your Home Assistant long-lived access token (optional, press Enter to skip)"
}

if ($Token) {
    Write-Info "`nVerifying Visual AutoView API endpoints..."
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type"  = "application/json"
    }
    
    $endpoints = @(
        "/api/visualautoview/automations",
        "/api/visualautoview/health",
        "/api/visualautoview/stats"
    )
    
    $successCount = 0
    foreach ($endpoint in $endpoints) {
        try {
            $url = "$HAUrl$endpoint"
            $response = Invoke-RestMethod -Uri $url -Headers $headers -Method GET -TimeoutSec 10 -SkipCertificateCheck
            Write-Success "Endpoint working: $endpoint"
            $successCount++
        }
        catch {
            Write-Warning "Endpoint failed: $endpoint"
            Write-Warning "  Error: $($_.Exception.Message)"
        }
    }
    
    Write-Info "`nEndpoint Test Results: $successCount/$($endpoints.Count) passed"
    
    if ($successCount -eq $endpoints.Count) {
        Write-Success "`n🎉 All API endpoints are working correctly!"
    }
    elseif ($successCount -gt 0) {
        Write-Warning "`n⚠️  Some endpoints are not responding. Check Home Assistant logs."
    }
    else {
        Write-Error "`n❌ API endpoints are not accessible. Integration may not be loaded."
        Write-Info "Try:"
        Write-Info "  1. Restart Home Assistant"
        Write-Info "  2. Check logs for errors"
        Write-Info "  3. Verify integration is enabled in Configuration → Integrations"
    }
}
else {
    Write-Warning "`nSkipping API verification (no token provided)"
}

# Check file installation
Write-Info "`nChecking file installation..."
$commonPaths = @(
    "$env:HOME/.homeassistant/custom_components/visualautoview",
    "$env:USERPROFILE/.homeassistant/custom_components/visualautoview",
    "/config/custom_components/visualautoview"
)

$found = $false
foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        if (Test-Path (Join-Path $path "manifest.json")) {
            $manifest = Get-Content (Join-Path $path "manifest.json") | ConvertFrom-Json
            Write-Success "Found installation at: $path"
            Write-Success "Version: $($manifest.version)"
            Write-Success "Domain: $($manifest.domain)"
            $found = $true
            break
        }
    }
}

if (-not $found) {
    Write-Warning "Could not locate installation in common directories"
    Write-Info "Installation may be in a custom location"
}

Write-Info "`n========================================="
Write-Info "Verification complete!"
Write-Info "`nNext Steps:"
Write-Info "  1. Open Home Assistant: $HAUrl"
Write-Info "  2. Go to Configuration → Integrations"
Write-Info "  3. Verify 'Visual AutoView' is listed and active"
Write-Info "  4. Check logs for any errors"
Write-Info "`nDocumentation: https://github.com/braczek/HAVisualAutomationViewer"
