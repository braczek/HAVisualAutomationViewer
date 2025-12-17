"""Base API handler for Visual AutoView."""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from homeassistant.components.http import HomeAssistantView
from homeassistant.const import (
    HTTP_BAD_REQUEST,
    HTTP_CREATED,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
)
from homeassistant.core import HomeAssistant

from .models import ApiResponse, ErrorResponse, SerializationHelper

_LOGGER = logging.getLogger(__name__)


class BaseApiView(HomeAssistantView, ABC):
    """Base class for API views."""

    # Override these in subclasses
    url: str = "/api/visualautoview"
    name: str = "api:visualautoview"
    requires_auth = True
    cors_allowed = True

    def __init__(self, hass: HomeAssistant):
        """Initialize the API view."""
        self.hass = hass
        self._logger = _LOGGER

    def log_request(self, method: str, path: str, data: Optional[Dict] = None):
        """Log incoming request."""
        self._logger.debug(f"{method} {path}" + (f" - {data}" if data else ""))

    def log_response(self, status: int, message: str = ""):
        """Log response."""
        self._logger.debug(f"Response {status}" + (f" - {message}" if message else ""))

    def json_response(
        self, data: Any, status: int = HTTP_OK, message: str = ""
    ) -> tuple:
        """Create a JSON response."""
        response = ApiResponse(
            success=status in (HTTP_OK, HTTP_CREATED),
            data=data,
            message=message,
            timestamp=datetime.utcnow(),
        )

        return (response.to_json(), status)

    def error_response(
        self, error: str, status: int = HTTP_BAD_REQUEST, message: str = ""
    ) -> tuple:
        """Create an error response."""
        response = ErrorResponse(
            success=False, error=error, message=message, timestamp=datetime.utcnow()
        )

        return (response.to_json(), status)

    def parse_json_body(self, request) -> Optional[Dict]:
        """Parse JSON from request body."""
        try:
            if isinstance(request.content, bytes):
                body = request.content.decode("utf-8")
            else:
                body = request.content

            return json.loads(body) if body else {}
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._logger.error(f"Failed to parse request body: {e}")
            return None

    def get_query_params(self, request) -> Dict[str, Any]:
        """Extract query parameters from request."""
        params = {}
        if hasattr(request, "query"):
            for key, value in request.query.items():
                # Try to convert to appropriate type
                if value.lower() in ("true", "false"):
                    params[key] = value.lower() == "true"
                elif value.isdigit():
                    params[key] = int(value)
                else:
                    params[key] = value
        return params


class RestApiEndpoint(BaseApiView):
    """Base class for REST API endpoints."""

    @abstractmethod
    async def get(self, request) -> tuple:
        """Handle GET request."""
        raise NotImplementedError

    async def post(self, request) -> tuple:
        """Handle POST request."""
        return self.error_response("POST not supported", HTTP_BAD_REQUEST)

    async def put(self, request) -> tuple:
        """Handle PUT request."""
        return self.error_response("PUT not supported", HTTP_BAD_REQUEST)

    async def delete(self, request) -> tuple:
        """Handle DELETE request."""
        return self.error_response("DELETE not supported", HTTP_BAD_REQUEST)


class WebSocketHandler(ABC):
    """Base class for WebSocket handlers."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the WebSocket handler."""
        self.hass = hass
        self._logger = _LOGGER
        self._subscriptions: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    async def handle_subscribe(self, connection, data: Dict[str, Any]):
        """Handle subscription request."""
        raise NotImplementedError

    @abstractmethod
    async def handle_unsubscribe(self, connection, subscription_id: str):
        """Handle unsubscription request."""
        raise NotImplementedError

    @abstractmethod
    async def handle_request(self, connection, message_id: str, data: Dict[str, Any]):
        """Handle data request via WebSocket."""
        raise NotImplementedError

    async def send_response(
        self, connection, message_id: str, data: Any, success: bool = True
    ):
        """Send response via WebSocket."""
        response = {
            "type": "response",
            "id": message_id,
            "success": success,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await connection.send_json(response)

    async def send_error(self, connection, message_id: str, error: str):
        """Send error via WebSocket."""
        response = {
            "type": "error",
            "id": message_id,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await connection.send_json(response)

    async def broadcast_event(
        self, event_type: str, data: Any, subscription_filter: Optional[Callable] = None
    ):
        """Broadcast event to subscribed clients."""
        event = {
            "type": "event",
            "action": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for sub_id, subscription in self._subscriptions.items():
            if subscription_filter is None or subscription_filter(subscription):
                try:
                    connection = subscription.get("connection")
                    if connection:
                        await connection.send_json(event)
                except Exception as e:
                    self._logger.error(
                        f"Failed to send event to subscription {sub_id}: {e}"
                    )


class ApiRegistry:
    """Registry for managing API endpoints."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the registry."""
        self.hass = hass
        self._endpoints: Dict[str, BaseApiView] = {}
        self._logger = _LOGGER

    def register(self, endpoint: BaseApiView) -> None:
        """Register an API endpoint."""
        if endpoint.url in self._endpoints:
            self._logger.warning(f"Endpoint {endpoint.url} already registered")

        self._endpoints[endpoint.url] = endpoint
        self._logger.debug(f"Registered API endpoint: {endpoint.url}")

    def get_endpoints(self) -> Dict[str, BaseApiView]:
        """Get all registered endpoints."""
        return self._endpoints

    async def register_with_http(self):
        """Register all endpoints with Home Assistant HTTP."""
        from homeassistant.components.http import HomeAssistantHTTP

        try:
            http = self.hass.data.get("http")
            if http:
                for url, endpoint in self._endpoints.items():
                    self.hass.http.register_view(endpoint)
                    self._logger.info(f"Registered HTTP view: {url}")
        except Exception as e:
            self._logger.error(f"Failed to register HTTP endpoints: {e}")


class ApiErrorHandler:
    """Helper for handling API errors."""

    @staticmethod
    def handle_error(
        error: Exception, status: int = HTTP_INTERNAL_SERVER_ERROR
    ) -> tuple:
        """Handle and log an error."""
        error_msg = str(error)
        _LOGGER.error(f"API Error: {error_msg}", exc_info=True)

        response = ErrorResponse(
            success=False,
            error=type(error).__name__,
            message=error_msg,
            timestamp=datetime.utcnow(),
        )

        return (response.to_json(), status)
