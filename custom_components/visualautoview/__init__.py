"""Visual AutoView - Home Assistant Automation Graph Visualization Integration."""

import logging
import os
from typing import Any

from homeassistant import config_entries
from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import setup_api
from .auth_diagnostics import AuthDiagnostics
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Visual AutoView integration."""
    _LOGGER.info("Visual AutoView integration is being loaded")

    # Store a reference to the domain
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Set up API endpoints
    api_setup_ok = await setup_api(hass)
    if not api_setup_ok:
        _LOGGER.warning("FAILED to setup API endpoints")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Visual AutoView from a config entry."""
    _LOGGER.warning(
        "========== Visual AutoView: Starting setup from config entry =========="
    )
    _LOGGER.info(f"Visual AutoView: Setting up config entry: {entry.entry_id}")

    # Log authentication diagnostics
    AuthDiagnostics.log_diagnostics(hass)

    # Store a reference to the domain
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Register static path for frontend files
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend_dist")
    if os.path.exists(frontend_path):
        _LOGGER.info(f"Visual AutoView: Registering static path: {frontend_path}")
        await hass.http.async_register_static_paths(
            [StaticPathConfig("/visualautoview_static", frontend_path, True)]
        )
    else:
        _LOGGER.error(f"Visual AutoView: Frontend path not found: {frontend_path}")

    # Set up API endpoints
    _LOGGER.info("Visual AutoView: Setting up API endpoints...")
    api_setup_ok = await setup_api(hass)
    if not api_setup_ok:
        _LOGGER.error("Visual AutoView: FAILED to setup API endpoints!")
    else:
        _LOGGER.warning("Visual AutoView: API setup completed successfully")

    # Register the custom panel in HA's sidebar
    _LOGGER.info("Visual AutoView: Registering frontend panel...")
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="AutoView",
        sidebar_icon="mdi:graph",
        frontend_url_path="visualautoview",
        config={
            "_panel_custom": {
                "name": "visualautoview-panel",
                "module_url": "/visualautoview_static/visualautoview-panel.js",
            }
        },
        require_admin=False,
    )

    _LOGGER.warning("========== Visual AutoView: Setup complete ==========")
    _LOGGER.info("Visual AutoView: Panel registered in sidebar")

    # Store config entry reference
    hass.data[DOMAIN][entry.entry_id] = {
        "config_entry": entry,
    }

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading Visual AutoView config entry: {entry.entry_id}")

    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
