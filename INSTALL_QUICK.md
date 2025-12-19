# Visual AutoView - One-Line Installers

Quick installation commands for Visual AutoView.

## Windows (PowerShell)

Copy and paste this into PowerShell:

```powershell
irm https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1 | iex
```

Or download and run:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1" -OutFile "$env:TEMP\install-visualautoview.ps1"; & "$env:TEMP\install-visualautoview.ps1"
```

## Linux / macOS

Copy and paste this into your terminal:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh)
```

Or download and run:

```bash
curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh -o /tmp/install-visualautoview.sh && bash /tmp/install-visualautoview.sh
```

## What These Commands Do

1. Download the latest installation script from GitHub
2. Run it automatically to install Visual AutoView
3. Auto-detect your Home Assistant directory
4. Copy integration files to the correct location
5. Verify the installation
6. Provide next steps

## Options

You can still download the script and run with options:

### Windows
```powershell
# Download script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1" -OutFile ".\install.ps1"

# Run with options
.\install.ps1 -HAConfigPath "C:\path\to\ha" -SkipRestart
```

### Linux/macOS
```bash
# Download script
curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh -o install.sh
chmod +x install.sh

# Run with options
./install.sh --ha-path /path/to/ha --skip-restart
```

## Alternative: Download Release

You can also download pre-packaged releases:

1. Go to [Releases](https://github.com/braczek/HAVisualAutomationViewer/releases/latest)
2. Download `visualautoview.zip`
3. Extract to `/config/custom_components/`
4. Restart Home Assistant

## Need Help?

See the [Installation Guide](INSTALLATION.md) for detailed instructions and troubleshooting.
