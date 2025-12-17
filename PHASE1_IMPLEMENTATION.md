# Phase 1 Implementation: Foundation & Backend

**Status:** ✅ COMPLETE

This directory contains the Phase 1 implementation of the Visual AutoView integration for Home Assistant. Phase 1 establishes the foundation and backend infrastructure for the automation graph visualization feature.

## What's Included

### 1. Custom Integration Structure (`custom_components/visualautoview/`)

The integration is structured as a standard Home Assistant custom component:

- **`manifest.json`** - Integration metadata and configuration
  - Domain: `visualautoview`
  - Version: 0.1.0
  - No external dependencies (uses HA built-ins only)
  - Configured as a system integration type

- **`__init__.py`** - Integration initialization and setup
  - `async_setup()` - Initializes integration and sets up domain storage
  - `async_setup_entry()` - Configures entries from config flow
  - `async_unload_entry()` - Cleans up when integration is unloaded
  - Proper logging with module-level logger

- **`const.py`** - Constants and configuration
  - Component type constants (trigger, condition, action, metadata)
  - Color scheme for visual nodes:
    - Triggers: Green (#4CAF50)
    - Conditions: Amber (#FFC107)
    - Actions: Blue (#2196F3)
    - Metadata: Grey (#9E9E9E)
  - Default values for node IDs

- **`graph_parser.py`** - Core automation parsing logic
  - Data models using Python dataclasses:
    - `AutomationNode` - Represents a single automation component
    - `AutomationEdge` - Represents connections between components
    - `AutomationGraph` - Complete automation visualization graph
  - `AutomationGraphParser` class with methods:
    - `parse_automation()` - Main entry point for parsing
    - `_extract_triggers()` - Parse trigger configurations
    - `_extract_conditions()` - Parse condition configurations
    - `_extract_actions()` - Parse action configurations
    - `_build_edges()` - Create connections between components
    - `_format_*_label()` - Generate human-readable labels for nodes
  - Support for various trigger types: state, time, sun, numeric_state, template
  - Support for various condition types: state, numeric_state, sun, time, template
  - Support for various action types: service calls, delays, choose/if-then, parallel, repeat, scenes

### 2. Comprehensive Unit Tests (`tests/test_graph_parser.py`)

**17 passing tests** covering:

#### Data Model Tests
- `TestAutomationNode` - Node creation and serialization
- `TestAutomationEdge` - Edge creation and serialization  
- `TestAutomationGraph` - Graph creation and JSON conversion

#### Automation Parsing Tests
- Simple automation with trigger, condition, and action
- Multiple triggers (OR logic)
- Multiple conditions (AND logic)
- Multiple actions in sequence
- Complex automation combining all features
- Automations without conditions

#### Edge Cases & Formatting
- Automations with missing fields (no alias, no conditions)
- List vs single-item triggers
- Label formatting for all trigger platforms
- Label formatting for all condition types
- Label formatting for all action types

### 3. Test Configuration

- **`conftest.py`** - Pytest configuration and fixtures
- **`pytest.ini`** - Pytest settings and test discovery patterns
- **`tests/__init__.py`** - Package marker for tests

## Data Model

### AutomationNode
```python
@dataclass
class AutomationNode:
    id: str                              # Unique node identifier
    label: str                           # Human-readable display label
    type: Literal["trigger", "condition", "action", "metadata"]  # Node type
    data: dict[str, Any]                 # Complete automation configuration
    color: str | None = None             # Hex color for visualization
```

### AutomationEdge
```python
@dataclass
class AutomationEdge:
    from_node: str                       # Source node ID
    to_node: str                         # Target node ID
    label: str | None = None             # Optional edge label ("if", "then", "AND")
```

### AutomationGraph
```python
@dataclass
class AutomationGraph:
    nodes: list[AutomationNode]          # All nodes in the automation
    edges: list[AutomationEdge]          # All connections between nodes
    metadata: dict[str, Any]             # Automation metadata (id, alias, description)
```

## Graph Structure Example

For the automation:
```yaml
id: 'motion_light'
alias: 'Motion Light Control'
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: 'on'
condition:
  - condition: sun
    after: sunset
    before: sunrise
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
  - delay:
      seconds: 30
  - service: light.turn_off
    target:
      entity_id: light.living_room
```

The parser generates:
- **7 Nodes:**
  1. Metadata: "Motion Light Control"
  2. Trigger: "State: binary_sensor.motion → on"
  3. Condition: "Sun: after sunset, before sunrise"
  4. Action: "Service: light.turn_on"
  5. Action: "Delay: 30 seconds"
  6. Action: "Service: light.turn_off"

- **5 Edges connecting:** Metadata → Trigger → Condition → Action → Action → Action

## Usage

### Installing the Integration

1. Create `custom_components/visualautoview/` in your Home Assistant configuration directory
2. Copy all files from `custom_components/visualautoview/` to that location
3. Restart Home Assistant
4. The integration will be available in Developer Tools → Services

### Using the Parser

```python
from custom_components.visualautoview.graph_parser import parse_automation

automation_config = {
    "id": "example",
    "alias": "Example Automation",
    "trigger": {...},
    "condition": [...],
    "action": [...]
}

graph = parse_automation(automation_config)

# Access graph data
print(f"Nodes: {len(graph.nodes)}")
print(f"Edges: {len(graph.edges)}")

# Convert to JSON for API response
graph_json = graph.to_dict()
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pyyaml

# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_graph_parser.py::TestSimpleAutomation -v

# Run with coverage
pytest tests/ --cov=custom_components/visualautoview
```

## Supported Automation Features

### Triggers
- ✅ State changes
- ✅ Time-based (specific time, sun events)
- ✅ Numeric state changes
- ✅ Template conditions
- ✅ Multiple triggers (OR logic)

### Conditions
- ✅ State conditions
- ✅ Numeric state conditions
- ✅ Sun position conditions
- ✅ Time-based conditions
- ✅ Template conditions
- ✅ Multiple conditions (AND logic)

### Actions
- ✅ Service calls
- ✅ Delays
- ✅ Choose/If-Then statements
- ✅ Parallel actions
- ✅ Repeat loops
- ✅ Scene activation
- ✅ Multiple sequential actions

## Architecture Decisions

### 1. Dataclass-Based Models
Used Python dataclasses for:
- Type safety with type hints
- Automatic `__init__` and serialization
- Easy JSON conversion via `asdict()`
- Clean, readable code

### 2. Parser as Separate Class
- Encapsulates parsing logic
- Node counter for unique IDs maintained per parse
- Reusable for multiple automations
- Convenience function wrapper for simple usage

### 3. Flexible Imports
- Handles both relative imports (when used as HA integration) and absolute imports (for testing)
- Allows testing without Home Assistant environment
- Forward-compatible with future refactoring

### 4. Comprehensive Label Generation
- Static methods for formatting labels based on automation type
- Human-readable display strings for all common automation components
- Extensible for custom/advanced automation features

## Next Steps (Phase 2)

Phase 2 will build on this foundation:

- Frontend infrastructure setup (npm, TypeScript, Lit)
- vis-network graph rendering
- Custom web components for graph display
- Integration with Home Assistant's frontend framework

## File Checklist for Phase 1

- ✅ `custom_components/visualautoview/__init__.py`
- ✅ `custom_components/visualautoview/manifest.json`
- ✅ `custom_components/visualautoview/const.py`
- ✅ `custom_components/visualautoview/graph_parser.py`
- ✅ `tests/__init__.py`
- ✅ `tests/test_graph_parser.py`
- ✅ `conftest.py`
- ✅ `pytest.ini`

## Verification

All 17 unit tests pass:
```
tests/test_graph_parser.py::TestAutomationNode::test_node_creation PASSED
tests/test_graph_parser.py::TestAutomationNode::test_node_to_dict PASSED
tests/test_graph_parser.py::TestAutomationEdge::test_edge_creation PASSED
tests/test_graph_parser.py::TestAutomationEdge::test_edge_to_dict PASSED
tests/test_graph_parser.py::TestAutomationGraph::test_empty_graph_creation PASSED
tests/test_graph_parser.py::TestAutomationGraph::test_graph_to_dict PASSED
tests/test_graph_parser.py::TestSimpleAutomation::test_simple_automation_parsing PASSED
tests/test_graph_parser.py::TestSimpleAutomation::test_automation_with_multiple_triggers PASSED
tests/test_graph_parser.py::TestSimpleAutomation::test_automation_with_conditions PASSED
tests/test_graph_parser.py::TestSimpleAutomation::test_automation_with_multiple_actions PASSED
tests/test_graph_parser.py::TestSimpleAutomation::test_complex_automation PASSED
tests/test_graph_parser.py::TestEdgeCases::test_automation_without_conditions PASSED
tests/test_graph_parser.py::TestEdgeCases::test_automation_with_list_trigger PASSED
tests/test_graph_parser.py::TestEdgeCases::test_automation_with_no_alias PASSED
tests/test_graph_parser.py::TestEdgeCases::test_trigger_label_formatting PASSED
tests/test_graph_parser.py::TestEdgeCases::test_condition_label_formatting PASSED
tests/test_graph_parser.py::TestEdgeCases::test_action_label_formatting PASSED
```

---

**Phase 1 Status:** Ready for Phase 2 (Frontend Setup)  
**Implementation Date:** December 16, 2025  
**Test Coverage:** 17 tests, all passing
