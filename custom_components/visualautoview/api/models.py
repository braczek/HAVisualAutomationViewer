"""API request/response models for Visual AutoView."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


@dataclass
class ApiResponse:
    """Standard API response wrapper."""
    
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_json(self) -> str:
        """Convert response to JSON string."""
        response_dict = {
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.error:
            response_dict["error"] = self.error
        if self.data is not None:
            response_dict["data"] = self.data
        return json.dumps(response_dict)


@dataclass
class ErrorResponse:
    """Standard error response."""
    
    success: bool = False
    error: str = ""
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_json(self) -> str:
        """Convert error response to JSON string."""
        return json.dumps({
            "success": self.success,
            "error": self.error,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        })


@dataclass
class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    page: int = 1
    per_page: int = 50
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # 'asc' or 'desc'
    
    def validate(self) -> bool:
        """Validate pagination parameters."""
        if self.page < 1 or self.per_page < 1:
            return False
        if self.sort_order not in ("asc", "desc"):
            return False
        return True


@dataclass
class PaginatedResponse:
    """Paginated response wrapper."""
    
    items: List[Any]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "items": self.items,
            "pagination": {
                "total_count": self.total_count,
                "page": self.page,
                "per_page": self.per_page,
                "total_pages": self.total_pages,
            }
        }


@dataclass
class GraphRequestParams:
    """Parameters for graph parsing requests."""
    
    automation_id: Optional[str] = None
    include_disabled: bool = False
    max_depth: Optional[int] = None
    expand_templates: bool = False


@dataclass
class SearchRequestParams:
    """Parameters for search requests."""
    
    query: str
    search_type: str = "full"  # 'full', 'triggers', 'conditions', 'actions', 'entities'
    match_type: str = "contains"  # 'contains', 'exact', 'regex'
    case_sensitive: bool = False
    include_disabled: bool = False


@dataclass
class FilterRequestParams:
    """Parameters for filter requests."""
    
    automation_state: Optional[str] = None  # 'enabled', 'disabled', None for all
    trigger_platforms: Optional[List[str]] = None
    entity_ids: Optional[List[str]] = None
    services_called: Optional[List[str]] = None
    has_conditions: Optional[bool] = None
    search_text: Optional[str] = None


@dataclass
class ExportRequestParams:
    """Parameters for export requests."""
    
    format: str  # 'json', 'csv', 'pdf'
    include_graphs: bool = True
    include_metadata: bool = True
    compression: bool = False
    automation_ids: Optional[List[str]] = None  # None = all


@dataclass
class ComparisonRequestParams:
    """Parameters for comparison requests."""
    
    automation_id_1: str
    automation_id_2: str
    include_structure_diff: bool = True
    include_similarity_score: bool = True
    include_consolidation: bool = True


@dataclass
class ThemeApplyParams:
    """Parameters for theme application."""
    
    theme_id: str
    automation_ids: Optional[List[str]] = None  # None = apply globally


@dataclass
class WebSocketMessage:
    """WebSocket message model."""
    
    type: str  # 'subscribe', 'unsubscribe', 'request', 'response', 'error', 'event'
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    id: Optional[str] = None  # Message ID for tracking
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "action": self.action,
            "data": self.data,
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class WebSocketSubscription:
    """WebSocket subscription model."""
    
    subscription_id: str
    action: str  # 'automation_updates', 'execution_events', 'metrics_updates', etc.
    automation_ids: Optional[List[str]] = None  # None = subscribe to all
    update_interval: int = 1000  # milliseconds


class SerializationHelper:
    """Helper class for serializing complex objects."""
    
    @staticmethod
    def to_dict(obj: Any) -> Any:
        """Convert object to dictionary, handling various types."""
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: SerializationHelper.to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [SerializationHelper.to_dict(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def to_json(obj: Any) -> str:
        """Convert object to JSON string."""
        return json.dumps(
            SerializationHelper.to_dict(obj),
            default=str,
            indent=2
        )
