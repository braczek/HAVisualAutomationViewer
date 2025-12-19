# Deployment Guide for VisualAutoView

## Deployment Overview

This integration requires deploying both backend (Python) and frontend (TypeScript/JavaScript) components to a Home Assistant instance.

**Target Server:** `\\192.168.1.7\config\`  
**Web Access:** `http://192.168.1.7:8123/local/visualautoview/index.html`

---

## Backend Deployment (Python Integration)

### 1. Deploy Backend Files

Copy the entire integration to the custom_components directory:

```powershell
Copy-Item -Path "C:\Repositories\HA\VisualAutoView\custom_components\visualautoview\*" `
    -Destination "\\192.168.1.7\config\custom_components\visualautoview\" `
    -Recurse -Force
```

### 2. Verify Backend Deployment

```powershell
Test-Path "\\192.168.1.7\config\custom_components\visualautoview\graph_parser.py"
Get-Item "\\192.168.1.7\config\custom_components\visualautoview\graph_parser.py" | Select-Object LastWriteTime, Length
```

### 3. Restart Home Assistant

**Option 1: PowerShell Script**
```powershell
.\restart_ha.ps1
```

**Option 2: Home Assistant UI**
- Settings → System → Restart

**Option 3: Developer Tools**
- Developer Tools → YAML → Restart

---

## Frontend Deployment (Web Application)

### 1. Build Frontend

```powershell
cd C:\Repositories\HA\VisualAutoView\frontend
npm run build
```

Expected output: Production bundle in `dist/` directory (~700KB)

### 2. Clean Old Builds (Important!)

Remove old JavaScript bundles before deploying new ones:

```powershell
# Get current build hash from index.html
$indexContent = Get-Content "C:\Repositories\HA\VisualAutoView\frontend\dist\index.html" -Raw
if ($indexContent -match 'main-(\w+)\.js') {
    $currentHash = $matches[1]
    Write-Host "Current build: main-$currentHash.js" -ForegroundColor Green
    
    # Remove all old builds from destination
    Remove-Item "\\192.168.1.7\config\www\visualautoview\assets\main-*.js" -Exclude "main-$currentHash.js"
    Remove-Item "\\192.168.1.7\config\www\visualautoview\assets\main-*.js.map" -Exclude "main-$currentHash.js.map"
    
    Write-Host "✓ Old builds cleaned" -ForegroundColor Green
}
```

### 3. Deploy Frontend Files

```powershell
Copy-Item -Path "C:\Repositories\HA\VisualAutoView\frontend\dist\*" `
    -Destination "\\192.168.1.7\config\www\visualautoview\" `
    -Recurse -Force
```

### 4. Verify Frontend Deployment

```powershell
Get-ChildItem "\\192.168.1.7\config\www\visualautoview\" | Select-Object Name, LastWriteTime, Length
Get-ChildItem "\\192.168.1.7\config\www\visualautoview\assets\" | Select-Object Name, LastWriteTime, Length
```

Expected files:
- `index.html` (~2KB)
- `assets/main-{hash}.js` (~700KB)
- `assets/main-{hash}.js.map` (~2.2MB)

---

## One-Line Deployment Commands

### Backend Only
```powershell
Copy-Item -Path "C:\Repositories\HA\VisualAutoView\custom_components\visualautoview\*" -Destination "\\192.168.1.7\config\custom_components\visualautoview\" -Recurse -Force
```

### Frontend Only (Build + Clean + Deploy)
```powershell
cd C:\Repositories\HA\VisualAutoView\frontend; npm run build; $indexContent = Get-Content "dist\index.html" -Raw; if ($indexContent -match 'main-(\w+)\.js') { $currentHash = $matches[1]; Remove-Item "\\192.168.1.7\config\www\visualautoview\assets\main-*.js" -Exclude "main-$currentHash.js"; Remove-Item "\\192.168.1.7\config\www\visualautoview\assets\main-*.js.map" -Exclude "main-$currentHash.js.map" }; Copy-Item -Path "dist\*" -Destination "\\192.168.1.7\config\www\visualautoview\" -Recurse -Force
```

### Full Deployment (Backend + Frontend)
```powershell
# Deploy backend
Copy-Item -Path "C:\Repositories\HA\VisualAutoView\custom_components\visualautoview\*" -Destination "\\192.168.1.7\config\custom_components\visualautoview\" -Recurse -Force

# Build and deploy frontend
cd C:\Repositories\HA\VisualAutoView\frontend
npm run build
$indexContent = Get-Content "dist\index.html" -Raw
if ($indexContent -match 'main-(\w+)\.js') { 
    $currentHash = $matches[1]
    Remove-Item "\\192.168.1.7\config\www\visualautoview\assets\main-*.js" -Exclude "main-$currentHash.js"
    Remove-Item "\\192.168.1.7\config\www\visualautoview\assets\main-*.js.map" -Exclude "main-$currentHash.js.map"
}
Copy-Item -Path "dist\*" -Destination "\\192.168.1.7\config\www\visualautoview\" -Recurse -Force

Write-Host "✓ Deployment complete! Restart Home Assistant to apply changes." -ForegroundColor Green
```

---

## Post-Deployment Steps

### 1. Restart Home Assistant
Wait 30-60 seconds for full restart

### 2. Clear Browser Cache
Hard refresh to load new JavaScript bundle:
- **Chrome/Edge:** `Ctrl + Shift + R`
- **Firefox:** `Ctrl + Shift + R`
- **Safari:** `Cmd + Shift + R`

### 3. Access Application
```
http://192.168.1.7:8123/local/visualautoview/index.html
```

### 4. Verify Deployment

**Backend Check:**
```
http://192.168.1.7:8123/api/visualautoview/health
```
Expected: `{"status": "ok", "version": "1.0.0"}`

**Home Assistant Logs:**
Look for: "Visual AutoView API setup complete" and "Registered 45 endpoints"

**Frontend Check:**
- Graph should display correctly
- No console errors (F12 → Console)
- Nested actions should expand properly
- Trigger labels should be descriptive

---

## Troubleshooting

### Changes Not Appearing

1. **Verify file timestamps match deployment time**
   ```powershell
   Get-Item "\\192.168.1.7\config\custom_components\visualautoview\graph_parser.py" | Select-Object LastWriteTime
   Get-Item "\\192.168.1.7\config\www\visualautoview\index.html" | Select-Object LastWriteTime
   ```

2. **Check Home Assistant restarted successfully**
   - Settings → System → Logs (look for errors)

3. **Clear browser cache completely**
   - Chrome: Settings → Privacy → Clear browsing data → Cached images and files

4. **Verify correct JavaScript bundle is loading**
   - F12 → Network tab → Reload page
   - Look for `main-{hash}.js` loading (should match deployed file)

### API Not Responding

1. **Check integration is loaded**
   ```
   http://192.168.1.7:8123/api/visualautoview/health
   ```

2. **Check Home Assistant logs**
   - Settings → System → Logs
   - Filter for "visualautoview"

3. **Verify manifest.json is valid**
   - Should be valid JSON
   - Version should match

### Graph Not Rendering

1. **Check browser console** (F12 → Console)
2. **Verify API returns data**
   ```
   http://192.168.1.7:8123/api/visualautoview/phase1/automations
   ```
3. **Check vis-network loaded**
   - Network tab should show vis-network library loaded

---

## File Structure Reference

### Backend Files (custom_components/visualautoview/)
```
__init__.py           - Integration setup
const.py             - Constants
graph_parser.py      - Core parsing logic (41KB)
manifest.json        - Integration metadata
api/                 - REST API endpoints
  __init__.py
  base.py
  models.py
  phase1_api.py
  phase2_api.py
  phase3_api.py
services/            - Business logic services
  (various service files)
```

### Frontend Files (www/visualautoview/)
```
index.html           - Entry point (2KB)
assets/
  main-{hash}.js     - Application bundle (700KB)
  main-{hash}.js.map - Source map (2.2MB)
```

---

## Best Practices

1. **Always clean old builds** before deploying frontend to avoid cache issues
2. **Verify file timestamps** after deployment
3. **Hard refresh browser** after frontend updates
4. **Restart Home Assistant** after backend updates
5. **Check logs** for errors after restart
6. **Test API health** endpoint before testing UI
7. **Keep only latest build** in production to save space and avoid confusion

---

## Quick Reference

| Component | Location | When to Deploy |
|-----------|----------|----------------|
| Backend | `custom_components/visualautoview/` | Python code changes |
| Frontend | `www/visualautoview/` | TypeScript/UI changes |
| Restart Required | Yes | After backend changes |
| Cache Clear Required | Yes | After frontend changes |

**Deployment Time:** ~1-2 minutes  
**Restart Time:** ~30-60 seconds  
**Total Update Time:** ~2-3 minutes
