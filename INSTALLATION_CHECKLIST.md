# Installation Checklist

Use this checklist to ensure a smooth installation of Visual AutoView.

## Pre-Installation

- [ ] **Home Assistant is running** (version 2023.1.0 or newer)
- [ ] **I have access** to the Home Assistant configuration directory
- [ ] **I have admin access** to Home Assistant
- [ ] **Optional:** I have created a long-lived access token for testing

## Choose Installation Method

Select ONE method:

- [ ] **One-Line Install** (fastest - 30 seconds)
- [ ] **Script Install** (more control - 2 minutes)
- [ ] **HACS Install** (best for updates - 5 minutes)
- [ ] **Manual Install** (full control - 10 minutes)

## Installation Steps

### If Using One-Line Install

- [ ] Opened PowerShell (Windows) or Terminal (Linux/macOS)
- [ ] Copied and pasted the one-line command
- [ ] Script completed successfully
- [ ] Noted the Home Assistant directory found

### If Using Script Install

- [ ] Downloaded installation script
- [ ] Reviewed script (optional but recommended)
- [ ] Made script executable (Linux/macOS only)
- [ ] Ran script with desired options
- [ ] Script completed successfully

### If Using HACS

- [ ] HACS is installed and configured
- [ ] Added custom repository URL
- [ ] Found Visual AutoView in HACS
- [ ] Downloaded integration
- [ ] Restarted Home Assistant
- [ ] Added integration via UI

### If Using Manual Install

- [ ] Downloaded latest release or cloned repository
- [ ] Created `custom_components` directory (if needed)
- [ ] Copied `visualautoview` folder to correct location
- [ ] Verified all files are present
- [ ] Set correct permissions (Linux/Docker)
- [ ] Restarted Home Assistant

## Post-Installation

- [ ] **Home Assistant restarted** completely
- [ ] **Checked logs** for "Visual AutoView API setup complete"
- [ ] **Verified endpoint count:** "Registered 45 endpoints"
- [ ] **Ran verification script** (if available)
  ```bash
  ./verify_install.sh  # or .ps1 on Windows
  ```

## Configuration

- [ ] Opened **Configuration** → **Integrations**
- [ ] Visual AutoView appears in integrations list
- [ ] Integration status shows "Configured" or "Ready"
- [ ] No error messages in logs

## Testing

- [ ] **Created long-lived access token** (if not done earlier)
  - Profile → Long-Lived Access Tokens → Create Token
  
- [ ] **Tested health endpoint:**
  ```bash
  curl -H "Authorization: Bearer YOUR_TOKEN" \
       http://YOUR_HA_IP:8123/api/visualautoview/health
  ```
  
- [ ] **Tested automations endpoint:**
  ```bash
  curl -H "Authorization: Bearer YOUR_TOKEN" \
       http://YOUR_HA_IP:8123/api/visualautoview/automations
  ```

- [ ] **Received valid JSON responses** (not 404 or errors)

## Optional: Frontend Setup

Only if you want the web interface:

- [ ] Node.js 18+ is installed
- [ ] Ran installation with `-DevMode` or `--dev` flag
- [ ] Frontend built successfully
- [ ] Files copied to `/config/www/visualautoview/`
- [ ] Accessed at `http://YOUR_HA_IP:8123/local/visualautoview/`
- [ ] Web interface loads without errors

## Documentation Review

- [ ] Read [QUICK_START.md](QUICK_START.md)
- [ ] Bookmarked [API_IMPLEMENTATION_COMPLETE.md](API_IMPLEMENTATION_COMPLETE.md)
- [ ] Reviewed available endpoints and features
- [ ] Understand how to use the integration

## Troubleshooting (If Needed)

If you encounter issues:

- [ ] Checked [INSTALLATION.md](INSTALLATION.md) troubleshooting section
- [ ] Reviewed Home Assistant logs for errors
- [ ] Verified file permissions (Linux/Docker)
- [ ] Confirmed Home Assistant version compatibility
- [ ] Searched GitHub issues for similar problems
- [ ] Created new issue with details if problem persists

## Success Criteria

You should have:

✅ Visual AutoView in Configuration → Integrations  
✅ "Visual AutoView API setup complete" in logs  
✅ 45 endpoints registered  
✅ API endpoints responding to requests  
✅ No errors in Home Assistant logs  

## Next Steps

- [ ] Explore automation visualization features
- [ ] Try different API endpoints
- [ ] Set up automations you want to visualize
- [ ] Test search and filter capabilities
- [ ] Experiment with analytics features
- [ ] Share feedback on GitHub

## Share Your Success! 🎉

If everything works:

- [ ] Star the repository on GitHub ⭐
- [ ] Share with the Home Assistant community
- [ ] Provide feedback or suggestions
- [ ] Report any bugs you find

---

**Need Help?**

- GitHub Issues: https://github.com/braczek/HAVisualAutomationViewer/issues
- Documentation: [README.md](README.md)
- Community: Home Assistant Forums

**Congratulations on installing Visual AutoView!** 🚀
