# Visual AutoView - Home Assistant Automation Visualization

**Status**: ✅ **PRODUCTION READY**  
**Version**: 1.0.0  
**Date**: December 17, 2025

---

## 📚 Documentation Guide

This repository contains all necessary files for the Visual AutoView integration. Here's what each document covers:

### 🚀 Installation & Setup
1. **[INSTALL_QUICK.md](INSTALL_QUICK.md)** ← **FASTEST START**
   - One-line installation commands
   - Quick copy-paste installers
   
2. **[AUTOMATED_INSTALL.md](AUTOMATED_INSTALL.md)** ← **RECOMMENDED**
   - Complete automation guide
   - All installation methods explained
   - Comparison and troubleshooting
   
3. **[INSTALLATION.md](INSTALLATION.md)**
   - Detailed installation instructions
   - Manual installation steps
   - Platform-specific guides

### 🏁 Getting Started
1. **[QUICK_START.md](QUICK_START.md)**
   - Project overview
   - Development setup
   - API endpoint reference
   - Troubleshooting guide

### 📋 Implementation Status
2. **[FINAL_STATUS_REPORT.md](FINAL_STATUS_REPORT.md)**
   - Current project status
   - What was completed
   - Key metrics and statistics
   - Production readiness checklist

3. **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)**
   - Complete implementation details
   - All components and endpoints listed
   - Code architecture overview
   - Quality assurance information

### 🔧 Technical Reference
4. **[API_IMPLEMENTATION_COMPLETE.md](API_IMPLEMENTATION_COMPLETE.md)**
   - All 45+ REST API endpoints documented
   - Request/response examples
   - Integration points
   - Feature descriptions

### 📅 Phase Documentation
5. **[PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md)** - Core graph parsing
6. **[PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)** - Dashboard & management
7. **[PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md)** - Advanced analytics

### 🎯 Next Steps
8. **[POST_IMPLEMENTATION_CHECKLIST.md](POST_IMPLEMENTATION_CHECKLIST.md)**
   - Pre-release testing checklist
   - Deployment procedures
   - Release planning template
   - Support structure guidelines

---

## 📊 Project Summary

```
Backend:        3,071 lines (7 files)
├── Phase 1 API:  4 endpoints
├── Phase 2 API: 20 endpoints
└── Phase 3 API: 21+ endpoints

Frontend:       2,010 lines (11 files)
├── 7 main components
├── API client (21+ methods)
└── Build configuration

Total:          5,081+ lines of production code
```

---

## ✨ Features

- ✅ **Graph Visualization** - Interactive automation flow visualization
- ✅ **Dashboard** - Automation management and overview
- ✅ **Search & Filter** - Advanced search capabilities
- ✅ **Analytics** - Performance metrics and analysis
- ✅ **Export** - Multi-format export (JSON, YAML, CSV)
- ✅ **Comparison** - Automation comparison and similarity
- ✅ **Themes** - Custom theme management
- ✅ **Entity Analysis** - Relationship and dependency tracking

---

## 🚀 Quick Start

### Installation

#### ⚡ One-Line Install (Fastest)

**Windows PowerShell**:
```powershell
irm https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.ps1 | iex
```

**Linux/macOS**:
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/braczek/HAVisualAutomationViewer/main/install.sh)
```

**[→ More installation options](INSTALL_QUICK.md)**

---

#### Option 1: Automated Installation (Easiest) ⚡

**Windows (PowerShell)**:
```powershell
cd path\to\VisualAutoView
.\install.ps1
```

**Linux/macOS (Bash)**:
```bash
chmod +x install.sh
./install.sh
```

The script will:
- ✓ Auto-detect your Home Assistant directory
- ✓ Install all required files
- ✓ Verify the installation
- ✓ Guide you through the setup

**[→ View detailed installation guide](INSTALLATION.md)**

#### Option 2: HACS (Recommended for Updates)
1. Open HACS in your Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/braczek/HAVisualAutomationViewer`
6. Search for "Visual AutoView"
7. Click "Install"
8. Restart Home Assistant

#### Option 3: Manual Installation
1. Access your Home Assistant configuration folder via:
   - **Samba share**: `\\your-ha-ip\config`
   - **SSH/Terminal addon**: Navigate to `/config`
   - **File editor addon**: Use the built-in file browser
2. Create `custom_components` folder if it doesn't exist
3. Copy the `visualautoview` folder into `config/custom_components/`
4. Your structure should be: `config/custom_components/visualautoview/`
5. Add to your `configuration.yaml`:
   ```yaml
   visualautoview:
   ```
6. Restart Home Assistant
7. After restart:
   - The panel "AutoView" will appear automatically in your sidebar
   - The API will be available at: `http://your-ha-ip:8123/api/visualautoview/`
   - Access the panel at: `http://your-ha-ip:8123/visualautoview`

#### Option 3: Manual Installation (Home Assistant Core)
```bash
# Copy backend to Home Assistant
cp -r custom_components/visualautoview ~/.homeassistant/custom_components/

# Restart Home Assistant
```

### Accessing Visual AutoView

After installation and restart, the interface is automatically available in your Home Assistant sidebar!

#### Step 1: Build the Frontend
```bash
cd frontend
npm install
npm run build
```

#### Step 2: Copy Frontend to Home Assistant
```bash
# Copy the built frontend to your HA www folder
cp -r dist \\192.168.1.7\config\www\visualautoview
```

#### Step 3: Restart Home Assistant
After copying, restart Home Assistant.

#### Step 4: Access the Interface

**Native Panel (Automatic)**
- Look for **"AutoView"** in your Home Assistant sidebar (with graph icon)
- Or navigate to: http://192.168.1.7:8123/visualautoview
- Full HA theme integration (matches light/dark mode automatically)
- Direct access to HA's internal APIs

**Legacy iframe Mode (Optional)**
- Direct URL: http://192.168.1.7:8123/local/visualautoview/index.html
- Limited theme access and cross-origin restrictions

**Benefits of Native Panel:**
- ✅ Automatic theme matching (light/dark mode)
- ✅ Direct access to `hass` object (states, services, WebSocket)
- ✅ No iframe restrictions
- ✅ Better performance
- ✅ Native HA look and feel

**API Endpoints:**
- Base URL: http://192.168.1.7:8123/api/visualautoview/
- Documentation: [API_IMPLEMENTATION_COMPLETE.md](API_IMPLEMENTATION_COMPLETE.md)

### Frontend Development
```bash
# Install frontend dependencies
cd frontend
npm install

# Build frontend
npm run build
```

### Development
```bash
# Start frontend dev server
npm run dev

# Run tests
pytest tests/ -v

# Type check
npm run type-check

# Verify implementation
python verify_implementation.py
```

---

## 📁 Source Code Structure

- **Backend**: `custom_components/visualautoview/`
  - **API Endpoints**: `api/` (45+ REST endpoints)
  - **Services**: `services/` (10 backend services)
- **Frontend**: `frontend/src/` (7 components)
- **Tests**: `tests/` (unit tests)


---

## 📞 Documentation by Topic

| Topic | Document |
|-------|----------|
| Getting Started | [QUICK_START.md](QUICK_START.md) |
| Project Status | [FINAL_STATUS_REPORT.md](FINAL_STATUS_REPORT.md) |
| Implementation Details | [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) |
| API Reference | [API_IMPLEMENTATION_COMPLETE.md](API_IMPLEMENTATION_COMPLETE.md) |
| Release Planning | [POST_IMPLEMENTATION_CHECKLIST.md](POST_IMPLEMENTATION_CHECKLIST.md) |
| Phase 1 Details | [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) |
| Phase 2 Details | [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md) |
| Phase 3 Details | [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md) |

---

## ✅ Verification

Run the automated verification script:
```bash
python verify_implementation.py
```

Expected output: All components verified, production ready ✅

---

## 🎯 Status

| Aspect | Status |
|--------|--------|
| Implementation | ✅ Complete (100%) |
| Frontend | ✅ Complete (7 components) |
| Backend | ✅ Complete (45+ endpoints) |
| Testing | ✅ Complete (17 tests) |
| Documentation | ✅ Complete (8 guides) |
| Production Ready | ✅ YES |

---

## 📄 License

[Your License Here]

---

## 🙋 Support

For detailed information, see the documentation guides listed above.

**Ready to deploy! Follow [QUICK_START.md](QUICK_START.md) to get started.**
