#!/usr/bin/env pwsh
# Visual AutoView Installation Script for Home Assistant
# This script automates the installation process for Windows, macOS, and Linux

param(
    [Parameter(Mandatory = $false)]
    [string]$HAConfigPath,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipRestart,
    
    [Parameter(Mandatory = $false)]
    [switch]$DevMode
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($message) {
    Write-ColorOutput Green "✓ $message"
}

function Write-Info($message) {
    Write-ColorOutput Cyan "ℹ $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "⚠ $message"
}

function Write-Error($message) {
    Write-ColorOutput Red "✗ $message"
}

Write-Info "Visual AutoView Installation Script"
Write-Info "====================================`n"

# Detect Home Assistant config directory
if (-not $HAConfigPath) {
    Write-Info "Detecting Home Assistant configuration directory..."
    
    $possiblePaths = @(
        "$env:HOME/.homeassistant",
        "$env:USERPROFILE/.homeassistant",
        "$env:HOME/homeassistant",
        "$env:USERPROFILE/homeassistant",
        "/config",  # Docker/HAOS
        "C:\ProgramData\HomeAssistant",
        "$env:APPDATA\HomeAssistant"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            if (Test-Path (Join-Path $path "configuration.yaml")) {
                $HAConfigPath = $path
                Write-Success "Found Home Assistant at: $HAConfigPath"
                break
            }
        }
    }
    
    if (-not $HAConfigPath) {
        Write-Error "Could not auto-detect Home Assistant directory."
        $HAConfigPath = Read-Host "Please enter the full path to your Home Assistant config directory"
        
        if (-not (Test-Path $HAConfigPath)) {
            Write-Error "Path does not exist: $HAConfigPath"
            exit 1
        }
    }
}

# Verify Home Assistant directory
if (-not (Test-Path (Join-Path $HAConfigPath "configuration.yaml"))) {
    Write-Error "Invalid Home Assistant directory (configuration.yaml not found)"
    exit 1
}

Write-Success "Using Home Assistant directory: $HAConfigPath`n"

# Create custom_components directory if it doesn't exist
$customComponentsPath = Join-Path $HAConfigPath "custom_components"
if (-not (Test-Path $customComponentsPath)) {
    Write-Info "Creating custom_components directory..."
    New-Item -ItemType Directory -Path $customComponentsPath | Out-Null
    Write-Success "Created custom_components directory"
}

# Copy integration files
$sourcePath = Join-Path $PSScriptRoot "custom_components\visualautoview"
$destPath = Join-Path $customComponentsPath "visualautoview"

Write-Info "Installing Visual AutoView integration..."

if (Test-Path $destPath) {
    Write-Warning "Visual AutoView is already installed. Updating..."
    Remove-Item -Path $destPath -Recurse -Force
}

Copy-Item -Path $sourcePath -Destination $destPath -Recurse
Write-Success "Integration files copied successfully"

# Verify installation
$manifestPath = Join-Path $destPath "manifest.json"
if (Test-Path $manifestPath) {
    $manifest = Get-Content $manifestPath | ConvertFrom-Json
    Write-Success "Installed Visual AutoView v$($manifest.version)"
}
else {
    Write-Error "Installation verification failed - manifest.json not found"
    exit 1
}

# Create www directory for frontend if needed
$wwwPath = Join-Path $HAConfigPath "www"
if (-not (Test-Path $wwwPath)) {
    New-Item -ItemType Directory -Path $wwwPath | Out-Null
    Write-Success "Created www directory"
}

# Build and install frontend if in dev mode
if ($DevMode) {
    Write-Info "`nBuilding frontend..."
    $frontendPath = Join-Path $PSScriptRoot "frontend"
    
    if (Test-Path $frontendPath) {
        Push-Location $frontendPath
        
        Write-Info "Installing frontend dependencies..."
        npm install
        
        Write-Info "Building frontend..."
        npm run build
        
        # Copy built frontend to www directory
        $distPath = Join-Path $frontendPath "dist"
        $frontendDestPath = Join-Path $wwwPath "visualautoview"
        
        if (Test-Path $distPath) {
            if (Test-Path $frontendDestPath) {
                Remove-Item -Path $frontendDestPath -Recurse -Force
            }
            Copy-Item -Path $distPath -Destination $frontendDestPath -Recurse
            Write-Success "Frontend installed to www/visualautoview"
        }
        
        Pop-Location
    }
}

Write-Success "`nInstallation completed successfully!`n"

Write-Info "========================================="
Write-Info "You can verify the installation by running:"
Write-Info "  .\verify_install.ps1"
Write-Info "=========================================`n"

# Next steps
Write-Info "Next Steps:"
Write-Info "==========="
Write-Info "1. Restart Home Assistant"

if (-not $SkipRestart) {
    $restart = Read-Host "Would you like to restart Home Assistant now? (y/N)"
    if ($restart -eq "y" -or $restart -eq "Y") {
        Write-Info "Restarting Home Assistant..."
        
        # Try to restart via Home Assistant CLI
        if (Get-Command ha -ErrorAction SilentlyContinue) {
            ha core restart
            Write-Success "Restart command sent"
        }
        else {
            Write-Warning "Home Assistant CLI not found. Please restart manually."
        }
    }
}

Write-Info "2. After restart, look for 'AutoView' in your Home Assistant sidebar"
Write-Info "3. Or access directly at: http://your-ha-ip:8123/visualautoview"
Write-Info "`nThe integration includes:"
Write-Info "  ✅ Native panel in sidebar (no iframe restrictions)"
Write-Info "  ✅ Automatic theme matching (light/dark mode)"
Write-Info "  ✅ Direct access to HA's internal APIs"

if ($DevMode) {
    Write-Info "`n4. Build and deploy frontend:"
    Write-Info "   cd frontend"
    Write-Info "   npm run build"
    Write-Info "   Copy dist/* to /config/www/visualautoview/"
    Write-Info "`n5. Legacy iframe access: http://your-ha-ip:8123/local/visualautoview/"
}

Write-Success "`nThank you for installing Visual AutoView!"
Write-Info "For support, visit: https://github.com/braczek/HAVisualAutomationViewer"
