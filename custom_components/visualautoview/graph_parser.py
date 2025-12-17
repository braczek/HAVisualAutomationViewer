"""Graph parser for Home Assistant automations.

This module handles parsing automation configurations and converting them
into graph data structures (nodes and edges) for visualization.
"""

import logging
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Literal

try:
    from .const import (
        COMP_TYPE_TRIGGER,
        COMP_TYPE_CONDITION,
        COMP_TYPE_ACTION,
        COMP_TYPE_METADATA,
        COLORS,
        DEFAULT_NODE_ID_PREFIX,
    )
except ImportError:
    # Fallback for testing without parent package
    from const import (
        COMP_TYPE_TRIGGER,
        COMP_TYPE_CONDITION,
        COMP_TYPE_ACTION,
        COMP_TYPE_METADATA,
        COLORS,
        DEFAULT_NODE_ID_PREFIX,
    )

_LOGGER = logging.getLogger(__name__)


@dataclass
class AutomationNode:
    """Represents a node in the automation graph."""

    id: str
    label: str
    type: Literal["trigger", "condition", "action", "metadata"]
    data: dict[str, Any]
    color: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class AutomationEdge:
    """Represents an edge connection between nodes."""

    from_node: str
    to_node: str
    label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert edge to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class AutomationGraph:
    """Complete graph representation of an automation."""

    nodes: list[AutomationNode] = field(default_factory=list)
    edges: list[AutomationEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert graph to dictionary for JSON serialization."""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }


class AutomationGraphParser:
    """Parser for Home Assistant automation configurations."""

    def __init__(self) -> None:
        """Initialize the parser."""
        self._node_counter = 0

    def _generate_node_id(self, prefix: str = "") -> str:
        """Generate a unique node ID."""
        self._node_counter += 1
        if prefix:
            return f"{prefix}_{self._node_counter}"
        return f"{DEFAULT_NODE_ID_PREFIX}{self._node_counter}"

    def parse_automation(self, automation_config: dict[str, Any]) -> AutomationGraph:
        """Parse an automation configuration into a graph structure.

        Args:
            automation_config: The automation configuration dictionary

        Returns:
            AutomationGraph: The parsed automation as a graph
        """
        graph = AutomationGraph()
        self._node_counter = 0

        try:
            # Extract metadata
            metadata_id = self._extract_metadata(automation_config, graph)

            # Extract triggers
            trigger_ids = self._extract_triggers(automation_config, graph)

            # Extract conditions
            condition_ids = self._extract_conditions(automation_config, graph)

            # Extract actions
            action_ids = self._extract_actions(automation_config, graph)

            # Build edges connecting the components
            self._build_edges(
                graph, metadata_id, trigger_ids, condition_ids, action_ids
            )

        except Exception as e:
            _LOGGER.error(f"Error parsing automation: {e}")
            raise

        return graph

    def _extract_metadata(
        self, automation_config: dict[str, Any], graph: AutomationGraph
    ) -> str:
        """Extract metadata from automation config.

        Args:
            automation_config: The automation configuration
            graph: The graph to add nodes to

        Returns:
            str: The ID of the metadata node
        """
        metadata_node_id = self._generate_node_id("metadata")
        
        alias = automation_config.get("alias", "Automation")
        description = automation_config.get("description", "")
        automation_id = automation_config.get("id", "unknown")

        node = AutomationNode(
            id=metadata_node_id,
            label=alias,
            type=COMP_TYPE_METADATA,
            data={
                "automation_id": automation_id,
                "alias": alias,
                "description": description,
            },
            color=COLORS[COMP_TYPE_METADATA],
        )
        
        graph.nodes.append(node)
        graph.metadata["automation_id"] = automation_id
        graph.metadata["alias"] = alias
        
        return metadata_node_id

    def _extract_triggers(
        self, automation_config: dict[str, Any], graph: AutomationGraph
    ) -> list[str]:
        """Extract triggers from automation config.

        Args:
            automation_config: The automation configuration
            graph: The graph to add nodes to

        Returns:
            list[str]: List of trigger node IDs
        """
        triggers = automation_config.get("trigger", [])
        if not isinstance(triggers, list):
            triggers = [triggers]

        trigger_ids = []
        for idx, trigger in enumerate(triggers):
            trigger_id = self._generate_node_id("trigger")
            
            trigger_type = trigger.get("platform", "unknown")
            label = self._format_trigger_label(trigger, idx)

            node = AutomationNode(
                id=trigger_id,
                label=label,
                type=COMP_TYPE_TRIGGER,
                data=trigger,
                color=COLORS[COMP_TYPE_TRIGGER],
            )
            
            graph.nodes.append(node)
            trigger_ids.append(trigger_id)

        return trigger_ids

    def _extract_conditions(
        self, automation_config: dict[str, Any], graph: AutomationGraph
    ) -> list[str]:
        """Extract conditions from automation config.

        Args:
            automation_config: The automation configuration
            graph: The graph to add nodes to

        Returns:
            list[str]: List of condition node IDs
        """
        conditions = automation_config.get("condition", [])
        if not isinstance(conditions, list):
            if conditions:
                conditions = [conditions]
            else:
                conditions = []

        condition_ids = []
        for idx, condition in enumerate(conditions):
            condition_id = self._generate_node_id("condition")
            
            label = self._format_condition_label(condition, idx)

            node = AutomationNode(
                id=condition_id,
                label=label,
                type=COMP_TYPE_CONDITION,
                data=condition,
                color=COLORS[COMP_TYPE_CONDITION],
            )
            
            graph.nodes.append(node)
            condition_ids.append(condition_id)

        return condition_ids

    def _extract_actions(
        self, automation_config: dict[str, Any], graph: AutomationGraph
    ) -> list[str]:
        """Extract actions from automation config.

        Args:
            automation_config: The automation configuration
            graph: The graph to add nodes to

        Returns:
            list[str]: List of action node IDs
        """
        actions = automation_config.get("action", [])
        if not isinstance(actions, list):
            actions = [actions] if actions else []

        action_ids = []
        for idx, action in enumerate(actions):
            action_id = self._generate_node_id("action")
            
            label = self._format_action_label(action, idx)

            node = AutomationNode(
                id=action_id,
                label=label,
                type=COMP_TYPE_ACTION,
                data=action,
                color=COLORS[COMP_TYPE_ACTION],
            )
            
            graph.nodes.append(node)
            action_ids.append(action_id)

        return action_ids

    def _build_edges(
        self,
        graph: AutomationGraph,
        metadata_id: str,
        trigger_ids: list[str],
        condition_ids: list[str],
        action_ids: list[str],
    ) -> None:
        """Build edges connecting automation components.

        Args:
            graph: The graph to add edges to
            metadata_id: The metadata node ID
            trigger_ids: List of trigger node IDs
            condition_ids: List of condition node IDs
            action_ids: List of action node IDs
        """
        # Metadata -> Triggers
        for trigger_id in trigger_ids:
            graph.edges.append(
                AutomationEdge(from_node=metadata_id, to_node=trigger_id)
            )

        # Triggers -> Conditions (if conditions exist)
        if condition_ids:
            for trigger_id in trigger_ids:
                # Connect to first condition
                graph.edges.append(
                    AutomationEdge(
                        from_node=trigger_id,
                        to_node=condition_ids[0],
                        label="if",
                    )
                )

            # Connect conditions in sequence
            for i in range(len(condition_ids) - 1):
                graph.edges.append(
                    AutomationEdge(
                        from_node=condition_ids[i],
                        to_node=condition_ids[i + 1],
                        label="AND",
                    )
                )

            # Last condition -> First action
            if action_ids:
                graph.edges.append(
                    AutomationEdge(
                        from_node=condition_ids[-1],
                        to_node=action_ids[0],
                        label="then",
                    )
                )
        else:
            # Triggers -> Actions (no conditions)
            for trigger_id in trigger_ids:
                if action_ids:
                    graph.edges.append(
                        AutomationEdge(from_node=trigger_id, to_node=action_ids[0])
                    )

        # Connect actions in sequence
        for i in range(len(action_ids) - 1):
            graph.edges.append(
                AutomationEdge(from_node=action_ids[i], to_node=action_ids[i + 1])
            )

    @staticmethod
    def _format_trigger_label(trigger: dict[str, Any], index: int) -> str:
        """Format a label for a trigger node.

        Args:
            trigger: The trigger configuration
            index: The trigger index

        Returns:
            str: Formatted label
        """
        platform = trigger.get("platform", "unknown")
        
        if platform == "state":
            entity_id = trigger.get("entity_id", "unknown")
            to_state = trigger.get("to", "")
            if to_state:
                return f"State: {entity_id} → {to_state}"
            return f"State: {entity_id}"
        elif platform == "time":
            at_time = trigger.get("at", "unknown")
            return f"Time: {at_time}"
        elif platform == "sun":
            event = trigger.get("event", "rise")
            return f"Sun: {event}"
        elif platform == "numeric_state":
            entity_id = trigger.get("entity_id", "unknown")
            return f"Numeric: {entity_id}"
        elif platform == "template":
            return f"Template trigger"
        else:
            return f"Trigger: {platform} #{index + 1}"

    @staticmethod
    def _format_condition_label(condition: dict[str, Any], index: int) -> str:
        """Format a label for a condition node.

        Args:
            condition: The condition configuration
            index: The condition index

        Returns:
            str: Formatted label
        """
        condition_type = condition.get("condition", "unknown")
        
        if condition_type == "state":
            entity_id = condition.get("entity_id", "unknown")
            state = condition.get("state", "unknown")
            return f"State: {entity_id} = {state}"
        elif condition_type == "numeric_state":
            entity_id = condition.get("entity_id", "unknown")
            return f"Numeric: {entity_id}"
        elif condition_type == "sun":
            after = condition.get("after", "")
            before = condition.get("before", "")
            parts = []
            if after:
                parts.append(f"after {after}")
            if before:
                parts.append(f"before {before}")
            if parts:
                return f"Sun: {', '.join(parts)}"
            return "Sun condition"
        elif condition_type == "time":
            after = condition.get("after", "")
            before = condition.get("before", "")
            parts = []
            if after:
                parts.append(f"after {after}")
            if before:
                parts.append(f"before {before}")
            if parts:
                return f"Time: {', '.join(parts)}"
            return "Time condition"
        elif condition_type == "template":
            return "Template condition"
        else:
            return f"Condition: {condition_type} #{index + 1}"

    @staticmethod
    def _format_action_label(action: dict[str, Any], index: int) -> str:
        """Format a label for an action node.

        Args:
            action: The action configuration
            index: The action index

        Returns:
            str: Formatted label
        """
        if isinstance(action, str):
            # Simple string action (service call)
            return f"Action: {action}"
        
        if "service" in action:
            service = action.get("service", "unknown")
            # Format: domain.service
            return f"Service: {service}"
        elif "delay" in action:
            delay_str = action.get("delay", "unknown")
            return f"Delay: {delay_str}"
        elif "wait_template" in action:
            return "Wait for template"
        elif "choose" in action:
            return "Choose/If-Then"
        elif "parallel" in action:
            return "Parallel actions"
        elif "repeat" in action:
            return "Repeat loop"
        elif "scene" in action:
            scene = action.get("scene", "unknown")
            return f"Scene: {scene}"
        else:
            return f"Action #{index + 1}"


def parse_automation(automation_config: dict[str, Any]) -> AutomationGraph:
    """Parse an automation configuration into a graph structure.

    This is a convenience function that creates a parser and parses
    the automation in one call.

    Args:
        automation_config: The automation configuration dictionary

    Returns:
        AutomationGraph: The parsed automation as a graph
    """
    parser = AutomationGraphParser()
    return parser.parse_automation(automation_config)
