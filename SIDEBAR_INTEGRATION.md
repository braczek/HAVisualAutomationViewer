# Adding Visual AutoView to Home Assistant Sidebar

## ✅ NEW: Direct URL Access with Automation ID

You can now link directly to a specific automation's graph using URL parameters!

### URL Format
```
http://192.168.1.7:8123/local/visualautoview/index.html?automation=AUTOMATION_ID
```

### How to Get the Automation ID

**Method 1: From Automation Edit URL**

When editing an automation, the URL looks like:
```
http://192.168.1.7:8123/config/automation/edit/1765388366505
```

The automation ID is the number at the end: `1765388366505`

**Method 2: From Entity ID**

If your automation has an entity ID like `automation.bedroom_lights`, you can use:
```
http://192.168.1.7:8123/local/visualautoview/index.html?automation=bedroom_lights
```

### Examples

**Using numeric ID:**
```
http://192.168.1.7:8123/local/visualautoview/index.html?automation=1765388366505
```

**Using entity name:**
```
http://192.168.1.7:8123/local/visualautoview/index.html?automation=bedroom_lights
```

**Opening in analytics view:**
```
http://192.168.1.7:8123/local/visualautoview/index.html?automation=bedroom_lights&view=analytics
```

### Creating Bookmarklets

You can create a bookmarklet to quickly view the graph of the automation you're editing:

**JavaScript Bookmarklet:**
```javascript
javascript:(function(){
  const match = window.location.href.match(/\/automation\/edit\/(\d+)/);
  if (match) {
    window.open(`/local/visualautoview/index.html?automation=${match[1]}`, '_blank');
  } else {
    alert('Not on an automation edit page');
  }
})();
```

**How to use:**
1. Create a new bookmark in your browser
2. Set the name to "View Automation Graph"
3. Paste the JavaScript code above as the URL
4. When viewing/editing an automation, click the bookmarklet
5. The graph opens in a new tab!

---

## Current Access Method

Currently, you need to access the graph viewer directly via URL:
```
http://192.168.1.7:8123/local/visualautoview/index.html
```

## Add to Sidebar

### Method 1: Using Lovelace Dashboard (Recommended)

Create a new dashboard or add to an existing one:

1. Go to Settings → Dashboards → Add Dashboard
2. Name it "Automation Graph" 
3. Create a new dashboard with this configuration:

Or add a view to existing dashboard:

```yaml
# In your dashboard configuration
views:
  - title: Automation Graph
    path: automation-graph
    icon: mdi:graph
    type: iframe
    url: /local/visualautoview/index.html
```

### Method 2: Custom Button Card

Add this card to any dashboard:

```yaml
type: button
name: Automation Graph Viewer
icon: mdi:graph-outline
tap_action:
  action: navigate
  navigation_path: /local/visualautoview/index.html
```

### Method 3: Webpage Card (Shows inline)

```yaml
type: iframe
url: /local/visualautoview/index.html
aspect_ratio: 100%
```

### Method 4: Using configuration.yaml (If panel_iframe is available)

**Note:** Only if your Home Assistant version supports `panel_iframe`:

```yaml
# This may not work on all HA versions
panel_iframe:
  visualautoview:
    title: "Automation Graph"
    icon: mdi:graph
    url: "/local/visualautoview/index.html"
    require_admin: false
```

If you get an error about `panel_iframe` not found, use Method 1 or 2 instead.

**Steps for Dashboard Method:**
1. Go to Settings → Dashboards in Home Assistant
2. Click "Add Dashboard" (or edit existing)
3. Add a view with type `iframe` pointing to `/local/visualautoview/index.html`
4. The automation graph will appear as a dashboard tab

**Steps for Button Method:**
1. Edit any dashboard
2. Add a new card
3. Choose "Manual" or "Button Card"
4. Paste the button card YAML above
5. Save - clicking the button opens the graph viewer

**Recommended:** Use the **Bookmarklet** method (see above) - it's the easiest way to jump from editing an automation directly to viewing its graph!

## Alternative: Add as Custom Panel (Advanced)

For a more integrated experience with "View Graph" in automation editor menus, you would need to:

1. Create a custom Lovelace card
2. Register it in the frontend
3. Add menu item hooks to automation editor

This requires additional frontend development and is more complex.

## Temporary Workaround

For now, to view an automation's graph:

1. **Note the automation ID** from the URL when editing:
   - Example: `http://192.168.1.7:8123/config/automation/edit/1765388366505`
   - The ID is: `1765388366505`

2. **Open the graph viewer:**
   ```
   http://192.168.1.7:8123/local/visualautoview/index.html
   ```

3. **Select the automation** from the dropdown list

## Future Enhancement: Context Menu Integration

To add "View Graph" to the automation editor's three-dot menu would require:

### Option 1: Custom Frontend Card/Plugin
Create a custom frontend integration that:
- Registers with Home Assistant's frontend
- Adds menu items to automation editor
- Opens graph in modal/new window

### Option 2: Browser Extension
Create a browser extension that:
- Detects automation edit pages
- Adds "View Graph" button
- Links to graph viewer with automation ID

### Option 3: Bookmarklet
Create a bookmarklet that:
- Extracts automation ID from current page
- Opens graph viewer in new tab/window

Would you like me to implement any of these options?

## Quick Access Tips

### 1. Browser Bookmark
Create a bookmark to the graph viewer for quick access

### 2. Home Assistant Dashboard Card
Add a button card to a dashboard:

```yaml
type: button
name: Automation Graph Viewer
icon: mdi:graph
tap_action:
  action: navigate
  navigation_path: /local/visualautoview/index.html
```

### 3. URL Template for Direct Access
If you know the automation entity ID, you can use:
```
http://192.168.1.7:8123/local/visualautoview/index.html?automation=automation.your_automation_name
```

Note: This would require frontend modifications to parse URL parameters.

## Recommended Immediate Solution

**Add to sidebar using panel_iframe** (instructions above) - this is the quickest and easiest way to make it easily accessible from within Home Assistant.
