"""Unit tests for the graph parser module."""

import importlib.util
import sys
from pathlib import Path

import pytest

# Load the modules directly without going through __init__.py
spec_const = importlib.util.spec_from_file_location(
    "const",
    Path(__file__).parent.parent / "custom_components" / "visualautoview" / "const.py",
)
if spec_const is None or spec_const.loader is None:
    raise ImportError("Could not load const module")
const = importlib.util.module_from_spec(spec_const)
sys.modules["const"] = const
spec_const.loader.exec_module(const)

spec_parser = importlib.util.spec_from_file_location(
    "graph_parser",
    Path(__file__).parent.parent
    / "custom_components"
    / "visualautoview"
    / "graph_parser.py",
)
if spec_parser is None or spec_parser.loader is None:
    raise ImportError("Could not load graph_parser module")
graph_parser = importlib.util.module_from_spec(spec_parser)
sys.modules["graph_parser"] = graph_parser
spec_parser.loader.exec_module(graph_parser)

AutomationNode = graph_parser.AutomationNode
AutomationEdge = graph_parser.AutomationEdge
AutomationGraph = graph_parser.AutomationGraph
AutomationGraphParser = graph_parser.AutomationGraphParser
parse_automation = graph_parser.parse_automation

COMP_TYPE_TRIGGER = const.COMP_TYPE_TRIGGER
COMP_TYPE_CONDITION = const.COMP_TYPE_CONDITION
COMP_TYPE_ACTION = const.COMP_TYPE_ACTION
COMP_TYPE_METADATA = const.COMP_TYPE_METADATA


class TestAutomationNode:
    """Tests for AutomationNode class."""

    def test_node_creation(self):
        """Test creating a node."""
        node = AutomationNode(
            id="test_1",
            label="Test Node",
            type=COMP_TYPE_TRIGGER,
            data={"platform": "state"},
            color="#4CAF50",
        )

        assert node.id == "test_1"
        assert node.label == "Test Node"
        assert node.type == COMP_TYPE_TRIGGER
        assert node.color == "#4CAF50"

    def test_node_to_dict(self):
        """Test converting node to dictionary."""
        node = AutomationNode(
            id="test_1",
            label="Test Node",
            type=COMP_TYPE_TRIGGER,
            data={"platform": "state"},
            color="#4CAF50",
        )

        node_dict = node.to_dict()
        assert node_dict["id"] == "test_1"
        assert node_dict["label"] == "Test Node"
        assert node_dict["type"] == COMP_TYPE_TRIGGER


class TestAutomationEdge:
    """Tests for AutomationEdge class."""

    def test_edge_creation(self):
        """Test creating an edge."""
        edge = AutomationEdge(
            from_node="node_1",
            to_node="node_2",
            label="connects_to",
        )

        assert edge.from_node == "node_1"
        assert edge.to_node == "node_2"
        assert edge.label == "connects_to"

    def test_edge_to_dict(self):
        """Test converting edge to dictionary."""
        edge = AutomationEdge(
            from_node="node_1",
            to_node="node_2",
        )

        edge_dict = edge.to_dict()
        assert edge_dict["from"] == "node_1"
        assert edge_dict["to"] == "node_2"


class TestAutomationGraph:
    """Tests for AutomationGraph class."""

    def test_empty_graph_creation(self):
        """Test creating an empty graph."""
        graph = AutomationGraph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph.metadata) == 0

    def test_graph_to_dict(self):
        """Test converting graph to dictionary."""
        node = AutomationNode(
            id="test_1",
            label="Test",
            type=COMP_TYPE_TRIGGER,
            data={},
        )
        edge = AutomationEdge(from_node="test_1", to_node="test_2")

        graph = AutomationGraph(
            nodes=[node],
            edges=[edge],
            metadata={"test": "value"},
        )

        graph_dict = graph.to_dict()
        assert len(graph_dict["nodes"]) == 1
        assert len(graph_dict["edges"]) == 1
        assert graph_dict["metadata"]["test"] == "value"


class TestSimpleAutomation:
    """Tests for parsing simple automations."""

    def test_simple_automation_parsing(self):
        """Test parsing a simple automation."""
        automation = {
            "id": "test_automation",
            "alias": "Test Automation",
            "description": "A test automation",
            "trigger": {
                "platform": "state",
                "entity_id": "sensor.test",
                "to": "on",
            },
            "condition": [],
            "action": {
                "service": "light.turn_on",
                "target": {"entity_id": "light.test"},
            },
        }

        graph = parse_automation(automation)

        # Should have: metadata, trigger, action nodes
        assert len(graph.nodes) >= 3

        # Check node types exist
        node_types = [node.type for node in graph.nodes]
        assert COMP_TYPE_METADATA in node_types
        assert COMP_TYPE_TRIGGER in node_types
        assert COMP_TYPE_ACTION in node_types

        # Check edges exist
        assert len(graph.edges) > 0

    def test_automation_with_multiple_triggers(self):
        """Test parsing automation with multiple triggers."""
        automation = {
            "id": "multi_trigger",
            "alias": "Multi Trigger",
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": "sensor.test1",
                    "to": "on",
                },
                {
                    "platform": "time",
                    "at": "12:00:00",
                },
            ],
            "condition": [],
            "action": {
                "service": "light.turn_on",
                "target": {"entity_id": "light.test"},
            },
        }

        graph = parse_automation(automation)

        # Count trigger nodes
        trigger_nodes = [n for n in graph.nodes if n.type == COMP_TYPE_TRIGGER]
        assert len(trigger_nodes) == 2

    def test_automation_with_conditions(self):
        """Test parsing automation with conditions."""
        automation = {
            "id": "with_conditions",
            "alias": "With Conditions",
            "trigger": {
                "platform": "state",
                "entity_id": "sensor.test",
            },
            "condition": [
                {
                    "condition": "state",
                    "entity_id": "light.test",
                    "state": "off",
                },
                {
                    "condition": "sun",
                    "after": "sunset",
                    "before": "sunrise",
                },
            ],
            "action": {
                "service": "light.turn_on",
                "target": {"entity_id": "light.test"},
            },
        }

        graph = parse_automation(automation)

        # Check for condition nodes
        condition_nodes = [n for n in graph.nodes if n.type == COMP_TYPE_CONDITION]
        assert len(condition_nodes) == 2

        # Check edges connect properly
        assert len(graph.edges) > 0

    def test_automation_with_multiple_actions(self):
        """Test parsing automation with multiple actions."""
        automation = {
            "id": "multi_action",
            "alias": "Multi Action",
            "trigger": {
                "platform": "state",
                "entity_id": "sensor.test",
            },
            "condition": [],
            "action": [
                {
                    "service": "light.turn_on",
                    "target": {"entity_id": "light.test"},
                },
                {
                    "delay": {"seconds": 30},
                },
                {
                    "service": "light.turn_off",
                    "target": {"entity_id": "light.test"},
                },
            ],
        }

        graph = parse_automation(automation)

        # Count action nodes
        action_nodes = [n for n in graph.nodes if n.type == COMP_TYPE_ACTION]
        assert len(action_nodes) == 3

        # Check actions are connected in sequence
        action_edges = [
            e for e in graph.edges if e.from_node in [n.id for n in action_nodes]
        ]
        assert len(action_edges) >= 2  # At least 2 edges connecting 3 actions

    def test_complex_automation(self):
        """Test parsing complex automation with triggers, conditions, and actions."""
        automation = {
            "id": "complex",
            "alias": "Motion Light Control",
            "description": "Turn on lights when motion detected",
            "trigger": {
                "platform": "state",
                "entity_id": "binary_sensor.motion_sensor",
                "to": "on",
            },
            "condition": [
                {
                    "condition": "sun",
                    "after": "sunset",
                    "before": "sunrise",
                },
                {
                    "condition": "state",
                    "entity_id": "light.living_room",
                    "state": "off",
                },
            ],
            "action": [
                {
                    "service": "light.turn_on",
                    "target": {"entity_id": "light.living_room"},
                    "data": {"brightness": 255},
                },
                {
                    "delay": {"seconds": 30},
                },
                {
                    "service": "light.turn_off",
                    "target": {"entity_id": "light.living_room"},
                },
            ],
        }

        graph = parse_automation(automation)

        # Verify complete structure
        assert graph.metadata["alias"] == "Motion Light Control"
        assert graph.metadata["automation_id"] == "complex"

        # Check all node types present
        node_types = [n.type for n in graph.nodes]
        assert COMP_TYPE_METADATA in node_types
        assert COMP_TYPE_TRIGGER in node_types
        assert COMP_TYPE_CONDITION in node_types
        assert COMP_TYPE_ACTION in node_types

        # Check nodes
        assert len([n for n in graph.nodes if n.type == COMP_TYPE_CONDITION]) == 2
        assert len([n for n in graph.nodes if n.type == COMP_TYPE_ACTION]) == 3

        # Check edges
        assert len(graph.edges) > 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_automation_without_conditions(self):
        """Test parsing automation without conditions."""
        automation = {
            "id": "no_conditions",
            "alias": "No Conditions",
            "trigger": {
                "platform": "state",
                "entity_id": "sensor.test",
            },
            "action": {
                "service": "light.turn_on",
                "target": {"entity_id": "light.test"},
            },
        }

        graph = parse_automation(automation)

        # Should still work
        assert len(graph.nodes) >= 3
        assert len(graph.edges) > 0

    def test_automation_with_list_trigger(self):
        """Test automation with trigger as list."""
        automation = {
            "id": "list_trigger",
            "alias": "List Trigger",
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": "sensor.test",
                },
            ],
            "action": {
                "service": "light.turn_on",
                "target": {"entity_id": "light.test"},
            },
        }

        graph = parse_automation(automation)
        assert len(graph.nodes) >= 3

    def test_automation_with_no_alias(self):
        """Test automation without alias uses default."""
        automation = {
            "id": "no_alias",
            "trigger": {
                "platform": "state",
                "entity_id": "sensor.test",
            },
            "action": {
                "service": "light.turn_on",
                "target": {"entity_id": "light.test"},
            },
        }

        graph = parse_automation(automation)

        # Should use default alias
        metadata_node = next(
            (n for n in graph.nodes if n.type == COMP_TYPE_METADATA), None
        )
        assert metadata_node is not None
        assert metadata_node.label == "Automation"

    def test_trigger_label_formatting(self):
        """Test trigger label formatting for various platforms."""
        parser = AutomationGraphParser()

        # State trigger
        state_trigger = {"platform": "state", "entity_id": "sensor.test", "to": "on"}
        label = parser._format_trigger_label(state_trigger, 0)
        assert "sensor.test" in label
        assert "on" in label

        # Time trigger
        time_trigger = {"platform": "time", "at": "12:00:00"}
        label = parser._format_trigger_label(time_trigger, 0)
        assert "12:00:00" in label

        # Sun trigger
        sun_trigger = {"platform": "sun", "event": "sunset"}
        label = parser._format_trigger_label(sun_trigger, 0)
        assert "sunset" in label

    def test_condition_label_formatting(self):
        """Test condition label formatting for various types."""
        parser = AutomationGraphParser()

        # State condition
        state_cond = {
            "condition": "state",
            "entity_id": "light.test",
            "state": "off",
        }
        label = parser._format_condition_label(state_cond, 0)
        assert "light.test" in label
        assert "off" in label

        # Sun condition
        sun_cond = {
            "condition": "sun",
            "after": "sunset",
            "before": "sunrise",
        }
        label = parser._format_condition_label(sun_cond, 0)
        assert "sunset" in label
        assert "sunrise" in label

    def test_action_label_formatting(self):
        """Test action label formatting for various types."""
        parser = AutomationGraphParser()

        # Service action
        service_action = {
            "service": "light.turn_on",
            "target": {"entity_id": "light.test"},
        }
        label = parser._format_action_label(service_action, 0)
        assert "light.turn_on" in label

        # Delay action
        delay_action = {"delay": {"seconds": 30}}
        label = parser._format_action_label(delay_action, 0)
        assert "30" in label


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
