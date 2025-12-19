# Visual AutoView - Installation Guide

Complete installation instructions for Visual AutoView Home Assistant integration.

## Table of Contents
- [Requirements](#requirements)
- [Installation Methods](#installation-methods)
  - [Automated Installation (Recommended)](#automated-installation-recommended)
  - [HACS Installation](#hacs-installation)
  - [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Requirements

- **Home Assistant**: Version 2023.1.0 or newer
- **Python**: 3.11+ (included with Home Assistant)
- **Optional**: Node.js 18+ and npm (for frontend development)

---

## Installation Methods

### Automated Installation (Recommended)

The easiest way to install Visual AutoView is using the automated installation script.

#### Windows (PowerShell)

```powershell
# Download and run the installation script
cd path\to\VisualAutoView
.\install.ps1
```

**Options:**
```powershell
# Specify custom Home Assistant path
.\install.ps1 -HAConfigPath "C:\path\to\homeassistant"

# Skip the restart prompt
.\install.ps1 -SkipRestart

# Install with frontend build (for developers)
.\install.ps1 -DevMode
```

#### Linux / macOS (Bash)

```bash
# Make the script executable
chmod +x install.sh

# Run the installation script
./install.sh
```

**Options:**
```bash
# Specify custom Home Assistant path
./install.sh --ha-path /path/to/homeassistant

# Skip the restart prompt
./install.sh --skip-restart

# Install with frontend build (for developers)
./install.sh --dev
```

#### What the Script Does

1. ✓ Auto-detects your Home Assistant configuration directory
2. ✓ Creates `custom_components` directory if needed
3. ✓ Copies all integration files
4. ✓ Verifies installation
5. ✓ Optionally builds and installs frontend
6. ✓ Provides next steps

---

### HACS Installation

HACS (Home Assistant Community Store) provides the easiest way to manage custom integrations.

#### Prerequisites

1. Install HACS if you haven't already: [HACS Installation Guide](https://hacs.xyz/docs/setup/download)

#### Installation Steps

1. **Open HACS** in your Home Assistant instance
2. Click on **"Integrations"**
3. Click the **three dots** (⋮) in the top right corner
4. Select **"Custom repositories"**
5. Add the repository:
   - **URL**: `https://github.com/braczek/HAVisualAutomationViewer`
   - **Category**: Integration
6. Click **"Add"**
7. Search for **"Visual AutoView"** in HACS
8. Click **"Download"**
9. **Restart Home Assistant**
10. Go to **Configuration** → **Integrations**
11. Click **"+ Add Integration"**
12. Search for **"Visual AutoView"**
13. Complete the setup

---

### Manual Installation

For advanced users or specific deployment scenarios.

#### Home Assistant OS / Supervised

1. **Access your Home Assistant installation**:
   - Via SSH add-on, or
   - Via Samba share, or
   - Via Terminal & SSH

2. **Navigate to config directory**:
   ```bash
   cd /config
   ```

3. **Create custom_components directory** (if it doesn't exist):
   ```bash
   mkdir -p custom_components
   ```

4. **Download and extract Visual AutoView**:
   ```bash
   cd custom_components
   git clone https://github.com/braczek/HAVisualAutomationViewer.git
   mv HAVisualAutomationViewer/custom_components/visualautoview ./
   rm -rf HAVisualAutomationViewer
   ```

   Or download the release archive:
   ```bash
   cd custom_components
   wget https://github.com/braczek/HAVisualAutomationViewer/releases/latest/download/visualautoview.zip
   unzip visualautoview.zip
   rm visualautoview.zip
   ```

5. **Verify the structure**:
   ```bash
   ls -la /config/custom_components/visualautoview/
   ```
   
   You should see:
   ```
   __init__.py
   manifest.json
   const.py
   graph_parser.py
   api/
   services/
   ```

6. **Restart Home Assistant**

#### Home Assistant Container (Docker)

1. **Locate your config directory** (usually mapped as a volume)

2. **Add integration files**:
   ```bash
   cd /path/to/your/ha/config
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/braczek/HAVisualAutomationViewer.git
   mv HAVisualAutomationViewer/custom_components/visualautoview ./
   rm -rf HAVisualAutomationViewer
   ```

3. **Restart the container**:
   ```bash
   docker restart homeassistant
   ```

#### Home Assistant Core (Python venv)

1. **Navigate to your config directory**:
   ```bash
   cd ~/.homeassistant  # or your custom path
   ```

2. **Create custom_components**:
   ```bash
   mkdir -p custom_components
   cd custom_components
   ```

3. **Clone the repository**:
   ```bash
   git clone https://github.com/braczek/HAVisualAutomationViewer.git
   mv HAVisualAutomationViewer/custom_components/visualautoview ./
   rm -rf HAVisualAutomationViewer
   ```

4. **Restart Home Assistant**:
   ```bash
   systemctl restart home-assistant@homeassistant
   # or
   sudo systemctl restart home-assistant
   ```

---

## Configuration

### Adding the Integration

1. Navigate to **Configuration** → **Integrations**
2. Click the **"+ Add Integration"** button
3. Search for **"Visual AutoView"**
4. Click on it to add
5. The integration will automatically discover your automations

### Verification

Check that the integration loaded successfully:

1. **Check logs** for confirmation message:
   ```
   Visual AutoView API setup complete
   Registered 45 endpoints
   ```

2. **Test an endpoint** (replace with your HA URL and token):
   ```bash
   curl -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN" \
        http://your-ha-ip:8123/api/visualautoview/automations
   ```

### Frontend Setup (Optional)

To use the web interface:

1. **Copy built frontend** to `www` directory:
   ```bash
   mkdir -p /config/www/visualautoview
   # Copy contents of frontend/dist/ to www/visualautoview/
   ```

2. **Access the interface**:
   ```
   http://your-ha-ip:8123/local/visualautoview/
   ```

---

## Troubleshooting

### Integration Doesn't Appear

**Problem**: Visual AutoView doesn't show up in the integration list.

**Solutions**:
1. Verify files are in the correct location: `/config/custom_components/visualautoview/`
2. Check that `manifest.json` exists and is valid JSON
3. Restart Home Assistant completely (not just reload integrations)
4. Check Home Assistant logs for errors:
   ```bash
   ha core logs
   ```

### Permission Errors (Docker/Linux)

**Problem**: Permission denied errors when copying files.

**Solutions**:
```bash
# Fix ownership (adjust UID:GID as needed)
sudo chown -R 1000:1000 /config/custom_components/visualautoview

# Fix permissions
sudo chmod -R 755 /config/custom_components/visualautoview
```

### Import Errors

**Problem**: Errors about missing Python modules.

**Solutions**:
1. Ensure Home Assistant is version 2023.1.0+
2. Check that all files were copied correctly
3. Restart Home Assistant
4. Check logs for specific missing modules

### API Endpoints Return 404

**Problem**: API calls return 404 Not Found.

**Solutions**:
1. Verify integration is loaded (check logs)
2. Ensure proper authorization header
3. Check endpoint URL format:
   ```
   http://your-ha-ip:8123/api/visualautoview/endpoint
   ```
4. Verify automations exist in Home Assistant

### Frontend Not Loading

**Problem**: Frontend shows blank page or errors.

**Solutions**:
1. Check browser console for errors (F12)
2. Verify files are in `/config/www/visualautoview/`
3. Clear browser cache
4. Ensure proper CORS settings
5. Check that files have correct permissions

### Getting Help

If you encounter issues:

1. **Check the logs**:
   - Home Assistant: Configuration → Logs
   - Or via CLI: `ha core logs`

2. **Search existing issues**: [GitHub Issues](https://github.com/braczek/HAVisualAutomationViewer/issues)

3. **Create a new issue** with:
   - Home Assistant version
   - Installation method used
   - Error messages from logs
   - Steps to reproduce

4. **Community Support**:
   - [Home Assistant Community Forum](https://community.home-assistant.io/)
   - Tag your post with `visualautoview`

---

## Uninstallation

To remove Visual AutoView:

1. **Remove the integration**:
   - Go to Configuration → Integrations
   - Find Visual AutoView
   - Click the three dots and select "Delete"

2. **Remove files**:
   ```bash
   rm -rf /config/custom_components/visualautoview
   rm -rf /config/www/visualautoview  # if you installed frontend
   ```

3. **Restart Home Assistant**

---

## Next Steps

After successful installation:

1. Read the [QUICK_START.md](QUICK_START.md) guide
2. Explore the [API Documentation](API_IMPLEMENTATION_COMPLETE.md)
3. Check out example use cases
4. Join the community discussions

---

**Questions?** Visit our [GitHub repository](https://github.com/braczek/HAVisualAutomationViewer)
