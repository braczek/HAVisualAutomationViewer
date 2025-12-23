"""API module for Visual AutoView integration."""

import logging

from homeassistant.core import HomeAssistant

from .analytics_api import AnalyticsEndpoints
from .automation_api import AutomationEndpoints
from .base import ApiRegistry
from .dashboard_api import DashboardEndpoints
from .execution_api import ExecutionEndpoints
from .export_api import ExportEndpoints
from .relationship_api import RelationshipEndpoints
from .search_api import SearchEndpoints
from .template_api import TemplateEndpoints
from .theme_api import ThemeEndpoints

_LOGGER = logging.getLogger(__name__)


async def setup_api(hass: HomeAssistant) -> bool:
    """Set up API endpoints for Visual AutoView."""
    try:
        _LOGGER.warning("Visual AutoView API: Starting endpoint registration")
        _LOGGER.info("Visual AutoView API: CORS support enabled for mobile apps")

        # Create registry
        registry = ApiRegistry(hass)
        _LOGGER.info("Visual AutoView API: Registry created")

        # Define all endpoint groups
        endpoint_groups = [
            ("Automation", AutomationEndpoints),
            ("Search", SearchEndpoints),
            ("Export", ExportEndpoints),
            ("Theme", ThemeEndpoints),
            ("Dashboard", DashboardEndpoints),
            ("Analytics", AnalyticsEndpoints),
            ("Relationship", RelationshipEndpoints),
            ("Execution", ExecutionEndpoints),
            ("Template", TemplateEndpoints),
        ]

        # Register all endpoint groups
        total_endpoints = 0
        for group_name, endpoint_class in endpoint_groups:
            _LOGGER.info(f"Visual AutoView API: Creating {group_name} endpoints")
            endpoints = endpoint_class.create_endpoints(hass)
            _LOGGER.info(
                f"Visual AutoView API: Created {len(endpoints)} {group_name} endpoints"
            )
            for endpoint in endpoints:
                registry.register(endpoint)
                _LOGGER.debug(f"  - Registered: {endpoint.url}")
            total_endpoints += len(endpoints)

        # Register all endpoints with Home Assistant HTTP
        _LOGGER.warning(
            "Visual AutoView API: Registering endpoints with Home Assistant HTTP..."
        )
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

        _LOGGER.info(
            "Visual AutoView API: All endpoints support CORS (Access-Control-Allow-Origin: *)"
        )
        _LOGGER.info(
            "Visual AutoView API: Authentication: requires_auth=True on all endpoints"
        )
        _LOGGER.info("Visual AutoView API: Mobile app support: enabled")

        return True

    except Exception as e:
        _LOGGER.error(f"Failed to setup Visual AutoView API: {e}", exc_info=True)
        return False
