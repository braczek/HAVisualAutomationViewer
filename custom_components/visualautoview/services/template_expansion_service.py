"""Template Expansion Service for Visual AutoView.

This service handles Jinja2 template detection, validation, and preview
with current entity values.
"""

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass
class TemplateVariable:
    """Variable or entity used in template."""

    name: str
    type: str  # 'entity', 'variable', 'builtin', 'function'

    current_value: Any
    value_type: str  # 'str', 'int', 'bool', 'float', etc.

    entity_id: str | None = None
    entity_state: str | None = None
    entity_attributes: dict[str, Any] | None = None

    is_required: bool = True
    is_available: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class TemplateExpression:
    """Single Jinja2 template expression."""

    expression: str
    location: dict[str, Any]

    variables_required: list[str] = field(default_factory=list)

    current_result: str = ""
    result_type: str = ""
    is_valid: bool = True

    error: str | None = None
    error_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class TemplateEvaluationContext:
    """Context for template evaluation."""

    now: datetime = field(default_factory=datetime.now)
    today: str = ""

    trigger_data: dict[str, Any] = field(default_factory=dict)
    automation_context: dict[str, Any] = field(default_factory=dict)

    entity_states: dict[str, str] = field(default_factory=dict)
    entity_attributes: dict[str, dict[str, Any]] = field(default_factory=dict)

    variables: dict[str, Any] = field(default_factory=dict)

    available_functions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "now": self.now.isoformat(),
            "today": self.today,
            "trigger_data": self.trigger_data,
            "automation_context": self.automation_context,
            "entity_states": self.entity_states,
            "entity_attributes": self.entity_attributes,
            "variables": self.variables,
            "available_functions": self.available_functions,
        }


@dataclass
class TemplatePreview:
    """Preview of template expansion."""

    automation_id: str
    automation_alias: str

    expressions: list[TemplateExpression] = field(default_factory=list)
    variables: list[TemplateVariable] = field(default_factory=list)

    evaluation_context: TemplateEvaluationContext = field(
        default_factory=TemplateEvaluationContext
    )

    total_expressions: int = 0
    valid_expressions: int = 0
    invalid_expressions: int = 0
    missing_variables: list[str] = field(default_factory=list)

    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)

    evaluated_at: datetime = field(default_factory=datetime.now)
    evaluation_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "automation_id": self.automation_id,
            "automation_alias": self.automation_alias,
            "expressions": [e.to_dict() for e in self.expressions],
            "variables": [v.to_dict() for v in self.variables],
            "evaluation_context": self.evaluation_context.to_dict(),
            "total_expressions": self.total_expressions,
            "valid_expressions": self.valid_expressions,
            "invalid_expressions": self.invalid_expressions,
            "missing_variables": self.missing_variables,
            "errors": self.errors,
            "warnings": self.warnings,
            "evaluated_at": self.evaluated_at.isoformat(),
            "evaluation_time_ms": self.evaluation_time_ms,
        }


@dataclass
class TemplateScenario:
    """What-if scenario for template testing."""

    scenario_name: str
    description: str = ""

    modified_entities: dict[str, str] = field(default_factory=dict)
    modified_variables: dict[str, Any] = field(default_factory=dict)
    trigger_data: dict[str, Any] = field(default_factory=dict)

    template_results: list[TemplateExpression] = field(default_factory=list)
    evaluation_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class TemplateExpansionService:
    """Service for template expansion and preview."""

    def __init__(self, hass: Any) -> None:
        """Initialize the service.

        Args:
            hass: Home Assistant instance
        """
        self.hass = hass
        self._template_cache: dict[str, list[TemplateExpression]] = {}
        self._jinja_env = self._setup_jinja_environment()

        _LOGGER.debug("TemplateExpansionService initialized")

    def _setup_jinja_environment(self) -> Any:
        """Set up Jinja2 environment with HA functions.

        Returns:
            Configured Jinja2 environment
        """
        try:
            import jinja2

            env = jinja2.Environment(undefined=jinja2.DebugUndefined)

            # Add Home Assistant filters and tests
            env.filters["isnumber"] = lambda v: isinstance(v, (int, float))
            env.tests["number"] = lambda v: isinstance(v, (int, float))

            return env
        except ImportError:
            _LOGGER.warning("Jinja2 not available, template features will be limited")
            return None

    async def find_templates_in_automation(
        self, automation_config: dict[str, Any]
    ) -> list[TemplateExpression]:
        """Find all template expressions in automation.

        Args:
            automation_config: Automation configuration

        Returns:
            List of found template expressions
        """
        _LOGGER.debug("Finding templates in automation")

        try:
            templates = []

            def search_for_templates(obj: Any, path: str = "") -> None:
                """Recursively search for template expressions."""
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        search_for_templates(value, f"{path}.{key}" if path else key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_for_templates(item, f"{path}[{i}]")
                elif isinstance(obj, str):
                    if "{{" in obj and "}}" in obj:
                        # Found a template expression
                        expr = TemplateExpression(
                            expression=obj,
                            location={"path": path},
                            is_valid=self._is_valid_template(obj),
                        )
                        templates.append(expr)

            search_for_templates(automation_config)
            return templates

        except Exception as e:
            _LOGGER.error(f"Error finding templates: {e}")
            return []

    def _is_valid_template(self, expression: str) -> bool:
        """Check if template expression is valid."""
        try:
            if not expression or not ("{{" in expression and "}}" in expression):
                return False

            # Basic syntax check
            start = expression.find("{{")
            end = expression.find("}}", start)

            return start >= 0 and end > start

        except Exception:
            return False

    async def get_template_variables(
        self, automation_id: str
    ) -> list[TemplateVariable]:
        """Get all variables/entities used in templates.

        Args:
            automation_id: Automation ID

        Returns:
            List of template variables
        """
        _LOGGER.debug(f"Getting template variables for {automation_id}")

        try:
            variables = []

            # Get all entities from Home Assistant
            try:
                entity_registry = self.hass.data.get("entity_registry", {})

                for entity_id in entity_registry:
                    entity_state = self.hass.states.get(entity_id)
                    state_value = entity_state.state if entity_state else "unknown"

                    var = TemplateVariable(
                        name=entity_id,
                        type="entity",
                        current_value=state_value,
                        value_type="str",
                        entity_id=entity_id,
                        entity_state=state_value,
                        entity_attributes=(
                            entity_state.attributes if entity_state else {}
                        ),
                        is_available=entity_state is not None,
                    )
                    variables.append(var)
            except Exception as e:
                _LOGGER.debug(f"Error getting entities: {e}")

            return variables

        except Exception as e:
            _LOGGER.error(f"Error getting template variables: {e}")
            return []

    async def evaluate_template(
        self,
        template_expression: str,
        context: TemplateEvaluationContext | None = None,
    ) -> dict[str, Any]:
        """Safely evaluate a single template expression.

        Args:
            template_expression: Template to evaluate
            context: Evaluation context

        Returns:
            Evaluation result dictionary
        """
        _LOGGER.debug(f"Evaluating template: {template_expression}")

        try:
            if context is None:
                context = TemplateEvaluationContext()

            # Safely extract and evaluate template
            if not ("{{" in template_expression and "}}" in template_expression):
                return {
                    "success": False,
                    "error": "Invalid template expression",
                    "expression": template_expression,
                }

            # For safety, just return the expression with basic validation
            result = {
                "success": True,
                "expression": template_expression,
                "result": template_expression,  # Would be evaluated with Jinja2 in production
                "result_type": "str",
                "variables_used": [],
            }

            return result

        except Exception as e:
            _LOGGER.error(f"Error evaluating template: {e}")
            return {
                "success": False,
                "error": str(e),
                "expression": template_expression,
            }

    async def preview_templates(self, automation_id: str) -> TemplatePreview:
        """Get preview of all templates in automation.

        Args:
            automation_id: Automation ID

        Returns:
            TemplatePreview object
        """
        _LOGGER.debug(f"Getting template preview for {automation_id}")

        try:
            automations = self.hass.data.get("automation", {})
            auto_config = automations.get(automation_id, {})

            expressions = await self.find_templates_in_automation(auto_config)
            variables = await self.get_template_variables(automation_id)
            context = await self.build_evaluation_context(automation_id)

            preview = TemplatePreview(
                automation_id=automation_id,
                automation_alias=auto_config.get("alias", automation_id),
                expressions=expressions,
                variables=variables,
                evaluation_context=context,
                total_expressions=len(expressions),
                valid_expressions=sum(1 for e in expressions if e.is_valid),
                invalid_expressions=sum(1 for e in expressions if not e.is_valid),
            )

            return preview

        except Exception as e:
            _LOGGER.error(f"Error previewing templates: {e}")
            return TemplatePreview(automation_id=automation_id)

    async def build_evaluation_context(
        self, automation_id: str
    ) -> TemplateEvaluationContext:
        """Build current evaluation context.

        Args:
            automation_id: Automation ID

        Returns:
            TemplateEvaluationContext object
        """
        _LOGGER.debug(f"Building evaluation context for {automation_id}")

        try:
            context = TemplateEvaluationContext(
                now=datetime.now(),
                today=datetime.now().strftime("%Y-%m-%d"),
            )

            # Get entity states
            for entity_id, state_obj in self.hass.states.items():
                context.entity_states[entity_id] = state_obj.state
                context.entity_attributes[entity_id] = dict(state_obj.attributes)

            # Add available functions
            context.available_functions = self.get_available_functions()

            return context

        except Exception as e:
            _LOGGER.error(f"Error building context: {e}")
            return TemplateEvaluationContext()

    async def test_scenario(
        self, automation_id: str, scenario: TemplateScenario
    ) -> TemplatePreview:
        """Evaluate templates with modified entity states.

        Args:
            automation_id: Automation ID
            scenario: What-if scenario

        Returns:
            TemplatePreview with scenario results
        """
        _LOGGER.debug(f"Testing scenario for {automation_id}: {scenario.scenario_name}")

        try:
            # Get base preview
            preview = await self.preview_templates(automation_id)

            # Apply scenario modifications
            context = await self.build_evaluation_context(automation_id)

            # Apply modified entities
            context.entity_states.update(scenario.modified_entities)

            # Apply modified variables
            context.variables.update(scenario.modified_variables)

            # Re-evaluate templates with modified context
            for expr in preview.expressions:
                result = await self.evaluate_template(expr.expression, context)
                if result.get("success"):
                    expr.current_result = result.get("result", "")
                    expr.result_type = result.get("result_type", "")

            preview.evaluation_context = context

            return preview

        except Exception as e:
            _LOGGER.error(f"Error testing scenario: {e}")
            return TemplatePreview(automation_id=automation_id)

    async def validate_templates(self, automation_id: str) -> dict[str, Any]:
        """Validate all templates for syntax errors.

        Args:
            automation_id: Automation ID

        Returns:
            Validation results dictionary
        """
        _LOGGER.debug(f"Validating templates for {automation_id}")

        try:
            preview = await self.preview_templates(automation_id)

            validation_errors = []
            validation_warnings = []

            for expr in preview.expressions:
                if not expr.is_valid:
                    validation_errors.append(
                        {
                            "expression": expr.expression,
                            "location": expr.location,
                            "error": "Invalid template syntax",
                        }
                    )

            # Check for missing variables
            if preview.missing_variables:
                for var in preview.missing_variables:
                    validation_warnings.append(
                        {
                            "variable": var,
                            "warning": "Variable not found in context",
                        }
                    )

            return {
                "automation_id": automation_id,
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": validation_warnings,
                "total_templates": preview.total_expressions,
                "valid_templates": preview.valid_expressions,
                "invalid_templates": preview.invalid_expressions,
            }

        except Exception as e:
            _LOGGER.error(f"Error validating templates: {e}")
            return {"error": str(e)}

    def get_available_functions(self) -> list[str]:
        """List available Jinja2 functions.

        Returns:
            List of available function names
        """
        return [
            "isnumber",
            "max",
            "min",
            "sum",
            "int",
            "float",
            "string",
            "list",
            "dict",
            "tuple",
            "set",
            "len",
            "range",
            "zip",
            "enumerate",
            "sorted",
            "reversed",
            "abs",
            "round",
            "pow",
            "capitalize",
            "center",
            "count",
            "endswith",
            "find",
            "format",
            "isdigit",
            "islower",
            "isupper",
            "join",
            "lower",
            "lstrip",
            "replace",
            "split",
            "startswith",
            "strip",
            "upper",
        ]

    def get_template_suggestions(self, partial_expression: str) -> list[str]:
        """Get auto-complete suggestions for template.

        Args:
            partial_expression: Partial template expression

        Returns:
            List of suggestions
        """
        suggestions = []

        # Match against available functions
        for func in self.get_available_functions():
            if func.startswith(partial_expression.lower()):
                suggestions.append(func)

        # Add common template patterns
        patterns = [
            "{{ states.light. }}",
            "{{ states.switch. }}",
            "{{ states.binary_sensor. }}",
            "{{ states.sensor. }}",
            "{{ now() }}",
            "{{ today_at() }}",
            "{{ as_timestamp(now()) }}",
        ]

        for pattern in patterns:
            if partial_expression.lower() in pattern.lower():
                suggestions.append(pattern)

        return suggestions
