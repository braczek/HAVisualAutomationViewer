# Visual AutoView - Automation Graph Visualization for Home Assistant

**Status**: ✅ **PRODUCTION READY**  
**Version**: 1.0.1

## 📖 About

Visual AutoView is a Home Assistant integration that provides advanced visualization and analysis of automation flows. It helps you understand your automation logic through interactive graphs, search capabilities, and detailed analytics.

## ✨ Features

- **Interactive Graph Visualization** - See your automations as visual flowcharts
- **Automation Dashboard** - Centralized view of all automations with management controls
- **Advanced Search & Filter** - Quickly find automations by triggers, actions, and conditions
- **Performance Analytics** - Monitor automation execution and performance metrics
- **Multi-Format Export** - Export automations as JSON, YAML, or CSV
- **Entity Relationship Analysis** - Track dependencies between entities and automations
- **Comparison Tools** - Compare similarities and differences between automations
- **Theme Management** - Customize the visual appearance

## 🚀 Installation

### Automatic Installation (Recommended)

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1 | iex
```

**Linux/macOS:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh)
```

### Manual Installation

1. Download the [latest release](https://github.com/braczek/HAVisualAutomationViewer/releases)
2. Extract the `visualautoview` folder to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings → Devices & Services** and look for "Visual AutoView" in the Integrations panel

### Installation Verification

Run the verification script to ensure everything is set up correctly:

**Windows:**
```powershell
.\verify_install.ps1
```

**Linux/macOS:**
```bash
bash verify_install.sh
```

## 📚 Getting Started

After installation, Visual AutoView will appear as "AutoView" in your Home Assistant sidebar. Access it by:
- Clicking the **AutoView** panel in the sidebar
- Or navigating to: `http://your-ha-ip:8123/visualautoview`

The integration provides REST API endpoints at `http://your-ha-ip:8123/api/visualautoview/`

## 📁 Source Code Structure

- **Backend**: `custom_components/visualautoview/`
  - **API Endpoints**: `api/` (45+ REST endpoints)
  - **Services**: `services/` (10 backend services)
- **Frontend**: `frontend/src/` (7 components)
- **Tests**: `tests/` (unit tests)

## 📄 License

[Your License Here]

## 🔗 Links

- **GitHub Repository**: https://github.com/braczek/HAVisualAutomationViewer
- **Home Assistant**: https://www.home-assistant.io/
- **Issues**: https://github.com/braczek/HAVisualAutomationViewer/issues
