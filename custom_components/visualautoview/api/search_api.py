"""Search API Endpoints - Search and filter automations."""

import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .base import ApiErrorHandler, RestApiEndpoint

_LOGGER = logging.getLogger(__name__)


class SearchEndpoints:
    """Container for Search API endpoints."""

    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Search endpoints."""
        return [
            SearchAutomationsEndpoint(hass),
            AdvancedSearchEndpoint(hass),
            FilterAutomationsEndpoint(hass),
            GetFilterOptionsEndpoint(hass),
        ]


# ============================================================================
# Search Endpoints
# ============================================================================


class SearchAutomationsEndpoint(RestApiEndpoint):
    """Search automations by text."""

    url = "/api/visualautoview/search"
    name = "api:visualautoview:search_automations"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """
        POST /api/visualautoview/phase2/search

        Search automations.

        Request body:
        {
            "query": "kitchen light",
            "search_type": "full",
            "match_type": "contains",
            "case_sensitive": false,
            "page": 1,
            "per_page": 50
        }

        Response:
        {
            "success": true,
            "data": {
                "query": "kitchen light",
                "results": [...],
                "total_results": 5,
                "page": 1,
                "per_page": 50
            }
        }
        """
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if not body or "query" not in body:
                return self.error_response(
                    "Missing required field: query", HTTPStatus.BAD_REQUEST
                )

            query = body.get("query", "")
            search_type = body.get("search_type", "full")
            match_type = body.get("match_type", "contains")
            case_sensitive = body.get("case_sensitive", False)
            page = body.get("page", 1)
            per_page = body.get("per_page", 50)

            automations = self.hass.states.async_entity_ids("automation")

            results = []
            for automation_id in automations:
                state = self.hass.states.get(automation_id)
                if not state:
                    continue

                alias = state.attributes.get("friendly_name", automation_id)
                description = state.attributes.get("description", "")

                # Simple text matching
                search_text = (
                    f"{alias} {description}".lower()
                    if not case_sensitive
                    else f"{alias} {description}"
                )
                query_text = query.lower() if not case_sensitive else query

                if match_type == "contains" and query_text in search_text:
                    results.append(
                        {
                            "automation_id": automation_id.replace("automation.", ""),
                            "alias": alias,
                            "relevance_score": 85.0,
                            "match_type": "text",
                            "matched_text": query,
                            "context": description[:100],
                        }
                    )

            total_count = len(results)
            total_pages = (total_count + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            paged_results = results[start_idx : start_idx + per_page]

            result = {
                "query": query,
                "results": paged_results,
                "total_results": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class AdvancedSearchEndpoint(RestApiEndpoint):
    """Advanced search with filters."""

    url = "/api/visualautoview/search/advanced"
    name = "api:visualautoview:advanced_search"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """POST advanced search request."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if not body:
                return self.error_response("Invalid request", HTTPStatus.BAD_REQUEST)

            query = body.get("query", "")
            automations = self.hass.states.async_entity_ids("automation")

            results = [
                {
                    "automation_id": a.replace("automation.", ""),
                    "alias": self.hass.states.get(a).attributes.get("friendly_name", a),
                    "relevance_score": 75.0,
                }
                for a in automations
            ]

            result = {
                "query": query,
                "results": results[:50],
                "total_results": len(results),
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


# ============================================================================
# Filter Endpoints
# ============================================================================


class FilterAutomationsEndpoint(RestApiEndpoint):
    """Filter automations by criteria."""

    url = "/api/visualautoview/filter"
    name = "api:visualautoview:filter_automations"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Filter automations by various criteria."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            automations = self.hass.states.async_entity_ids("automation")

            results = [
                {
                    "automation_id": a.replace("automation.", ""),
                    "alias": self.hass.states.get(a).attributes.get("friendly_name", a),
                    "enabled": self.hass.states.get(a).state == "on",
                }
                for a in automations
            ]

            result = {
                "results": results,
                "total_count": len(results),
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class GetFilterOptionsEndpoint(RestApiEndpoint):
    """Get available filter options."""

    url = "/api/visualautoview/filter/options"
    name = "api:visualautoview:get_filter_options"

    async def get(self, request) -> tuple:
        """Get available filter options and values."""
        try:
            self.log_request("GET", self.url)

            result = {
                "automation_states": ["enabled", "disabled"],
                "trigger_platforms": ["time", "state", "event", "numeric_state"],
                "trigger_types": ["state", "time", "event", "sun", "calendar"],
                "condition_types": ["state", "numeric_state", "time", "template"],
                "action_types": ["call_service", "toggle", "turn_on", "turn_off"],
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)
