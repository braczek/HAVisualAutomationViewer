"""All Automations Service - Fetch and manage all automations as mini-graphs."""

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# These imports would come from Phase 1
# from ..graph_parser import AutomationGraph, AutomationGraphParser

_LOGGER = logging.getLogger(__name__)


@dataclass
class MiniGraphData:
    """Lightweight representation of automation graph for dashboard."""

    automation_id: str
    alias: str
    description: str
    enabled: bool
    node_count: int
    edge_count: int
    primary_triggers: List[str]
    primary_actions: List[str]
    execution_time: Optional[float] = None
    last_triggered: Optional[datetime] = None
    graph_data: Optional[Dict[str, Any]] = None  # Simplified graph

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.last_triggered:
            data["last_triggered"] = self.last_triggered.isoformat()
        return data


@dataclass
class AllAutomationsResponse:
    """Response from all automations API."""

    total_count: int
    enabled_count: int
    disabled_count: int
    automations: List[MiniGraphData]
    cache_timestamp: datetime
    page: int = 1
    per_page: int = 50
    total_pages: int = field(default=1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_count": self.total_count,
            "enabled_count": self.enabled_count,
            "disabled_count": self.disabled_count,
            "automations": [auto.to_dict() for auto in self.automations],
            "cache_timestamp": self.cache_timestamp.isoformat(),
            "page": self.page,
            "per_page": self.per_page,
            "total_pages": self.total_pages,
        }


@dataclass
class DashboardFilter:
    """Filter criteria for dashboard."""

    automation_state: Optional[str] = None  # 'enabled', 'disabled', or None
    trigger_platforms: Optional[List[str]] = None  # e.g., ['state', 'time']
    automation_type: Optional[str] = None
    enabled_only: bool = False

    def applies(self, automation: MiniGraphData) -> bool:
        """Check if automation matches filter criteria."""
        # Check automation state
        if self.automation_state == "enabled" and not automation.enabled:
            return False
        if self.automation_state == "disabled" and automation.enabled:
            return False

        # Check enabled_only flag
        if self.enabled_only and not automation.enabled:
            return False

        # Check trigger platforms
        if self.trigger_platforms:
            if not any(
                tp in automation.primary_triggers for tp in self.trigger_platforms
            ):
                return False

        return True


class AllAutomationsService:
    """Service to fetch and manage all automations."""

    def __init__(self, hass):
        """Initialize service."""
        self.hass = hass
        self._cache: Dict[str, MiniGraphData] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes
        _LOGGER.debug("All Automations Service initialized")

    async def get_all_automations(
        self,
        page: int = 1,
        per_page: int = 50,
        filters: Optional[DashboardFilter] = None,
    ) -> AllAutomationsResponse:
        """
        Get all automations as mini-graphs.

        Args:
            page: Page number (1-indexed)
            per_page: Results per page
            filters: Optional filter criteria

        Returns:
            AllAutomationsResponse with paginated results
        """
        try:
            # Build all automations list
            automations = await self._build_all_automations_list()

            # Apply filters if provided
            if filters:
                automations = [auto for auto in automations if filters.applies(auto)]

            # Calculate pagination
            total_count = len(automations)
            total_pages = (total_count + per_page - 1) // per_page

            # Validate page number
            if page < 1:
                page = 1
            if page > total_pages and total_pages > 0:
                page = total_pages

            # Get paginated results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_automations = automations[start_idx:end_idx]

            # Count enabled/disabled
            enabled_count = sum(1 for auto in automations if auto.enabled)
            disabled_count = total_count - enabled_count

            response = AllAutomationsResponse(
                total_count=total_count,
                enabled_count=enabled_count,
                disabled_count=disabled_count,
                automations=paginated_automations,
                cache_timestamp=self._cache_timestamp or datetime.now(),
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

            _LOGGER.debug(
                f"Retrieved {len(paginated_automations)} automations "
                f"(page {page}/{total_pages}, total {total_count})"
            )

            return response

        except Exception as err:
            _LOGGER.error(f"Error fetching all automations: {err}", exc_info=True)
            raise

    async def _build_all_automations_list(self) -> List[MiniGraphData]:
        """
        Build list of all automations with mini-graphs.

        Returns:
            List of MiniGraphData objects
        """
        automations = []

        try:
            # Get automation registry from HA
            automation_entities = self.hass.states.async_all()
            automation_registry = self.hass.data.get("automation", {})

            # In real implementation, would iterate through automation registry
            # and create MiniGraphData for each automation

            _LOGGER.debug(f"Built list of {len(automations)} automations")

        except Exception as err:
            _LOGGER.error(f"Error building automations list: {err}", exc_info=True)
            raise

        return automations

    async def get_automation_stats(self) -> Dict[str, Any]:
        """
        Get global statistics about automations.

        Returns:
            Dictionary with automation statistics
        """
        try:
            automations = await self._build_all_automations_list()

            enabled_count = sum(1 for auto in automations if auto.enabled)
            disabled_count = len(automations) - enabled_count

            avg_nodes = (
                sum(auto.node_count for auto in automations) / len(automations)
                if automations
                else 0
            )
            avg_edges = (
                sum(auto.edge_count for auto in automations) / len(automations)
                if automations
                else 0
            )

            # Count by trigger platform
            trigger_counts = {}
            for auto in automations:
                for trigger in auto.primary_triggers:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

            return {
                "total_automations": len(automations),
                "enabled": enabled_count,
                "disabled": disabled_count,
                "avg_nodes": round(avg_nodes, 2),
                "avg_edges": round(avg_edges, 2),
                "max_nodes": max((auto.node_count for auto in automations), default=0),
                "trigger_platforms": trigger_counts,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as err:
            _LOGGER.error(f"Error getting automation stats: {err}", exc_info=True)
            raise

    def invalidate_cache(self) -> None:
        """Invalidate the automation cache."""
        self._cache.clear()
        self._cache_timestamp = None
        _LOGGER.debug("All automations cache invalidated")


# Example usage in integration:
"""
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    service = AllAutomationsService(hass)
    hass.data[DOMAIN]['all_automations_service'] = service
    
    # Register API endpoint
    async def handle_all_automations(request):
        page = int(request.rel_url.query.get('page', 1))
        per_page = int(request.rel_url.query.get('per_page', 50))
        
        filters = None
        state = request.rel_url.query.get('state')
        if state:
            filters = DashboardFilter(automation_state=state)
        
        response = await service.get_all_automations(page, per_page, filters)
        return web.json_response(response.to_dict())
    
    hass.http.app.router.add_get(
        '/api/visualautoview/automations/all',
        handle_all_automations
    )
"""
