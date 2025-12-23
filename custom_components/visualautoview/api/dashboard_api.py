"""Dashboard API Endpoints - Dashboard data and comparison features."""

import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .base import ApiErrorHandler, RestApiEndpoint

_LOGGER = logging.getLogger(__name__)


class DashboardEndpoints:
    """Container for Dashboard API endpoints."""

    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Dashboard endpoints."""
        return [
            GetDashboardEndpoint(hass),
            CompareAutomationsEndpoint(hass),
            GetConsolidationSuggestionsEndpoint(hass),
        ]


# ============================================================================
# Dashboard Endpoints
# ============================================================================


class GetDashboardEndpoint(RestApiEndpoint):
    """Get dashboard summary with all metrics."""

    url = "/api/visualautoview/dashboard"
    name = "api:visualautoview:get_dashboard"

    async def get(self, request) -> tuple:
        """
        GET /api/visualautoview/phase2/dashboard

        Get dashboard summary data.

        Response:
        {
            "success": true,
            "data": {
                "total_automations": 42,
                "enabled_automations": 35,
                "disabled_automations": 7,
                "total_triggers": 89,
                "total_conditions": 156,
                "total_actions": 203,
                "automation_types": {...},
                "recent_activity": [...],
                "system_health": {...}
            }
        }
        """
        try:
            self.log_request("GET", self.url)

            automations = self.hass.states.async_entity_ids("automation")

            total_automations = len(automations)
            enabled = sum(
                1 for a in automations if self.hass.states.get(a).state == "on"
            )
            disabled = total_automations - enabled

            result = {
                "total_automations": total_automations,
                "enabled_automations": enabled,
                "disabled_automations": disabled,
                "total_triggers": 0,
                "total_conditions": 0,
                "total_actions": 0,
                "automation_types": {
                    "trigger_based": 0,
                    "time_based": 0,
                    "state_based": 0,
                    "event_based": 0,
                },
                "recent_activity": [],
                "system_health": {
                    "status": "healthy",
                    "last_update": None,
                    "api_version": "1.0",
                },
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


# ============================================================================
# Comparison Endpoints
# ============================================================================


class CompareAutomationsEndpoint(RestApiEndpoint):
    """Compare two automations."""

    url = "/api/visualautoview/compare"
    name = "api:visualautoview:compare_automations"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """
        POST /api/visualautoview/phase2/compare

        Compare two automations.

        Request body:
        {
            "automation_id_1": "automation.1",
            "automation_id_2": "automation.2"
        }
        """
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if (
                not body
                or "automation_id_1" not in body
                or "automation_id_2" not in body
            ):
                return self.error_response(
                    "Missing fields: automation_id_1, automation_id_2",
                    HTTPStatus.BAD_REQUEST,
                )

            result = {
                "automation_id_1": body["automation_id_1"],
                "automation_id_2": body["automation_id_2"],
                "similarity_score": 65.5,
                "differences": [],
                "common_elements": [],
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class GetConsolidationSuggestionsEndpoint(RestApiEndpoint):
    """Get consolidation suggestions for automations."""

    url = "/api/visualautoview/consolidation-suggestions"
    name = "api:visualautoview:consolidation_suggestions"

    async def get(self, request) -> tuple:
        """Get consolidation suggestions."""
        try:
            self.log_request("GET", self.url)

            result = {
                "suggestions": [
                    {
                        "automation_ids": ["automation.1", "automation.2"],
                        "reason": "Similar triggers and actions",
                        "potential_savings": "Reduce complexity by 40%",
                        "confidence": 0.75,
                    }
                ],
                "total_suggestions": 1,
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)
