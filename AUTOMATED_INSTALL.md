# Automated Installation - Complete Guide

This document explains all the automated installation options available for Visual AutoView.

## 📋 Overview

Visual AutoView now offers multiple installation methods to suit different user preferences:

1. **One-Line Install** - Fastest, downloads and runs automatically
2. **Script Install** - Download script first, then run with options
3. **HACS Install** - Best for ongoing updates
4. **Manual Install** - Full control over the process

---

## 🚀 Installation Methods

### Method 1: One-Line Install (Recommended for Most Users)

The absolute fastest way to install. Copy and paste one command.

#### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1 | iex
```

#### Linux/macOS
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh)
```

**What happens:**
1. ✓ Downloads installation script
2. ✓ Detects Home Assistant directory automatically
3. ✓ Copies integration files
4. ✓ Verifies installation
5. ✓ Provides next steps

**Time required:** ~30 seconds

---

### Method 2: Script Install (More Control)

Download the script first, review it, then run with options.

#### Windows

1. **Download the script:**
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1" -OutFile "install.ps1"
   ```

2. **Run with options:**
   ```powershell
   # Basic installation
   .\install.ps1
   
   # Specify custom HA path
   .\install.ps1 -HAConfigPath "C:\custom\path\to\homeassistant"
   
   # Skip restart prompt
   .\install.ps1 -SkipRestart
   
   # Developer mode (includes frontend build)
   .\install.ps1 -DevMode
   
   # Combine options
   .\install.ps1 -HAConfigPath "C:\HA" -DevMode -SkipRestart
   ```

#### Linux/macOS

1. **Download the script:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh -o install.sh
   chmod +x install.sh
   ```

2. **Run with options:**
   ```bash
   # Basic installation
   ./install.sh
   
   # Specify custom HA path
   ./install.sh --ha-path /custom/path/to/homeassistant
   
   # Skip restart prompt
   ./install.sh --skip-restart
   
   # Developer mode (includes frontend build)
   ./install.sh --dev
   
   # Combine options
   ./install.sh --ha-path /config --dev --skip-restart
   ```

**Time required:** ~1-2 minutes

---

### Method 3: HACS Install (Best for Updates)

If you use HACS (Home Assistant Community Store), this is the best option for ongoing updates.

#### First-Time Setup

1. Open HACS in Home Assistant
2. Navigate to **Integrations**
3. Click the **⋮** (three dots) in top right
4. Select **"Custom repositories"**
5. Add:
   - **URL:** `https://github.com/braczek/HAVisualAutomationViewer`
   - **Category:** Integration
6. Click **"Add"**

#### Installation

1. Search for **"Visual AutoView"** in HACS
2. Click **"Download"**
3. **Restart Home Assistant**
4. Go to **Configuration** → **Integrations**
5. Click **"+ Add Integration"**
6. Search for **"Visual AutoView"**
7. Complete setup

#### Updates

HACS will automatically notify you when updates are available. Click "Update" to get the latest version.

**Time required:** ~3-5 minutes (first time), ~30 seconds (updates)

---

### Method 4: Manual Install

For advanced users or specific requirements.

See [INSTALLATION.md](INSTALLATION.md) for detailed manual installation instructions.

**Time required:** ~5-10 minutes

---

## ✅ Verification

After installation, verify everything is working:

### Windows
```powershell
.\verify_install.ps1
```

### Linux/macOS
```bash
chmod +x verify_install.sh
./verify_install.sh
```

The verification script will:
- ✓ Check Home Assistant connectivity
- ✓ Verify API endpoints are accessible
- ✓ Confirm files are installed correctly
- ✓ Display version information

### Manual Verification

1. **Check Home Assistant Logs:**
   - Look for: `Visual AutoView API setup complete`
   - Should show: `Registered 45 endpoints`

2. **Check Integrations Page:**
   - Go to Configuration → Integrations
   - Visual AutoView should be listed

3. **Test an API Endpoint:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://your-ha-ip:8123/api/visualautoview/health
   ```

---

## 🛠️ What Gets Installed

All installation methods install the same components:

```
/config/custom_components/visualautoview/
├── __init__.py                  # Integration entry point
├── manifest.json                # Integration metadata
├── const.py                     # Constants
├── graph_parser.py              # Automation parser
├── api/                         # REST API (45+ endpoints)
│   ├── __init__.py
│   ├── base.py
│   ├── models.py
│   ├── phase1_api.py           # 4 endpoints
│   ├── phase2_api.py           # 20 endpoints
│   └── phase3_api.py           # 21 endpoints
└── services/                    # Service layer
    ├── __init__.py
    ├── all_automations_service.py
    ├── comparison_engine.py
    ├── dependency_graph_service.py
    ├── entity_relationship_service.py
    ├── execution_path_service.py
    ├── export_service.py
    ├── performance_metrics_service.py
    ├── search_engine.py
    ├── template_expansion_service.py
    └── theme_manager.py
```

**With `-DevMode` / `--dev` option, also installs:**
```
/config/www/visualautoview/      # Frontend web interface
├── index.html
├── assets/
│   ├── app.js
│   ├── app.css
│   └── vendor.js
└── ...
```

---

## 🔧 Installation Options Explained

### Auto-Detection

All scripts automatically detect your Home Assistant directory by checking:
- `~/.homeassistant` (most Linux installations)
- `/config` (Home Assistant OS, Docker)
- `C:\ProgramData\HomeAssistant` (Windows)
- Custom locations via user input

### Skip Restart

By default, scripts offer to restart Home Assistant. Use skip options if:
- You want to install multiple integrations before restarting
- You prefer to restart manually
- You're running in a restricted environment

### Dev Mode

Developer mode additionally:
- Installs Node.js frontend dependencies
- Builds the TypeScript frontend
- Copies built files to `www/visualautoview/`
- Enables the web interface

**Only use if:**
- You want the web UI
- You have Node.js 18+ installed
- You're comfortable with frontend development

---

## 📊 Comparison Matrix

| Feature | One-Line | Script | HACS | Manual |
|---------|----------|--------|------|--------|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡ |
| Ease | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Control | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Updates | Manual | Manual | Auto | Manual |
| Review Code | No | Yes | No | Yes |
| Custom Path | No | Yes | No | Yes |
| Offline | No | After DL | No | Yes |

---

## 🆘 Troubleshooting

### Script Won't Run (Windows)

**Error:** "Running scripts is disabled on this system"

**Solution:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Script Won't Run (Linux/macOS)

**Error:** "Permission denied"

**Solution:**
```bash
chmod +x install.sh
```

### Home Assistant Not Detected

**Solutions:**
1. Specify path manually:
   ```powershell
   .\install.ps1 -HAConfigPath "C:\path\to\ha"
   ```
   ```bash
   ./install.sh --ha-path /path/to/ha
   ```

2. Ensure `configuration.yaml` exists in the directory

### Installation Succeeds But Integration Not Found

**Solutions:**
1. Verify files copied correctly:
   ```bash
   ls -la /config/custom_components/visualautoview/
   ```

2. Check manifest.json exists and is valid:
   ```bash
   cat /config/custom_components/visualautoview/manifest.json
   ```

3. Restart Home Assistant (full restart, not just reload)

4. Check logs for errors:
   ```
   Configuration → Logs
   ```

### API Endpoints Return 404

**Solutions:**
1. Run verification script
2. Check integration is enabled in Integrations page
3. Verify in logs: "Visual AutoView API setup complete"
4. Try restarting Home Assistant again

---

## 📚 Next Steps After Installation

1. **Verify Installation:**
   ```bash
   ./verify_install.sh  # or .ps1 on Windows
   ```

2. **Access Integration:**
   - Configuration → Integrations → Visual AutoView

3. **Read Documentation:**
   - [Quick Start Guide](QUICK_START.md)
   - [API Reference](API_IMPLEMENTATION_COMPLETE.md)
   - [Full Documentation](README.md)

4. **Test API Endpoints:**
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
        http://ha-ip:8123/api/visualautoview/automations
   ```

5. **Explore Features:**
   - Graph visualization
   - Automation search
   - Performance analytics
   - Entity relationships

---

## 🔄 Updating

### Via HACS
HACS will notify you of updates. Click "Update" when available.

### Via Script
Re-run the installation script. It will detect the existing installation and update it:
```powershell
.\install.ps1  # Windows
```
```bash
./install.sh   # Linux/macOS
```

### Manual
Download the latest release and replace the files in `custom_components/visualautoview/`.

---

## 🗑️ Uninstallation

### Via Home Assistant
1. Configuration → Integrations
2. Find Visual AutoView
3. Click ⋮ → Delete

### Remove Files

**Windows:**
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.homeassistant\custom_components\visualautoview"
```

**Linux/macOS:**
```bash
rm -rf ~/.homeassistant/custom_components/visualautoview
rm -rf /config/custom_components/visualautoview  # if Docker/HAOS
```

**Restart Home Assistant** after removal.

---

## 💡 Tips

1. **Use One-Line Install** for quickest setup
2. **Use HACS** if you want automatic updates
3. **Use Script Install** if you need custom paths
4. **Review verification script** output to ensure everything works
5. **Check logs** after installation for any warnings
6. **Bookmark API docs** for reference

---

## 🆘 Getting Help

- **GitHub Issues:** [Report bugs or request features](https://github.com/braczek/HAVisualAutomationViewer/issues)
- **Discussions:** [Ask questions](https://github.com/braczek/HAVisualAutomationViewer/discussions)
- **Documentation:** [Full docs](README.md)
- **Community:** [Home Assistant Forum](https://community.home-assistant.io/)

---

**Happy Automating! 🎉**
