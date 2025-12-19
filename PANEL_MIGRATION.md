# Migrating from iFrame to Native Panel Integration

## What Changed

Your extension now runs as a **native Home Assistant panel** instead of an iframe. This gives you:

✅ **Full access to HA theme system** - Your UI automatically matches HA's theme (light/dark mode, colors)  
✅ **Access to `hass` object** - Direct access to states, services, WebSocket connection  
✅ **No iframe restrictions** - No cross-origin issues, better performance  
✅ **Sidebar integration** - Shows up in HA's sidebar like native features  
✅ **Better UX** - Feels like a native HA feature

## Setup Steps

### 1. Build the Panel

```bash
cd frontend
npm run build
```

This creates `visualautoview-panel.js` in `dist/`

### 2. Copy to Home Assistant

Copy the built files to your HA's `www` directory:

```bash
# On Windows PowerShell
Copy-Item -Path ".\frontend\dist\*" -Destination "\\YOUR_HA_IP\config\www\visualautoview\" -Recurse -Force

# On Linux/Mac
cp -r frontend/dist/* /config/www/visualautoview/
```

Or if using Docker/Add-on, use the File Editor add-on to upload files to `/config/www/visualautoview/`

### 3. Restart Home Assistant

The integration will now register a panel in your sidebar called "AutoView" with a graph icon.

### 4. Access Your Panel

After restart, look for **AutoView** in your Home Assistant sidebar (left menu). Click it to open your visualization tool.

## Key Differences

### Before (iframe):
- Accessed via `/local/visualautoview/index.html`
- Limited theme access (had to guess from parent)
- No direct access to HA internals
- Cross-origin restrictions

### After (Native Panel):
- Accessed via sidebar or `/visualautoview`
- Full theme integration via `hass.themes`
- Direct access to states via `this.hass.states`
- Can call services via `this.hass.callService()`
- Access WebSocket via `this.hass.connection`

## Using the `hass` Object

In your components, you now have access to:

```typescript
// Get all automations from states
const automations = Object.values(this.hass.states)
  .filter(entity => entity.entity_id.startsWith('automation.'));

// Call a service
await this.hass.callService('automation', 'trigger', {
  entity_id: 'automation.my_automation'
});

// Get theme info
const isDark = this.hass.themes?.darkMode;
const primaryColor = this.hass.themes?.default_theme?.primary_color;

// Listen to WebSocket events
this.hass.connection.subscribeEvents((event) => {
  console.log('State changed:', event);
}, 'state_changed');
```

## Customization

### Change Panel Icon/Title

Edit [__init__.py](__init__.py#L46-L50):

```python
hass.components.frontend.async_register_built_in_panel(
    component_name="custom",
    sidebar_title="My Title",      # Change this
    sidebar_icon="mdi:chart-line",  # Change this (any MDI icon)
    # ...
)
```

### Access Theme Variables

All HA CSS variables are available in your components:

```css
.my-element {
  background: var(--card-background-color);
  color: var(--primary-text-color);
  border: 1px solid var(--divider-color);
}
```

Common variables:
- `--primary-color` - Main theme color
- `--accent-color` - Accent color
- `--primary-text-color` - Text color
- `--primary-background-color` - Background
- `--card-background-color` - Card backgrounds
- `--divider-color` - Borders/dividers

## Troubleshooting

### Panel not showing in sidebar
1. Check HA logs for errors during startup
2. Ensure `visualautoview-panel.js` exists in `/config/www/visualautoview/`
3. Clear browser cache (Ctrl+Shift+R)
4. Restart HA

### Theme not applying
The `hass` object is passed to your component. Make sure:
1. Your component accepts `@property({ attribute: false }) hass: any;`
2. You update when `hass` changes in `updated()` lifecycle method

### Old iframe still loading
The old `index.html` still works for backwards compatibility. To remove it, just don't build/deploy it.

## Next Steps

- Update your components to use `this.hass.states` instead of API calls
- Leverage HA's built-in components (ha-card, ha-button, etc.)
- Use HA's WebSocket for real-time updates
