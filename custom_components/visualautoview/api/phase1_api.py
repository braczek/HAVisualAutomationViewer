"""Phase 1 API Endpoints - Graph Parsing and Core Operations."""

import logging
from http import HTTPStatus
from typing import Any, Dict, Optional

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
            HealthCheckEndpoint(hass),
            ParseGraphEndpoint(hass),
            GetAutomationGraphEndpoint(hass),
            ListAutomationsEndpoint(hass),
            ValidateAutomationEndpoint(hass),
        ]


class HealthCheckEndpoint(RestApiEndpoint):
    """Simple health check endpoint."""

    url = "/api/visualautoview/health"
    name = "api:visualautoview:health"

    async def get(self, request) -> tuple:
        """GET /api/visualautoview/health - Health check endpoint."""
        try:
            result = {
                "status": "ok",
                "version": "1.0.1",
                "integration": "visualautoview",
            }
            return self.json_response(result, HTTPStatus.OK)
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


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
                return self.error_response("Invalid JSON body", HTTPStatus.BAD_REQUEST)

            automation_id = body.get("automation_id")
            automation_data = body.get("automation_data")
            expand_templates = body.get("expand_templates", False)

            if not automation_id or not automation_data:
                return self.error_response(
                    "Missing required fields: automation_id, automation_data",
                    HTTPStatus.BAD_REQUEST,
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

            self.log_response(HTTPStatus.OK, "Graph parsed successfully")
            return self.json_response(result, HTTPStatus.OK, "Graph parsed successfully")

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)

    async def get(self, request) -> tuple:
        """GET is not supported for this endpoint."""
        return self.error_response(
            "GET not supported. Use POST with automation data.", HTTPStatus.BAD_REQUEST
        )


class GetAutomationGraphEndpoint(RestApiEndpoint):
    """Retrieve graph for a specific automation from Home Assistant."""

    url = "/api/visualautoview/phase1/automations/{automation_id}/graph"
    name = "api:visualautoview:get_automation_graph"

    async def get(self, request, automation_id=None) -> tuple:
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

            # Get automation_id from either parameter or match_info
            if not automation_id:
                automation_id = request.match_info.get("automation_id")
            
            if not automation_id:
                return self.error_response(
                    "Missing automation_id in path", HTTPStatus.BAD_REQUEST
                )

            # Get automation from Home Assistant
            automations = self.hass.states.async_entity_ids("automation")
            _LOGGER.info(f"Looking for automation: automation.{automation_id}")
            
            if (
                f"automation.{automation_id}" not in automations
                and automation_id not in automations
            ):
                return self.error_response(
                    f"Automation not found: {automation_id}", HTTPStatus.NOT_FOUND
                )

            # Get automation config state
            automation_state = self.hass.states.get(
                f"automation.{automation_id}"
            ) or self.hass.states.get(automation_id)

            if not automation_state:
                return self.error_response(
                    f"Automation not found: {automation_id}", HTTPStatus.NOT_FOUND
                )

            # Try to get automation configuration from automations component
            automation_data = None
            
            # Method 1: Get from automation entity's raw_config
            try:
                automation_component = self.hass.data.get("automation")
                if automation_component:
                    entity_id = f"automation.{automation_id}" if not automation_id.startswith("automation.") else automation_id
                    
                    # Get entity from component
                    if hasattr(automation_component, 'get_entity'):
                        entity = automation_component.get_entity(entity_id)
                        if entity and hasattr(entity, 'raw_config'):
                            automation_data = entity.raw_config
                            _LOGGER.info(f"Got automation config from raw_config: {automation_data}")
                    
            except Exception as e:
                _LOGGER.error(f"Error accessing automation component: {e}", exc_info=True)
            
            # Method 2: Fallback to empty data
            if not automation_data:
                _LOGGER.warning("Could not find automation config, using empty data")
                automation_data = {
                    "alias": automation_state.attributes.get("friendly_name", automation_id),
                    "triggers": [],
                    "conditions": [],
                    "actions": [],
                }
            
            _LOGGER.info(f"Final automation data keys: {automation_data.keys() if automation_data else 'None'}")
            _LOGGER.info(f"Triggers count: {len(automation_data.get('triggers', automation_data.get('trigger', [])))}, Conditions count: {len(automation_data.get('conditions', automation_data.get('condition', [])))}, Actions count: {len(automation_data.get('actions', automation_data.get('action', [])))}")

            # Parse the automation
            parser = AutomationGraphParser()
            try:
                graph = parser.parse_automation(automation_data)
            except Exception as parse_error:
                _LOGGER.error(f"Error parsing automation: {parse_error}", exc_info=True)
                return self.error_response(
                    f"Failed to parse automation: {str(parse_error)}", 
                    HTTPStatus.INTERNAL_SERVER_ERROR
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
                    "trigger_count": len(automation_data.get("triggers", [])),
                    "condition_count": len(automation_data.get("conditions", [])),
                    "action_count": len(automation_data.get("actions", [])),
                },
            }

            self.log_response(HTTPStatus.OK, f"Graph retrieved for {automation_id}")
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            _LOGGER.error(f"Error in GetAutomationGraphEndpoint: {e}", exc_info=True)
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _get_automation_configs(self) -> list:
        """Get all automation configs from Home Assistant."""
        try:
            # Access the automation storage/config
            from homeassistant.components.automation import automations_with_entity_id
            configs = []
            
            # Try to get from hass.data
            if "automation" in self.hass.data:
                return self.hass.data["automation"].get("configs", [])
            
            return configs
        except Exception as e:
            _LOGGER.warning(f"Could not access automation configs: {e}")
            return []


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
            parser = AutomationGraphParser()

            for automation_id in automations:
                state = self.hass.states.get(automation_id)
                if not state:
                    continue

                is_enabled = state.state == "on"
                if enabled_only and not is_enabled:
                    continue

                # Try to get actual automation config
                node_count = 0
                edge_count = 0
                
                try:
                    # Get the automation configuration from the component
                    automation_config = await self._get_automation_config(automation_id)
                    
                    if automation_config:
                        # Parse automation to get actual node/edge counts
                        graph = parser.parse_automation(automation_config)
                        node_count = len(graph.nodes)
                        edge_count = len(graph.edges)
                    
                except Exception as e:
                    _LOGGER.debug(f"Could not parse automation {automation_id}: {e}")
                    # Keep default 0 values

                automation_list.append(
                    {
                        "automation_id": automation_id.replace("automation.", ""),
                        "alias": state.attributes.get("friendly_name", automation_id),
                        "enabled": is_enabled,
                        "node_count": node_count,
                        "edge_count": edge_count,
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

            self.log_response(HTTPStatus.OK, f"Listed {len(paged_automations)} automations")
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)

    async def _get_automation_config(self, automation_id: str) -> Optional[Dict[str, Any]]:
        """Get automation configuration from Home Assistant.
        
        Args:
            automation_id: The automation entity ID (e.g., 'automation.my_automation')
            
        Returns:
            Automation configuration dictionary or None if not found
        """
        try:
            # Clean automation_id
            clean_id = automation_id.replace("automation.", "")
            
            # Try to get automation config from automation component
            automation_component = self.hass.data.get("automation")
            if automation_component:
                # Look for automation entity in component
                for entity in automation_component.entities:
                    if entity.entity_id == automation_id:
                        # Try to extract config from entity
                        config = {
                            "id": clean_id,
                            "alias": entity.name or clean_id,
                        }
                        
                        # Extract triggers
                        if hasattr(entity, "_trigger_config"):
                            config["trigger"] = entity._trigger_config
                        elif hasattr(entity, "trigger"):
                            config["trigger"] = entity.trigger
                        
                        # Extract conditions
                        if hasattr(entity, "_cond_config"):
                            config["condition"] = entity._cond_config
                        
                        # Extract actions
                        if hasattr(entity, "_action_config"):
                            config["action"] = entity._action_config
                        elif hasattr(entity, "action_script") and hasattr(entity.action_script, "sequence"):
                            config["action"] = entity.action_script.sequence
                        
                        # Description
                        if hasattr(entity, "description"):
                            config["description"] = entity.description
                        
                        return config if (config.get("trigger") or config.get("action")) else None
            
            # Fallback: try to read from attributes
            state = self.hass.states.get(automation_id)
            if state and state.attributes:
                return {
                    "id": clean_id,
                    "alias": state.attributes.get("friendly_name", clean_id),
                    "trigger": [],  # Minimal config
                    "action": [],
                }
            
            return None
            
        except Exception as e:
            _LOGGER.debug(f"Error getting automation config for {automation_id}: {e}")
            return None


class ValidateAutomationEndpoint(RestApiEndpoint):
    """Validate automation YAML and return parse result."""

    url = "/api/visualautoview/phase1/validate"
    name = "api:visualautoview:validate_automation"

    async def get(self, request) -> tuple:
        """GET not supported for validation - use POST."""
        return self.error_response(
            "GET not supported. Use POST with automation data.", HTTPStatus.BAD_REQUEST
        )

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
                return self.error_response("Invalid JSON body", HTTPStatus.BAD_REQUEST)

            automation_data = body.get("automation_data")
            strict = body.get("strict", False)

            if not automation_data:
                return self.error_response(
                    "Missing required field: automation_data", HTTPStatus.BAD_REQUEST
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

            status = HTTPStatus.OK if valid else HTTPStatus.BAD_REQUEST
            message = "Validation successful" if valid else "Validation failed"
            self.log_response(status, message)
            return self.json_response(result, status, message)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)
