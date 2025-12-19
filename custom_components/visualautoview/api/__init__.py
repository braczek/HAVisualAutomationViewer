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
        _LOGGER.warning("Visual AutoView API: Starting endpoint registration")

        # Create registry
        registry = ApiRegistry(hass)
        _LOGGER.info("Visual AutoView API: Registry created")

        # Register Phase 1 endpoints
        _LOGGER.info("Visual AutoView API: Creating Phase 1 endpoints")
        phase1_endpoints = Phase1Endpoints.create_endpoints(hass)
        _LOGGER.info(f"Visual AutoView API: Created {len(phase1_endpoints)} Phase 1 endpoints")
        for endpoint in phase1_endpoints:
            registry.register(endpoint)

        # Register Phase 2 endpoints
        _LOGGER.info("Visual AutoView API: Creating Phase 2 endpoints")
        phase2_endpoints = Phase2Endpoints.create_endpoints(hass)
        _LOGGER.info(f"Visual AutoView API: Created {len(phase2_endpoints)} Phase 2 endpoints")
        for endpoint in phase2_endpoints:
            registry.register(endpoint)

        # Register Phase 3 endpoints
        _LOGGER.info("Visual AutoView API: Creating Phase 3 endpoints")
        phase3_endpoints = Phase3Endpoints.create_endpoints(hass)
        _LOGGER.info(f"Visual AutoView API: Created {len(phase3_endpoints)} Phase 3 endpoints")
        for endpoint in phase3_endpoints:
            registry.register(endpoint)

        # Register all endpoints with Home Assistant HTTP
        _LOGGER.warning("Visual AutoView API: Registering endpoints with Home Assistant HTTP...")
        await registry.register_with_http()

        # Store registry in hass.data
        if "visualautoview" not in hass.data:
            hass.data["visualautoview"] = {}
        hass.data["visualautoview"]["api_registry"] = registry

        endpoint_count = len(registry.get_endpoints())
        _LOGGER.warning(
            f"========== Visual AutoView API: Successfully registered {endpoint_count} endpoints =========="
        )
        
        # Log all registered URLs
        for url in registry.get_endpoints().keys():
            _LOGGER.warning(f"  ✓ Registered: {url}")

        return True

    except Exception as e:
        _LOGGER.error(f"Failed to setup Visual AutoView API: {e}", exc_info=True)
        return False
