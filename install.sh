#!/bin/bash
# Visual AutoView Installation Script for Home Assistant
# This script automates the installation process for Linux and macOS

set -e

# Color output functions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Parse command line arguments
HA_CONFIG_PATH=""
SKIP_RESTART=false
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --ha-path)
            HA_CONFIG_PATH="$2"
            shift 2
            ;;
        --skip-restart)
            SKIP_RESTART=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

info "Visual AutoView Installation Script"
info "====================================\n"

# Detect Home Assistant config directory
if [ -z "$HA_CONFIG_PATH" ]; then
    info "Detecting Home Assistant configuration directory..."
    
    POSSIBLE_PATHS=(
        "$HOME/.homeassistant"
        "$HOME/homeassistant"
        "/config"
        "/usr/share/hassio/homeassistant"
    )
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ] && [ -f "$path/configuration.yaml" ]; then
            HA_CONFIG_PATH="$path"
            success "Found Home Assistant at: $HA_CONFIG_PATH"
            break
        fi
    done
    
    if [ -z "$HA_CONFIG_PATH" ]; then
        warning "Could not auto-detect Home Assistant directory."
        read -p "Please enter the full path to your Home Assistant config directory: " HA_CONFIG_PATH
        
        if [ ! -d "$HA_CONFIG_PATH" ]; then
            error "Path does not exist: $HA_CONFIG_PATH"
        fi
    fi
fi

# Verify Home Assistant directory
if [ ! -f "$HA_CONFIG_PATH/configuration.yaml" ]; then
    error "Invalid Home Assistant directory (configuration.yaml not found)"
fi

success "Using Home Assistant directory: $HA_CONFIG_PATH\n"

# Create custom_components directory if it doesn't exist
CUSTOM_COMPONENTS_PATH="$HA_CONFIG_PATH/custom_components"
if [ ! -d "$CUSTOM_COMPONENTS_PATH" ]; then
    info "Creating custom_components directory..."
    mkdir -p "$CUSTOM_COMPONENTS_PATH"
    success "Created custom_components directory"
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy integration files
SOURCE_PATH="$SCRIPT_DIR/custom_components/visualautoview"
DEST_PATH="$CUSTOM_COMPONENTS_PATH/visualautoview"

info "Installing Visual AutoView integration..."

if [ -d "$DEST_PATH" ]; then
    warning "Visual AutoView is already installed. Updating..."
    rm -rf "$DEST_PATH"
fi

cp -r "$SOURCE_PATH" "$DEST_PATH"
success "Integration files copied successfully"

# Verify installation
MANIFEST_PATH="$DEST_PATH/manifest.json"
if [ -f "$MANIFEST_PATH" ]; then
    VERSION=$(grep -o '"version": "[^"]*' "$MANIFEST_PATH" | cut -d'"' -f4)
    success "Installed Visual AutoView v$VERSION"
else
    error "Installation verification failed - manifest.json not found"
fi

# Create www directory for frontend if needed
WWW_PATH="$HA_CONFIG_PATH/www"
if [ ! -d "$WWW_PATH" ]; then
    mkdir -p "$WWW_PATH"
    success "Created www directory"
fi

# Build and install frontend if in dev mode
if [ "$DEV_MODE" = true ]; then
    info "\nBuilding frontend..."
    FRONTEND_PATH="$SCRIPT_DIR/frontend"
    
    if [ -d "$FRONTEND_PATH" ]; then
        cd "$FRONTEND_PATH"
        
        info "Installing frontend dependencies..."
        npm install
        
        info "Building frontend..."
        npm run build
        
        # Copy built frontend to www directory
        DIST_PATH="$FRONTEND_PATH/dist"
        FRONTEND_DEST_PATH="$WWW_PATH/visualautoview"
        
        if [ -d "$DIST_PATH" ]; then
            if [ -d "$FRONTEND_DEST_PATH" ]; then
                rm -rf "$FRONTEND_DEST_PATH"
            fi
            cp -r "$DIST_PATH" "$FRONTEND_DEST_PATH"
            success "Frontend installed to www/visualautoview"
        fi
        
        cd - > /dev/null
    fi
fi

success "\nInstallation completed successfully!\n"

info "========================================="
info "You can verify the installation by running:"
info "  ./verify_install.sh"
info "=========================================\n"

# Next steps
info "Next Steps:"
info "==========="
info "1. Restart Home Assistant"

if [ "$SKIP_RESTART" = false ]; then
    read -p "Would you like to restart Home Assistant now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Restarting Home Assistant..."
        
        # Try to restart via Home Assistant CLI
        if command -v ha &> /dev/null; then
            ha core restart
            success "Restart command sent"
        else
            warning "Home Assistant CLI not found. Please restart manually."
        fi
    fi
fi

info "2. After restart, look for 'AutoView' in your Home Assistant sidebar"
info "3. Or access directly at: http://your-ha-ip:8123/visualautoview"
info ""
info "The integration includes:"
info "  ✅ Native panel in sidebar (no iframe restrictions)"
info "  ✅ Automatic theme matching (light/dark mode)"
info "  ✅ Direct access to HA's internal APIs"

if [ "$DEV_MODE" = true ]; then
    info ""
    info "4. Build and deploy frontend:"
    info "   cd frontend"
    info "   npm run build"
    info "   Copy dist/* to /config/www/visualautoview/"
    info ""
    info "5. Legacy iframe access: http://your-ha-ip:8123/local/visualautoview/"
fi

success "\nThank you for installing Visual AutoView!"
info "For support, visit: https://github.com/braczek/HAVisualAutomationViewer"
