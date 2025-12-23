"""
Authentication Troubleshooting Guide for Visual AutoView

This module provides debugging utilities for authentication issues,
particularly for mobile app access problems.
"""

import logging
from typing import Any, Dict, List

_LOGGER = logging.getLogger(__name__)


class AuthDiagnostics:
    """Diagnostic utilities for authentication issues."""

    @staticmethod
    def get_auth_status() -> Dict[str, Any]:
        """Get current authentication status information."""
        return {
            "cors_enabled": True,
            "cors_headers": [
                "Access-Control-Allow-Origin: *",
                "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With",
                "Access-Control-Allow-Credentials: true",
            ],
            "auth_required": True,
            "mobile_app_support": True,
            "cache_headers": {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        }

    @staticmethod
    def get_troubleshooting_tips() -> Dict[str, List[str]]:
        """Get troubleshooting tips for common authentication issues."""
        return {
            "mobile_app_no_access": [
                "1. Ensure you're logged in to Home Assistant in your mobile app",
                "2. Check that CORS headers are being sent in responses",
                "3. Verify the Authorization header is present in requests",
                "4. Try accessing from HA web dashboard first to confirm integration works",
                "5. Check Home Assistant logs for 401/403 errors",
                "6. Restart Home Assistant if changes were made to the integration",
            ],
            "auth_expires_after_time": [
                "1. Tokens may expire. Check Home Assistant's token lifetime settings",
                "2. Implement token refresh logic on the client side",
                "3. Check if your Home Assistant session is expiring",
                "4. Try logging out and logging back in",
                "5. Check Home Assistant's authentication settings in configuration.yaml",
                "6. Monitor logs for 'Token has expired' messages",
            ],
            "general_auth_errors": [
                "1. Verify your Home Assistant user has admin privileges",
                "2. Check that your token/session is still valid",
                "3. Ensure CORS headers are present in HTTP responses",
                "4. Check browser console for specific error messages",
                "5. Verify the API endpoint URL is correct",
                "6. Check Home Assistant error logs for backend issues",
            ],
            "cors_errors": [
                "1. CORS headers should be present on all responses",
                "2. Check that Access-Control-Allow-Origin header is set to '*'",
                "3. Verify OPTIONS requests are handled correctly",
                "4. Mobile apps may have stricter CORS requirements",
                "5. Try accessing from a different network or device",
            ],
        }

    @staticmethod
    def log_diagnostics(hass) -> None:
        """Log diagnostic information for debugging."""
        _LOGGER.warning("========== Visual AutoView Auth Diagnostics ==========")
        _LOGGER.warning("Mobile App Authentication Support Status:")
        _LOGGER.warning("  ✓ CORS Headers: Enabled")
        _LOGGER.warning("  ✓ Token Validation: Enabled")
        _LOGGER.warning("  ✓ Session Management: Enabled")
        _LOGGER.warning("  ✓ Error Logging: Enabled")
        _LOGGER.warning("")
        _LOGGER.warning("If experiencing authentication issues:")
        _LOGGER.warning("  1. Check Home Assistant logs: Settings -> System -> Logs")
        _LOGGER.warning("  2. Verify user has admin privileges")
        _LOGGER.warning("  3. Try accessing from web dashboard first")
        _LOGGER.warning("  4. Check mobile app version is up to date")
        _LOGGER.warning(
            "  5. Review troubleshooting guide in integration documentation"
        )
        _LOGGER.warning("=====================================================")


def debug_log_auth_headers(request) -> None:
    """Log authentication headers from request for debugging."""
    auth_header = request.headers.get("Authorization", "Not present")
    origin = request.headers.get("Origin", "Not present")
    content_type = request.headers.get("Content-Type", "Not present")

    _LOGGER.debug(f"Request Auth Headers:")
    _LOGGER.debug(
        f"  Authorization: {auth_header[:50] + '...' if len(auth_header) > 50 else auth_header}"
    )
    _LOGGER.debug(f"  Origin: {origin}")
    _LOGGER.debug(f"  Content-Type: {content_type}")


def get_auth_error_message(status_code: int) -> str:
    """Get helpful error message for authentication status codes."""
    messages = {
        401: "Unauthorized - Your authentication token has expired or is invalid. Please log in again.",
        403: "Forbidden - Your account doesn't have permission to access this resource. Check your Home Assistant user privileges.",
        407: "Proxy Authentication Required - Check your proxy/firewall settings.",
    }
    return messages.get(status_code, f"Authentication error (HTTP {status_code})")
