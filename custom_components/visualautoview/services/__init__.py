"""Backend services for Visual AutoView integration."""

# Import all services for easy access
try:
    from .all_automations_service import AllAutomationsService
except ImportError:
    AllAutomationsService = None

try:
    from .comparison_engine import ComparisonEngine
except ImportError:
    ComparisonEngine = None

try:
    from .dependency_graph_service import DependencyGraphService
except ImportError:
    DependencyGraphService = None

try:
    from .entity_relationship_service import EntityRelationshipService
except ImportError:
    EntityRelationshipService = None

try:
    from .execution_path_service import ExecutionPathService
except ImportError:
    ExecutionPathService = None

try:
    from .export_service import ExportService
except ImportError:
    ExportService = None

try:
    from .performance_metrics_service import PerformanceMetricsService
except ImportError:
    PerformanceMetricsService = None

try:
    from .search_engine import SearchEngine
except ImportError:
    SearchEngine = None

try:
    from .template_expansion_service import TemplateExpansionService
except ImportError:
    TemplateExpansionService = None

try:
    from .theme_manager import ThemeManager
except ImportError:
    ThemeManager = None

__all__ = [
    "AllAutomationsService",
    "ComparisonEngine",
    "DependencyGraphService",
    "EntityRelationshipService",
    "ExecutionPathService",
    "ExportService",
    "PerformanceMetricsService",
    "SearchEngine",
    "TemplateExpansionService",
    "ThemeManager",
]
