"""Theme API Endpoints - Manage visualization themes."""

import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

from .base import ApiErrorHandler, RestApiEndpoint

_LOGGER = logging.getLogger(__name__)


class ThemeEndpoints:
    """Container for Theme API endpoints."""

    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Theme endpoints."""
        return [
            ListThemesEndpoint(hass),
            GetThemeEndpoint(hass),
            CreateThemeEndpoint(hass),
            UpdateThemeEndpoint(hass),
            DeleteThemeEndpoint(hass),
            ApplyThemeEndpoint(hass),
            ExportThemeEndpoint(hass),
            ImportThemeEndpoint(hass),
        ]


# ============================================================================
# Theme Endpoints
# ============================================================================


class ListThemesEndpoint(RestApiEndpoint):
    """List available themes."""

    url = "/api/visualautoview/themes"
    name = "api:visualautoview:list_themes"

    async def get(self, request) -> tuple:
        """Get list of available themes."""
        try:
            self.log_request("GET", self.url)

            themes = [
                {
                    "id": "default",
                    "name": "Default Theme",
                    "description": "Default Visual AutoView theme",
                    "colors": {"primary": "#2196F3", "secondary": "#FFC107"},
                },
                {
                    "id": "dark",
                    "name": "Dark Theme",
                    "description": "Dark mode theme",
                    "colors": {"primary": "#1976D2", "secondary": "#FF6F00"},
                },
            ]

            result = {
                "themes": themes,
                "total_count": len(themes),
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class GetThemeEndpoint(RestApiEndpoint):
    """Get specific theme."""

    url = "/api/visualautoview/themes/{theme_id}"
    name = "api:visualautoview:get_theme"

    async def get(self, request) -> tuple:
        """Get specific theme details."""
        try:
            self.log_request("GET", self.url)

            theme_id = request.match_info.get("theme_id")

            result = {
                "id": theme_id,
                "name": f"{theme_id.title()} Theme",
                "colors": {},
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class CreateThemeEndpoint(RestApiEndpoint):
    """Create new theme."""

    url = "/api/visualautoview/themes"
    name = "api:visualautoview:create_theme"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Create new theme."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            if not body or "name" not in body:
                return self.error_response(
                    "Missing field: name", HTTPStatus.BAD_REQUEST
                )

            result = {
                "id": "theme_new",
                "name": body.get("name"),
                "colors": body.get("colors", {}),
            }

            self.log_response(HTTPStatus.CREATED)
            return self.json_response(result, HTTPStatus.CREATED, "Theme created")

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class UpdateThemeEndpoint(RestApiEndpoint):
    """Update existing theme."""

    url = "/api/visualautoview/themes/{theme_id}"
    name = "api:visualautoview:update_theme"

    async def put(self, request) -> tuple:
        """Update theme."""
        try:
            self.log_request("PUT", self.url)

            theme_id = request.match_info.get("theme_id")
            body = await self.parse_json_body(request)

            result = {
                "id": theme_id,
                "updated": True,
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class DeleteThemeEndpoint(RestApiEndpoint):
    """Delete theme."""

    url = "/api/visualautoview/themes/{theme_id}"
    name = "api:visualautoview:delete_theme"

    async def delete(self, request) -> tuple:
        """Delete theme."""
        try:
            self.log_request("DELETE", self.url)

            theme_id = request.match_info.get("theme_id")

            result = {
                "id": theme_id,
                "deleted": True,
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class ApplyThemeEndpoint(RestApiEndpoint):
    """Apply theme to automations."""

    url = "/api/visualautoview/themes/{theme_id}/apply"
    name = "api:visualautoview:apply_theme"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Apply theme to automations."""
        try:
            self.log_request("POST", self.url)

            theme_id = request.match_info.get("theme_id")
            body = await self.parse_json_body(request)

            result = {
                "theme_id": theme_id,
                "applied": True,
                "automations_affected": body.get("automation_ids", []) if body else [],
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class ExportThemeEndpoint(RestApiEndpoint):
    """Export theme."""

    url = "/api/visualautoview/themes/{theme_id}/export"
    name = "api:visualautoview:export_theme"

    async def get(self, request) -> tuple:
        """Export theme."""
        try:
            self.log_request("GET", self.url)

            theme_id = request.match_info.get("theme_id")

            result = {
                "theme_id": theme_id,
                "export_format": "json",
                "data": {},
            }

            self.log_response(HTTPStatus.OK)
            return self.json_response(result, HTTPStatus.OK)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)


class ImportThemeEndpoint(RestApiEndpoint):
    """Import theme."""

    url = "/api/visualautoview/themes/import"
    name = "api:visualautoview:import_theme"

    async def get(self, request) -> tuple:
        """GET not supported - use POST."""
        return self.error_response(
            "GET not supported. Use POST with request data.", HTTPStatus.BAD_REQUEST
        )

    async def post(self, request) -> tuple:
        """Import theme."""
        try:
            self.log_request("POST", self.url)
            body = await self.parse_json_body(request)

            result = {
                "theme_id": "imported_theme",
                "imported": True,
            }

            self.log_response(HTTPStatus.CREATED)
            return self.json_response(result, HTTPStatus.CREATED)

        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTPStatus.INTERNAL_SERVER_ERROR)
