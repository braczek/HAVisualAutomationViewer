"""Export API Endpoints - Export automations and graphs."""

import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .base import ApiErrorHandler, RestApiEndpoint

_LOGGER = logging.getLogger(__name__)


class ExportEndpoints:
    """Container for Export API endpoints."""

    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Export endpoints."""
        return [
            ExportAutomationsEndpoint(hass),
            ExportGraphEndpoint(hass),
        ]


# ============================================================================
# Export Endpoints
# ============================================================================


class ExportAutomationsEndpoint(RestApiEndpoint):
    """Export automations in various formats."""

    url = "/api/visualautoview/export"
    name = "api:visualautoview:export_automations"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """
        POST /api/visualautoview/phase2/export

        Export automations.

        Request body:
        {
            "format": "json",  # json, csv, pdf
            "include_graphs": true,
            "include_metadata": true,
            "automation_ids": ["automation.1", "automation.2"]
        }
        """
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if not body:
                return self.error_response("Invalid request", HTTPStatus.BAD_REQUEST)

            export_format = body.get("format", "json")
            automation_ids = body.get("automation_ids", [])
            include_graphs = body.get("include_graphs", True)
            include_metadata = body.get("include_metadata", True)

            if not automation_ids:
                return self.error_response(
                    "No automation IDs provided", HTTPStatus.BAD_REQUEST
                )

            if export_format not in ("json", "csv", "pdf"):
                return self.error_response(
                    f"Invalid format: {export_format}", HTTPStatus.BAD_REQUEST
                )

            # Get automation data for export
            export_data = []
            _LOGGER.debug(f"Exporting automations: {automation_ids}")
            
            automation_component = self.hass.data.get("automation")
            
            for auto_id in automation_ids:
                state = self.hass.states.get(auto_id)
                _LOGGER.debug(f"Checking automation {auto_id}, state: {state}")
                
                if not state:
                    _LOGGER.warning(f"Automation {auto_id} not found in state machine")
                    continue
                
                automation_data = {
                    "entity_id": auto_id,
                    "name": state.attributes.get("friendly_name", auto_id),
                    "state": state.state,
                }
                
                # Get detailed configuration if available
                if automation_component:
                    for entity in automation_component.entities:
                        if entity.entity_id == auto_id:
                            if include_metadata:
                                config = {}
                                
                                # Get triggers
                                if hasattr(entity, "_trigger_config"):
                                    config["triggers"] = entity._trigger_config
                                elif hasattr(entity, "trigger"):
                                    config["triggers"] = entity.trigger
                                
                                # Get conditions
                                if hasattr(entity, "_cond_config"):
                                    config["conditions"] = entity._cond_config
                                
                                # Get actions
                                if hasattr(entity, "_action_config"):
                                    config["actions"] = entity._action_config
                                elif hasattr(entity, "action_script") and hasattr(
                                    entity.action_script, "sequence"
                                ):
                                    config["actions"] = entity.action_script.sequence
                                
                                # Get description
                                if hasattr(entity, "description"):
                                    config["description"] = entity.description
                                
                                automation_data["configuration"] = config
                            break
                
                if include_metadata and "configuration" not in automation_data:
                    # Fallback to state attributes if config not found
                    automation_data["attributes"] = dict(state.attributes)
                
                export_data.append(automation_data)

            result = {
                "format": export_format,
                "status": "completed",
                "data": export_data,
                "count": len(export_data),
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class ExportGraphEndpoint(RestApiEndpoint):
    """Export automation graph in various formats."""

    url = "/api/visualautoview/export/graph/{automation_id}"
    name = "api:visualautoview:export_graph"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Export graph for specific automation."""
        try:
            self.log_request("POST", self.url)

            automation_id = request.match_info.get("automation_id")
            body = await self.parse_json_body(request)

            result = {
                "export_id": f"export_{automation_id}",
                "automation_id": automation_id,
                "format": body.get("format", "json") if body else "json",
                "status": "completed",
                "data": {
                    "nodes": [],
                    "edges": [],
                },
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)
