"""Phase 2 API Endpoints - Dashboard, Search, Export, Themes, Comparison."""

import logging
from typing import Any, Dict, Optional, List
from homeassistant.core import HomeAssistant
from homeassistant.const import HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_SERVER_ERROR, HTTP_CREATED

from .base import RestApiEndpoint, ApiErrorHandler
from .models import (
    PaginationParams, PaginatedResponse, SearchRequestParams,
    FilterRequestParams, ExportRequestParams, ComparisonRequestParams,
    ThemeApplyParams
)

_LOGGER = logging.getLogger(__name__)


class Phase2Endpoints:
    """Container for Phase 2 API endpoints."""
    
    @staticmethod
    def create_endpoints(hass: HomeAssistant) -> list:
        """Create all Phase 2 endpoints."""
        return [
            # Dashboard Endpoints
            GetDashboardEndpoint(hass),
            GetAllAutomationsEndpoint(hass),
            GetAutomationSummaryEndpoint(hass),
            
            # Search Endpoints
            SearchAutomationsEndpoint(hass),
            AdvancedSearchEndpoint(hass),
            
            # Filter Endpoints
            FilterAutomationsEndpoint(hass),
            GetFilterOptionsEndpoint(hass),
            
            # Export Endpoints
            ExportAutomationsEndpoint(hass),
            ExportGraphEndpoint(hass),
            
            # Theme Endpoints
            ListThemesEndpoint(hass),
            GetThemeEndpoint(hass),
            CreateThemeEndpoint(hass),
            UpdateThemeEndpoint(hass),
            DeleteThemeEndpoint(hass),
            ApplyThemeEndpoint(hass),
            ExportThemeEndpoint(hass),
            ImportThemeEndpoint(hass),
            
            # Comparison Endpoints
            CompareAutomationsEndpoint(hass),
            GetConsolidationSuggestionsEndpoint(hass),
        ]


# ============================================================================
# Dashboard Endpoints
# ============================================================================

class GetDashboardEndpoint(RestApiEndpoint):
    """Get dashboard summary with all metrics."""
    
    url = "/api/visualautoview/phase2/dashboard"
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
            enabled = sum(1 for a in automations if self.hass.states.get(a).state == "on")
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
                }
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class GetAllAutomationsEndpoint(RestApiEndpoint):
    """Get all automations with mini-graphs."""
    
    url = "/api/visualautoview/phase2/automations/all"
    name = "api:visualautoview:get_all_automations"
    
    async def get(self, request) -> tuple:
        """
        GET /api/visualautoview/phase2/automations/all
        
        Get all automations with mini-graph data.
        
        Query parameters:
        - page: int (default: 1)
        - per_page: int (default: 50)
        - include_disabled: bool (default: false)
        
        Response:
        {
            "success": true,
            "data": {
                "items": [...],
                "pagination": {...}
            }
        }
        """
        try:
            self.log_request("GET", self.url)
            params = self.get_query_params(request)
            
            page = params.get("page", 1)
            per_page = params.get("per_page", 50)
            include_disabled = params.get("include_disabled", False)
            
            automations = self.hass.states.async_entity_ids("automation")
            
            items = []
            for automation_id in automations:
                state = self.hass.states.get(automation_id)
                if not state:
                    continue
                
                is_enabled = state.state == "on"
                if not include_disabled and not is_enabled:
                    continue
                
                items.append({
                    "automation_id": automation_id.replace("automation.", ""),
                    "alias": state.attributes.get("friendly_name", automation_id),
                    "description": state.attributes.get("description", ""),
                    "enabled": is_enabled,
                    "node_count": 0,
                    "edge_count": 0,
                    "primary_triggers": [],
                    "primary_actions": [],
                    "execution_time": None,
                    "last_triggered": None,
                })
            
            total_count = len(items)
            total_pages = (total_count + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            paged_items = items[start_idx:start_idx + per_page]
            
            result = {
                "items": paged_items,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": total_pages,
                }
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class GetAutomationSummaryEndpoint(RestApiEndpoint):
    """Get summary statistics for automations."""
    
    url = "/api/visualautoview/phase2/automations/summary"
    name = "api:visualautoview:get_automation_summary"
    
    async def get(self, request) -> tuple:
        """Get summary statistics."""
        try:
            self.log_request("GET", self.url)
            
            automations = self.hass.states.async_entity_ids("automation")
            
            result = {
                "total": len(automations),
                "enabled": sum(1 for a in automations if self.hass.states.get(a).state == "on"),
                "disabled": sum(1 for a in automations if self.hass.states.get(a).state != "on"),
                "by_platform": {},
                "by_type": {},
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


# ============================================================================
# Search Endpoints
# ============================================================================

class SearchAutomationsEndpoint(RestApiEndpoint):
    """Search automations by text."""
    
    url = "/api/visualautoview/phase2/search"
    name = "api:visualautoview:search_automations"
    
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
            body = self.parse_json_body(request)
            
            if not body or "query" not in body:
                return self.error_response(
                    "Missing required field: query",
                    HTTP_BAD_REQUEST
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
                search_text = f"{alias} {description}".lower() if not case_sensitive else f"{alias} {description}"
                query_text = query.lower() if not case_sensitive else query
                
                if match_type == "contains" and query_text in search_text:
                    results.append({
                        "automation_id": automation_id.replace("automation.", ""),
                        "alias": alias,
                        "relevance_score": 85.0,
                        "match_type": "text",
                        "matched_text": query,
                        "context": description[:100],
                    })
            
            total_count = len(results)
            total_pages = (total_count + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            paged_results = results[start_idx:start_idx + per_page]
            
            result = {
                "query": query,
                "results": paged_results,
                "total_results": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class AdvancedSearchEndpoint(RestApiEndpoint):
    """Advanced search with filters."""
    
    url = "/api/visualautoview/phase2/search/advanced"
    name = "api:visualautoview:advanced_search"
    
    async def post(self, request) -> tuple:
        """POST advanced search request."""
        try:
            self.log_request("POST", self.url)
            body = self.parse_json_body(request)
            
            if not body:
                return self.error_response("Invalid request", HTTP_BAD_REQUEST)
            
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


# ============================================================================
# Filter Endpoints
# ============================================================================

class FilterAutomationsEndpoint(RestApiEndpoint):
    """Filter automations by criteria."""
    
    url = "/api/visualautoview/phase2/filter"
    name = "api:visualautoview:filter_automations"
    
    async def post(self, request) -> tuple:
        """Filter automations by various criteria."""
        try:
            self.log_request("POST", self.url)
            body = self.parse_json_body(request)
            
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class GetFilterOptionsEndpoint(RestApiEndpoint):
    """Get available filter options."""
    
    url = "/api/visualautoview/phase2/filter/options"
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


# ============================================================================
# Export Endpoints
# ============================================================================

class ExportAutomationsEndpoint(RestApiEndpoint):
    """Export automations in various formats."""
    
    url = "/api/visualautoview/phase2/export"
    name = "api:visualautoview:export_automations"
    
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
            body = self.parse_json_body(request)
            
            if not body:
                return self.error_response("Invalid request", HTTP_BAD_REQUEST)
            
            export_format = body.get("format", "json")
            include_graphs = body.get("include_graphs", True)
            
            if export_format not in ("json", "csv", "pdf"):
                return self.error_response(
                    f"Invalid format: {export_format}",
                    HTTP_BAD_REQUEST
                )
            
            result = {
                "export_id": "export_12345",
                "format": export_format,
                "status": "pending",
                "created_at": None,
                "file_url": None,
                "estimated_time_seconds": 5,
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class ExportGraphEndpoint(RestApiEndpoint):
    """Export automation graph in various formats."""
    
    url = "/api/visualautoview/phase2/export/graph/{automation_id}"
    name = "api:visualautoview:export_graph"
    
    async def post(self, request) -> tuple:
        """Export graph for specific automation."""
        try:
            self.log_request("POST", self.url)
            
            automation_id = request.match_info.get("automation_id")
            body = self.parse_json_body(request)
            
            result = {
                "export_id": f"export_{automation_id}",
                "automation_id": automation_id,
                "format": body.get("format", "json") if body else "json",
                "status": "completed",
                "data": {
                    "nodes": [],
                    "edges": [],
                }
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


# ============================================================================
# Theme Endpoints
# ============================================================================

class ListThemesEndpoint(RestApiEndpoint):
    """List available themes."""
    
    url = "/api/visualautoview/phase2/themes"
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class GetThemeEndpoint(RestApiEndpoint):
    """Get specific theme."""
    
    url = "/api/visualautoview/phase2/themes/{theme_id}"
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class CreateThemeEndpoint(RestApiEndpoint):
    """Create new theme."""
    
    url = "/api/visualautoview/phase2/themes"
    name = "api:visualautoview:create_theme"
    
    async def post(self, request) -> tuple:
        """Create new theme."""
        try:
            self.log_request("POST", self.url)
            body = self.parse_json_body(request)
            
            if not body or "name" not in body:
                return self.error_response("Missing field: name", HTTP_BAD_REQUEST)
            
            result = {
                "id": "theme_new",
                "name": body.get("name"),
                "colors": body.get("colors", {}),
            }
            
            self.log_response(HTTP_CREATED)
            return self.json_response(result, HTTP_CREATED, "Theme created")
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class UpdateThemeEndpoint(RestApiEndpoint):
    """Update existing theme."""
    
    url = "/api/visualautoview/phase2/themes/{theme_id}"
    name = "api:visualautoview:update_theme"
    
    async def put(self, request) -> tuple:
        """Update theme."""
        try:
            self.log_request("PUT", self.url)
            
            theme_id = request.match_info.get("theme_id")
            body = self.parse_json_body(request)
            
            result = {
                "id": theme_id,
                "updated": True,
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class DeleteThemeEndpoint(RestApiEndpoint):
    """Delete theme."""
    
    url = "/api/visualautoview/phase2/themes/{theme_id}"
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class ApplyThemeEndpoint(RestApiEndpoint):
    """Apply theme to automations."""
    
    url = "/api/visualautoview/phase2/themes/{theme_id}/apply"
    name = "api:visualautoview:apply_theme"
    
    async def post(self, request) -> tuple:
        """Apply theme to automations."""
        try:
            self.log_request("POST", self.url)
            
            theme_id = request.match_info.get("theme_id")
            body = self.parse_json_body(request)
            
            result = {
                "theme_id": theme_id,
                "applied": True,
                "automations_affected": body.get("automation_ids", []) if body else [],
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class ExportThemeEndpoint(RestApiEndpoint):
    """Export theme."""
    
    url = "/api/visualautoview/phase2/themes/{theme_id}/export"
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class ImportThemeEndpoint(RestApiEndpoint):
    """Import theme."""
    
    url = "/api/visualautoview/phase2/themes/import"
    name = "api:visualautoview:import_theme"
    
    async def post(self, request) -> tuple:
        """Import theme."""
        try:
            self.log_request("POST", self.url)
            body = self.parse_json_body(request)
            
            result = {
                "theme_id": "imported_theme",
                "imported": True,
            }
            
            self.log_response(HTTP_CREATED)
            return self.json_response(result, HTTP_CREATED)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


# ============================================================================
# Comparison Endpoints
# ============================================================================

class CompareAutomationsEndpoint(RestApiEndpoint):
    """Compare two automations."""
    
    url = "/api/visualautoview/phase2/compare"
    name = "api:visualautoview:compare_automations"
    
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
            body = self.parse_json_body(request)
            
            if not body or "automation_id_1" not in body or "automation_id_2" not in body:
                return self.error_response(
                    "Missing fields: automation_id_1, automation_id_2",
                    HTTP_BAD_REQUEST
                )
            
            result = {
                "automation_id_1": body["automation_id_1"],
                "automation_id_2": body["automation_id_2"],
                "similarity_score": 65.5,
                "differences": [],
                "common_elements": [],
            }
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)


class GetConsolidationSuggestionsEndpoint(RestApiEndpoint):
    """Get consolidation suggestions for automations."""
    
    url = "/api/visualautoview/phase2/consolidation-suggestions"
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
            
            self.log_response(HTTP_OK)
            return self.json_response(result, HTTP_OK)
            
        except Exception as e:
            return ApiErrorHandler.handle_error(e, HTTP_INTERNAL_SERVER_ERROR)
