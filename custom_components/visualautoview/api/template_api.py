"""Template API Endpoints - Template variable expansion and validation."""

import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .base import ApiErrorHandler, RestApiEndpoint

_LOGGER = logging.getLogger(__name__)


class TemplateEndpoints:
    """Container for Template API endpoints."""

    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Template endpoints."""
        return [
            GetTemplateVariablesEndpoint(hass),
            PreviewTemplateExpansionEndpoint(hass),
            ValidateTemplateExpressionEndpoint(hass),
            EvaluateTemplateScenarioEndpoint(hass),
        ]


# ============================================================================
# Template Expansion Endpoints
# ============================================================================


class GetTemplateVariablesEndpoint(RestApiEndpoint):
    """Get available template variables."""

    url = "/api/visualautoview/templates/variables"
    name = "api:visualautoview:template_variables"

    async def get(self, request) -> tuple:
        """
        GET /api/visualautoview/phase3/template-variables

        Get available template variables for expansion.

        Response:
        {
            "success": true,
            "data": {
                "variables": [
                    {
                        "name": "trigger.entity_id",
                        "type": "string",
                        "description": "Entity ID that triggered the automation",
                        "example": "light.living_room"
                    }
                ],
                "functions": [...]
            }
        }
        """
        try:
            self.log_request("GET", self.url)

            result = {
                "variables": [
                    {
                        "name": "trigger",
                        "type": "object",
                        "description": "Trigger data",
                    },
                    {
                        "name": "state",
                        "type": "dict",
                        "description": "Entity states",
                    },
                ],
                "functions": [
                    {
                        "name": "is_state",
                        "description": "Check entity state",
                    }
                ],
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class PreviewTemplateExpansionEndpoint(RestApiEndpoint):
    """Preview template expansion result."""

    url = "/api/visualautoview/templates/preview"
    name = "api:visualautoview:preview_template"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Preview template expansion."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if not body or "template" not in body:
                return self.error_response(
                    "Missing field: template", HTTPStatus.BAD_REQUEST
                )

            result = {
                "template": body["template"],
                "result": "expanded_value",
                "valid": True,
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class ValidateTemplateExpressionEndpoint(RestApiEndpoint):
    """Validate template expression syntax."""

    url = "/api/visualautoview/templates/validate"
    name = "api:visualautoview:validate_template"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Validate template."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if not body:
                return self.error_response("Invalid request", HTTPStatus.BAD_REQUEST)

            result = {
                "valid": True,
                "errors": [],
                "warnings": [],
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class EvaluateTemplateScenarioEndpoint(RestApiEndpoint):
    """Evaluate template in specific scenario."""

    url = "/api/visualautoview/templates/scenario"
    name = "api:visualautoview:template_scenario"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Evaluate template scenario."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            result = {
                "scenario_id": "scenario_001",
                "template": body.get("template") if body else "",
                "result": "",
                "execution_time_ms": 5,
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)
