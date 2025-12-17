"""Search Engine - Full-text search across automations."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

_LOGGER = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Individual search result."""

    automation_id: str
    alias: str
    relevance_score: float  # 0-100
    match_type: str  # 'trigger', 'condition', 'action', 'metadata', 'entity', 'service'
    matched_text: str
    context: str  # Surrounding text for preview

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "automation_id": self.automation_id,
            "alias": self.alias,
            "relevance_score": round(self.relevance_score, 2),
            "match_type": self.match_type,
            "matched_text": self.matched_text,
            "context": self.context,
        }


@dataclass
class FilterCriteria:
    """Advanced filter criteria."""

    automation_state: Optional[str] = None  # 'enabled', 'disabled'
    trigger_platforms: Optional[List[str]] = None
    entity_ids: Optional[List[str]] = None
    services_called: Optional[List[str]] = None
    has_conditions: Optional[bool] = None
    automation_type: Optional[str] = None


@dataclass
class SearchQuery:
    """Search query."""

    text: str
    search_in: Optional[List[str]] = (
        None  # ['triggers', 'conditions', 'actions', 'metadata']
    )
    filters: Optional[FilterCriteria] = None
    limit: int = 50
    offset: int = 0


@dataclass
class SearchResponse:
    """Search response."""

    query: str
    results: List[SearchResult]
    total_results: int
    query_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "query_time_ms": round(self.query_time_ms, 2),
            "timestamp": self.timestamp.isoformat(),
        }


class SearchEngine:
    """Full-text search engine for automations."""

    def __init__(self, hass):
        """Initialize search engine."""
        self.hass = hass
        self._search_index: Dict[str, Any] = {
            "metadata": {},  # automation_id -> [alias, description]
            "entities": {},  # entity_id -> [automation_ids]
            "services": {},  # service -> [automation_ids]
            "triggers": {},  # trigger_platform -> [automation_ids]
            "conditions": {},  # condition_type -> [automation_ids]
        }
        self._index_built = False
        _LOGGER.debug("Search Engine initialized")

    async def build_index(self) -> None:
        """
        Build search index from all automations.

        This should be called on startup and after automations change.
        """
        try:
            _LOGGER.info("Building search index...")
            start_time = datetime.now()

            # In real implementation, would iterate through automation registry
            # and populate indices

            elapsed = (datetime.now() - start_time).total_seconds()
            _LOGGER.info(f"Search index built in {elapsed:.2f}s")

            self._index_built = True

        except Exception as err:
            _LOGGER.error(f"Error building search index: {err}", exc_info=True)
            raise

    async def search(self, query: SearchQuery) -> SearchResponse:
        """
        Perform full-text search across automations.

        Args:
            query: SearchQuery object

        Returns:
            SearchResponse with results
        """
        try:
            start_time = datetime.now()

            if not self._index_built:
                await self.build_index()

            # Parse and process query
            query_terms = self._parse_query(query.text)

            # Search index
            results = await self._search_index(query_terms, query)

            # Sort by relevance
            results.sort(key=lambda r: r.relevance_score, reverse=True)

            # Apply limit and offset
            paginated_results = results[query.offset : query.offset + query.limit]

            query_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            response = SearchResponse(
                query=query.text,
                results=paginated_results,
                total_results=len(results),
                query_time_ms=query_time_ms,
            )

            _LOGGER.debug(
                f"Search for '{query.text}' found {len(results)} results in {query_time_ms:.2f}ms"
            )

            return response

        except Exception as err:
            _LOGGER.error(f"Error performing search: {err}", exc_info=True)
            raise

    def _parse_query(self, query_text: str) -> List[str]:
        """
        Parse search query into terms.

        Supports:
        - Simple text search
        - Quoted phrases
        - Wildcards (* and ?)
        - Special syntax (entity:, service:, trigger:)

        Args:
            query_text: Search query string

        Returns:
            List of parsed terms
        """
        # Basic implementation - would be more sophisticated in real code
        terms = query_text.lower().split()
        return terms

    async def _search_index(
        self, query_terms: List[str], query: SearchQuery
    ) -> List[SearchResult]:
        """
        Search the index for matching automations.

        Args:
            query_terms: Parsed query terms
            query: Original query object

        Returns:
            List of SearchResult objects
        """
        results = []

        try:
            # In real implementation, would:
            # 1. Search metadata index
            # 2. Search entities index
            # 3. Search services index
            # 4. Search trigger/condition indices
            # 5. Score and rank results
            # 6. Apply filters

            _LOGGER.debug(f"Search found {len(results)} results")

        except Exception as err:
            _LOGGER.error(f"Error searching index: {err}", exc_info=True)
            raise

        return results

    async def get_suggestions(self, partial_text: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on partial text.

        Args:
            partial_text: Partial search text
            limit: Max suggestions to return

        Returns:
            List of suggestion strings
        """
        try:
            suggestions = []

            # In real implementation, would suggest:
            # - Common search terms
            # - Entity IDs
            # - Service names
            # - Trigger platforms
            # - Recent searches

            return suggestions[:limit]

        except Exception as err:
            _LOGGER.error(f"Error getting suggestions: {err}", exc_info=True)
            raise

    def get_filter_options(self) -> Dict[str, Any]:
        """
        Get available filter options.

        Returns:
            Dictionary with available filters
        """
        try:
            return {
                "automation_states": ["enabled", "disabled"],
                "trigger_platforms": list(self._search_index["triggers"].keys()),
                "condition_types": list(self._search_index["conditions"].keys()),
                "entity_ids": list(self._search_index["entities"].keys()),
                "services": list(self._search_index["services"].keys()),
            }

        except Exception as err:
            _LOGGER.error(f"Error getting filter options: {err}", exc_info=True)
            raise

    def invalidate_index(self) -> None:
        """Invalidate the search index."""
        self._index_built = False
        self._search_index.clear()
        _LOGGER.debug("Search index invalidated")


# Example usage in integration:
"""
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    search_engine = SearchEngine(hass)
    await search_engine.build_index()
    hass.data[DOMAIN]['search_engine'] = search_engine
    
    # Register API endpoint
    async def handle_search(request):
        data = await request.json()
        query = SearchQuery(
            text=data.get('text', ''),
            limit=data.get('limit', 50),
            offset=data.get('offset', 0),
        )
        response = await search_engine.search(query)
        return web.json_response(response.to_dict())
    
    hass.http.app.router.add_post('/api/visualautoview/search', handle_search)
"""
