"""Phase 1 API Endpoints - Graph Parsing and Core Operations."""

import logging
from typing import Any, Dict, Optional

from homeassistant.const import (
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
)
from homeassistant.core import HomeAssistant

from ..graph_parser import AutomationGraphParser
from .base import ApiErrorHandler, RestApiEndpoint
from .models import GraphRequestParams

_LOGGER = logging.getLogger(__name__)


class Phase1Endpoints:
    """Container for Phase 1 API endpoints."""

    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Phase 1 endpoints."""
        return [
            ParseGraphEndpoint(hass),
            GetAutomationGraphEndpoint(hass),
            ListAutomationsEndpoint(hass),
            ValidateAutomationEndpoint(hass),
        ]


class ParseGraphEndpoint(RestApiEndpoint):
    """Parse a single automation and return its graph."""

    url = "/api/visualautoview/phase1/parse"
    name = "api:visualautoview:parse_graph"

    async def post(self, request) -> tuple:
        """
        POST /api/visualautoview/phase1/parse

        Parse automation YAML and return graph.

        Request body:
        {
            "automation_id": "automation.my_automation",
            "automation_data": {...},  # Full automation config
            "expand_templates": false
        }

        Response:
        {
            "success": true,
            "data": {
                "automation_id": "...",
                "alias": "...",
                "nodes": [...],
                "edges": [...],
                "graph": {...}
            }
        }
        """
        try:
            self.log_request("POST", self.url)
            body = self.parse_json_body(request)

            if not body:
                return self.error_response("Invalid JSON body", HTTP_BAD_REQUEST)

            automation_id = body.get("automation_id")
            automation_data = body.get("automation_data")
            expand_templates = body.get("expand_templates", False)

            if not automation_id or not automation_data:
                return self.error_response(
                    "Missing required fields: automation_id, automation_data",
                    HTTP_BAD_REQUEST,
                )

            # Parse the automation
            parser = AutomationGraphParser()
            graph = parser.parse_automation(automation_data)

            result = {
                "automation_id": automation_id,
                "alias": automation_data.get("alias", automation_id),
                "nodes": [node.to_dict() for node in graph.nodes],
                "edges": [edge.to_dict() for edge in graph.edges],
                "graph": graph.to_dict(),
                "statistics": {
                    "node_count": len(graph.nodes),
                    "edge_count": len(graph.edges),
                    "trigger_count": len(
                        [n for n in graph.nodes if n.type == "trigger"]
                    ),
                    "condition_count": len(
                        [n for n in graph.nodes if n.type == "condition"]
                    ),
                    "action_count": len([n for n in graph.nodes if n.type == "action"]),
                },
            }

            self.log_response(HTTP_OK, "Graph parsed successfully")
            return self.json_response(result, HTTP_OK, "Graph parsed successfully")

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)

    async def get(self, request) -> tuple:
        """GET is not supported for this endpoint."""
        return self.error_response(
            "GET not supported. Use POST with automation data.", HTTP_BAD_REQUEST
        )


class GetAutomationGraphEndpoint(RestApiEndpoint):
    """Retrieve graph for a specific automation from Home Assistant."""

    url = "/api/visualautoview/phase1/automations/{automation_id}/graph"
    name = "api:visualautoview:get_automation_graph"

    async def get(self, request) -> tuple:
        """
        GET /api/visualautoview/phase1/automations/{automation_id}/graph

        Get the graph for a specific automation.

        Query parameters:
        - include_disabled: bool (default: false)
        - max_depth: int (optional)

        Response:
        {
            "success": true,
            "data": {
                "automation_id": "...",
                "alias": "...",
                "enabled": true,
                "nodes": [...],
                "edges": [...],
                "statistics": {...}
            }
        }
        """
        try:
            self.log_request("GET", self.url)

            automation_id = request.match_info.get("automation_id")
            if not automation_id:
                return self.error_response(
                    "Missing automation_id in path", HTTP_BAD_REQUEST
                )

            params = self.get_query_params(request)

            # Get automation from Home Assistant
            automations = self.hass.states.async_entity_ids("automation")
            if (
                f"automation.{automation_id}" not in automations
                and automation_id not in automations
            ):
                return self.error_response(
                    f"Automation not found: {automation_id}", HTTP_NOT_FOUND
                )

            # Get automation config
            automation_state = self.hass.states.get(
                f"automation.{automation_id}"
            ) or self.hass.states.get(automation_id)

            if not automation_state:
                return self.error_response(
                    f"Automation not found: {automation_id}", HTTP_NOT_FOUND
                )

            # Parse the automation
            parser = AutomationGraphParser()
            # Note: In real implementation, fetch actual automation data from config
            graph = parser.parse_automation(
                {
                    "alias": automation_state.attributes.get(
                        "friendly_name", automation_id
                    ),
                    "trigger": [],
                    "condition": [],
                    "action": [],
                }
            )

            result = {
                "automation_id": automation_id,
                "alias": automation_state.attributes.get(
                    "friendly_name", automation_id
                ),
                "enabled": automation_state.state == "on",
                "nodes": [node.to_dict() for node in graph.nodes],
                "edges": [edge.to_dict() for edge in graph.edges],
                "statistics": {
                    "node_count": len(graph.nodes),
                    "edge_count": len(graph.edges),
                },
            }

            self.log_response(HTTP_OK, f"Graph retrieved for {automation_id}")
            return self.json_response(result, HTTP_OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class ListAutomationsEndpoint(RestApiEndpoint):
    """List all automations with basic graph information."""

    url = "/api/visualautoview/phase1/automations"
    name = "api:visualautoview:list_automations"

    async def get(self, request) -> tuple:
        """
        GET /api/visualautoview/phase1/automations

        List all automations with summary information.

        Query parameters:
        - page: int (default: 1)
        - per_page: int (default: 50)
        - enabled_only: bool (default: false)

        Response:
        {
            "success": true,
            "data": {
                "total_count": 42,
                "enabled_count": 35,
                "disabled_count": 7,
                "automations": [
                    {
                        "automation_id": "...",
                        "alias": "...",
                        "enabled": true,
                        "node_count": 5,
                        "edge_count": 4
                    }
                ],
                "page": 1,
                "per_page": 50,
                "total_pages": 1
            }
        }
        """
        try:
            self.log_request("GET", self.url)
            params = self.get_query_params(request)

            page = params.get("page", 1)
            per_page = params.get("per_page", 50)
            enabled_only = params.get("enabled_only", False)

            # Get all automations
            automations = self.hass.states.async_entity_ids("automation")

            automation_list = []
            for automation_id in automations:
                state = self.hass.states.get(automation_id)
                if not state:
                    continue

                is_enabled = state.state == "on"
                if enabled_only and not is_enabled:
                    continue

                automation_list.append(
                    {
                        "automation_id": automation_id.replace("automation.", ""),
                        "alias": state.attributes.get("friendly_name", automation_id),
                        "enabled": is_enabled,
                        "node_count": 0,  # Will be calculated on demand
                        "edge_count": 0,
                    }
                )

            # Pagination
            total_count = len(automation_list)
            total_pages = (total_count + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            paged_automations = automation_list[start_idx:end_idx]

            result = {
                "total_count": total_count,
                "enabled_count": sum(1 for a in automation_list if a["enabled"]),
                "disabled_count": sum(1 for a in automation_list if not a["enabled"]),
                "automations": paged_automations,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            }

            self.log_response(HTTP_OK, f"Listed {len(paged_automations)} automations")
            return self.json_response(result, HTTP_OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class ValidateAutomationEndpoint(RestApiEndpoint):
    """Validate automation YAML and return parse result."""

    url = "/api/visualautoview/phase1/validate"
    name = "api:visualautoview:validate_automation"

    async def post(self, request) -> tuple:
        """
        POST /api/visualautoview/phase1/validate

        Validate automation YAML and return parse result with any errors.

        Request body:
        {
            "automation_data": {...},
            "strict": false
        }

        Response:
        {
            "success": true,
            "data": {
                "valid": true,
                "errors": [],
                "warnings": [],
                "statistics": {
                    "triggers": 1,
                    "conditions": 2,
                    "actions": 3
                }
            }
        }
        """
        try:
            self.log_request("POST", self.url)
            body = self.parse_json_body(request)

            if not body:
                return self.error_response("Invalid JSON body", HTTP_BAD_REQUEST)

            automation_data = body.get("automation_data")
            strict = body.get("strict", False)

            if not automation_data:
                return self.error_response(
                    "Missing required field: automation_data", HTTP_BAD_REQUEST
                )

            errors = []
            warnings = []

            # Basic validation
            if not isinstance(automation_data, dict):
                errors.append("automation_data must be a dictionary")
            else:
                if "trigger" not in automation_data:
                    errors.append("Missing required field: trigger")
                if "action" not in automation_data:
                    errors.append("Missing required field: action")

            # Try to parse
            valid = len(errors) == 0
            statistics = {
                "triggers": 0,
                "conditions": 0,
                "actions": 0,
            }

            if valid:
                try:
                    parser = AutomationGraphParser()
                    graph = parser.parse_automation(automation_data)
                    statistics["triggers"] = len(
                        [n for n in graph.nodes if n.type == "trigger"]
                    )
                    statistics["conditions"] = len(
                        [n for n in graph.nodes if n.type == "condition"]
                    )
                    statistics["actions"] = len(
                        [n for n in graph.nodes if n.type == "action"]
                    )
                except Exception as e:
                    if strict:
                        valid = False
                        errors.append(f"Parse error: {str(e)}")
                    else:
                        warnings.append(f"Parse warning: {str(e)}")

            result = {
                "valid": valid,
                "errors": errors,
                "warnings": warnings,
                "statistics": statistics,
            }

            status = HTTP_OK if valid else HTTP_BAD_REQUEST
            message = "Validation successful" if valid else "Validation failed"
            self.log_response(status, message)
            return self.json_response(result, status, message)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)
