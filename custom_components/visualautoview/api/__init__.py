"""API module for Visual AutoView integration."""

import logging
from homeassistant.core import HomeAssistant

from .base import ApiRegistry
from .phase1_api import Phase1Endpoints
from .phase2_api import Phase2Endpoints
from .phase3_api import Phase3Endpoints

_LOGGER = logging.getLogger(__name__)


async def setup_api(hass: HomeAssistant) -> bool:
    """Set up API endpoints for Visual AutoView."""
    try:
        _LOGGER.debug("Setting up Visual AutoView API")

        # Create registry
        registry = ApiRegistry(hass)

        # Register Phase 1 endpoints
        phase1_endpoints = Phase1Endpoints.create_endpoints(hass)
        for endpoint in phase1_endpoints:
            registry.register(endpoint)

        # Register Phase 2 endpoints
        phase2_endpoints = Phase2Endpoints.create_endpoints(hass)
        for endpoint in phase2_endpoints:
            registry.register(endpoint)

        # Register Phase 3 endpoints
        phase3_endpoints = Phase3Endpoints.create_endpoints(hass)
        for endpoint in phase3_endpoints:
            registry.register(endpoint)

        # Register all endpoints with Home Assistant HTTP
        await registry.register_with_http()

        # Store registry in hass.data
        if "visualautoview" not in hass.data:
            hass.data["visualautoview"] = {}
        hass.data["visualautoview"]["api_registry"] = registry

        _LOGGER.info(
            f"Visual AutoView API setup complete. "
            f"Registered {len(registry.get_endpoints())} endpoints"
        )

        return True

    except Exception as e:
        _LOGGER.error(f"Failed to setup Visual AutoView API: {e}", exc_info=True)
        return False
