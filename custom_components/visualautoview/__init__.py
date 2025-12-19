"""Visual AutoView - Home Assistant Automation Graph Visualization Integration."""

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import setup_api
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Visual AutoView integration."""
    _LOGGER.warning("========== Visual AutoView: Starting setup ==========")
    _LOGGER.info("Visual AutoView integration is being loaded")

    # Store a reference to the domain
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Set up API endpoints
    _LOGGER.info("Visual AutoView: Setting up API endpoints...")
    api_setup_ok = await setup_api(hass)
    if not api_setup_ok:
        _LOGGER.error("Visual AutoView: FAILED to setup API endpoints!")
    else:
        _LOGGER.warning("Visual AutoView: API setup completed successfully")

    _LOGGER.warning("========== Visual AutoView: Setup complete ==========")
    _LOGGER.info("Visual AutoView: Access the interface at /local/visualautoview/index.html")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Visual AutoView from a config entry."""
    _LOGGER.debug(f"Setting up Visual AutoView config entry: {entry.entry_id}")

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
