#!/bin/bash
# Visual AutoView Installation Verification Script
# Run this after installation to verify everything is working correctly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ $1${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; }

HA_URL="${1:-http://localhost:8123}"
TOKEN="${2:-}"

info "Visual AutoView Installation Verification"
info "=========================================\n"

# Check if Home Assistant is accessible
info "Checking Home Assistant connectivity..."
if curl -sf "$HA_URL/api/" > /dev/null 2>&1; then
    success "Home Assistant is accessible at $HA_URL"
else
    error "Cannot reach Home Assistant at $HA_URL"
    warning "Please ensure Home Assistant is running and the URL is correct"
    exit 1
fi

# Get token if not provided
if [ -z "$TOKEN" ]; then
    info "\nTo verify API access, we need a long-lived access token."
    info "Create one in Home Assistant: Profile → Long-Lived Access Tokens"
    read -p "Enter your Home Assistant long-lived access token (optional, press Enter to skip): " TOKEN
fi

if [ -n "$TOKEN" ]; then
    info "\nVerifying Visual AutoView API endpoints..."
    
    ENDPOINTS=(
        "/api/visualautoview/automations"
        "/api/visualautoview/health"
        "/api/visualautoview/stats"
    )
    
    SUCCESS_COUNT=0
    for endpoint in "${ENDPOINTS[@]}"; do
        if curl -sf -H "Authorization: Bearer $TOKEN" "$HA_URL$endpoint" > /dev/null 2>&1; then
            success "Endpoint working: $endpoint"
            ((SUCCESS_COUNT++))
        else
            warning "Endpoint failed: $endpoint"
        fi
    done
    
    info "\nEndpoint Test Results: $SUCCESS_COUNT/${#ENDPOINTS[@]} passed"
    
    if [ $SUCCESS_COUNT -eq ${#ENDPOINTS[@]} ]; then
        success "\n🎉 All API endpoints are working correctly!"
    elif [ $SUCCESS_COUNT -gt 0 ]; then
        warning "\n⚠️  Some endpoints are not responding. Check Home Assistant logs."
    else
        error "\n❌ API endpoints are not accessible. Integration may not be loaded."
        info "Try:"
        info "  1. Restart Home Assistant"
        info "  2. Check logs for errors"
        info "  3. Verify integration is enabled in Configuration → Integrations"
    fi
else
    warning "\nSkipping API verification (no token provided)"
fi

# Check file installation
info "\nChecking file installation..."
COMMON_PATHS=(
    "$HOME/.homeassistant/custom_components/visualautoview"
    "/config/custom_components/visualautoview"
    "/usr/share/hassio/homeassistant/custom_components/visualautoview"
)

FOUND=false
for path in "${COMMON_PATHS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/manifest.json" ]; then
        VERSION=$(grep -o '"version": "[^"]*' "$path/manifest.json" | cut -d'"' -f4)
        DOMAIN=$(grep -o '"domain": "[^"]*' "$path/manifest.json" | cut -d'"' -f4)
        success "Found installation at: $path"
        success "Version: $VERSION"
        success "Domain: $DOMAIN"
        FOUND=true
        break
    fi
done

if [ "$FOUND" = false ]; then
    warning "Could not locate installation in common directories"
    info "Installation may be in a custom location"
fi

info "\n========================================="
info "Verification complete!"
info "\nNext Steps:"
info "  1. Open Home Assistant: $HA_URL"
info "  2. Go to Configuration → Integrations"
info "  3. Verify 'Visual AutoView' is listed and active"
info "  4. Check logs for any errors"
info "\nDocumentation: https://github.com/braczek/HAVisualAutomationViewer"
