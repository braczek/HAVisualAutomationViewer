"""Graph parser for Home Assistant automations.

This module handles parsing automation configurations and converting them
into graph data structures (nodes and edges) for visualization.
"""

import logging
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

try:
    from .const import (
        COLORS,
        COMP_TYPE_ACTION,
        COMP_TYPE_CONDITION,
        COMP_TYPE_METADATA,
        COMP_TYPE_TRIGGER,
        DEFAULT_NODE_ID_PREFIX,
    )
except ImportError:
    # Fallback for testing without parent package
    from const import (
        COLORS,
        COMP_TYPE_ACTION,
        COMP_TYPE_CONDITION,
        COMP_TYPE_METADATA,
        COMP_TYPE_TRIGGER,
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
        """Convert edge to dictionary for JSON serialization with vis-network format."""
        return {
            "from": self.from_node,
            "to": self.to_node,
            "label": self.label,
        }


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
        # Accept both "trigger" and "triggers" field names
        triggers = automation_config.get("triggers") or automation_config.get(
            "trigger", []
        )
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
        # Accept both "condition" and "conditions" field names
        conditions = automation_config.get("conditions") or automation_config.get(
            "condition", []
        )
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
        # Accept both "action" and "actions" field names
        actions = automation_config.get("actions") or automation_config.get(
            "action", []
        )
        if not isinstance(actions, list):
            actions = [actions] if actions else []

        action_ids = []
        for idx, action in enumerate(actions):
            # Process nested actions recursively
            nested_ids = self._process_action_recursive(action, idx, graph)
            action_ids.extend(nested_ids)

        return action_ids

    def _process_action_recursive(
        self,
        action: dict[str, Any],
        index: int,
        graph: AutomationGraph,
        parent_id: str | None = None,
    ) -> list[str]:
        """Process an action recursively, handling nested structures.

        Args:
            action: The action configuration
            index: The action index
            graph: The graph to add nodes to
            parent_id: Optional parent node ID for nested actions

        Returns:
            list[str]: List of action node IDs created
        """
        action_ids = []

        # Handle choose/if-then structures
        if "choose" in action:
            choose_id = self._generate_node_id("action")
            node = AutomationNode(
                id=choose_id,
                label="Choose/If-Then",
                type=COMP_TYPE_ACTION,
                data={"type": "choose"},
                color=COLORS[COMP_TYPE_ACTION],
            )
            graph.nodes.append(node)
            action_ids.append(choose_id)

            # Process each choice branch
            choose_list = action.get("choose", [])
            if not isinstance(choose_list, list):
                choose_list = [choose_list]

            for choice_idx, choice in enumerate(choose_list):
                # Create a branch node
                branch_id = self._generate_node_id("action")
                branch_label = f"Branch {choice_idx + 1}"

                # Check if there are conditions for this choice
                if "conditions" in choice or "condition" in choice:
                    conditions = choice.get("conditions") or choice.get("condition", [])
                    if not isinstance(conditions, list):
                        conditions = [conditions] if conditions else []
                    if conditions:
                        cond_summary = self._summarize_conditions(conditions)
                        branch_label = f"If: {cond_summary}"

                branch_node = AutomationNode(
                    id=branch_id,
                    label=branch_label,
                    type=COMP_TYPE_CONDITION,
                    data=choice.get("conditions") or choice.get("condition", {}),
                    color=COLORS[COMP_TYPE_CONDITION],
                )
                graph.nodes.append(branch_node)
                graph.edges.append(
                    AutomationEdge(
                        from_node=choose_id,
                        to_node=branch_id,
                        label=f"option {choice_idx + 1}",
                    )
                )

                # Process sequence of actions in this branch
                sequence = choice.get("sequence", [])
                if not isinstance(sequence, list):
                    sequence = [sequence] if sequence else []

                prev_id = branch_id
                for seq_idx, seq_action in enumerate(sequence):
                    seq_ids = self._process_action_recursive(
                        seq_action, seq_idx, graph, parent_id=branch_id
                    )
                    if seq_ids:
                        # Connect first action in sequence to branch
                        graph.edges.append(
                            AutomationEdge(from_node=prev_id, to_node=seq_ids[0])
                        )
                        # Connect actions in sequence
                        for i in range(len(seq_ids) - 1):
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=seq_ids[i], to_node=seq_ids[i + 1]
                                )
                            )
                        prev_id = seq_ids[-1]

            # Handle default branch
            if "default" in action:
                default_id = self._generate_node_id("action")
                default_node = AutomationNode(
                    id=default_id,
                    label="Default/Else",
                    type=COMP_TYPE_CONDITION,
                    data={"type": "default"},
                    color=COLORS[COMP_TYPE_CONDITION],
                )
                graph.nodes.append(default_node)
                graph.edges.append(
                    AutomationEdge(
                        from_node=choose_id, to_node=default_id, label="else"
                    )
                )

                # Process default sequence
                default_sequence = action.get("default", [])
                if not isinstance(default_sequence, list):
                    default_sequence = [default_sequence] if default_sequence else []

                prev_id = default_id
                for seq_idx, seq_action in enumerate(default_sequence):
                    seq_ids = self._process_action_recursive(
                        seq_action, seq_idx, graph, parent_id=default_id
                    )
                    if seq_ids:
                        graph.edges.append(
                            AutomationEdge(from_node=prev_id, to_node=seq_ids[0])
                        )
                        for i in range(len(seq_ids) - 1):
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=seq_ids[i], to_node=seq_ids[i + 1]
                                )
                            )
                        prev_id = seq_ids[-1]

        # Handle if-then structure
        elif "if" in action:
            if_id = self._generate_node_id("action")

            # Get condition summary
            conditions = action.get("if", [])
            if not isinstance(conditions, list):
                conditions = [conditions] if conditions else []
            cond_summary = self._summarize_conditions(conditions)

            node = AutomationNode(
                id=if_id,
                label=f"If: {cond_summary}",
                type=COMP_TYPE_CONDITION,
                data=action.get("if", {}),
                color=COLORS[COMP_TYPE_CONDITION],
            )
            graph.nodes.append(node)
            action_ids.append(if_id)

            # Process then branch
            if "then" in action:
                then_sequence = action.get("then", [])
                if not isinstance(then_sequence, list):
                    then_sequence = [then_sequence] if then_sequence else []

                prev_id = if_id
                for seq_idx, seq_action in enumerate(then_sequence):
                    seq_ids = self._process_action_recursive(
                        seq_action, seq_idx, graph, parent_id=if_id
                    )
                    if seq_ids:
                        if prev_id == if_id:
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=prev_id, to_node=seq_ids[0], label="then"
                                )
                            )
                        else:
                            graph.edges.append(
                                AutomationEdge(from_node=prev_id, to_node=seq_ids[0])
                            )
                        for i in range(len(seq_ids) - 1):
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=seq_ids[i], to_node=seq_ids[i + 1]
                                )
                            )
                        prev_id = seq_ids[-1]

            # Process else branch
            if "else" in action:
                else_sequence = action.get("else", [])
                if not isinstance(else_sequence, list):
                    else_sequence = [else_sequence] if else_sequence else []

                prev_id = if_id
                for seq_idx, seq_action in enumerate(else_sequence):
                    seq_ids = self._process_action_recursive(
                        seq_action, seq_idx, graph, parent_id=if_id
                    )
                    if seq_ids:
                        if prev_id == if_id:
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=prev_id, to_node=seq_ids[0], label="else"
                                )
                            )
                        else:
                            graph.edges.append(
                                AutomationEdge(from_node=prev_id, to_node=seq_ids[0])
                            )
                        for i in range(len(seq_ids) - 1):
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=seq_ids[i], to_node=seq_ids[i + 1]
                                )
                            )
                        prev_id = seq_ids[-1]

        # Handle parallel actions
        elif "parallel" in action:
            parallel_id = self._generate_node_id("action")
            node = AutomationNode(
                id=parallel_id,
                label="Parallel Actions",
                type=COMP_TYPE_ACTION,
                data={"type": "parallel"},
                color=COLORS[COMP_TYPE_ACTION],
            )
            graph.nodes.append(node)
            action_ids.append(parallel_id)

            # Process each parallel sequence
            parallel_sequences = action.get("parallel", [])
            if not isinstance(parallel_sequences, list):
                parallel_sequences = [parallel_sequences]

            for par_idx, sequence in enumerate(parallel_sequences):
                if not isinstance(sequence, list):
                    sequence = [sequence] if sequence else []

                prev_id = parallel_id
                for seq_idx, seq_action in enumerate(sequence):
                    seq_ids = self._process_action_recursive(
                        seq_action, seq_idx, graph, parent_id=parallel_id
                    )
                    if seq_ids:
                        if prev_id == parallel_id:
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=prev_id,
                                    to_node=seq_ids[0],
                                    label=f"thread {par_idx + 1}",
                                )
                            )
                        else:
                            graph.edges.append(
                                AutomationEdge(from_node=prev_id, to_node=seq_ids[0])
                            )
                        for i in range(len(seq_ids) - 1):
                            graph.edges.append(
                                AutomationEdge(
                                    from_node=seq_ids[i], to_node=seq_ids[i + 1]
                                )
                            )
                        prev_id = seq_ids[-1]

        # Handle repeat loops
        elif "repeat" in action:
            repeat_id = self._generate_node_id("action")
            repeat_config = action.get("repeat", {})

            # Determine repeat type
            repeat_label = "Repeat"
            if "count" in repeat_config:
                repeat_label = f"Repeat {repeat_config['count']}x"
            elif "while" in repeat_config:
                repeat_label = "Repeat while..."
            elif "until" in repeat_config:
                repeat_label = "Repeat until..."

            node = AutomationNode(
                id=repeat_id,
                label=repeat_label,
                type=COMP_TYPE_ACTION,
                data={"type": "repeat", "config": repeat_config},
                color=COLORS[COMP_TYPE_ACTION],
            )
            graph.nodes.append(node)
            action_ids.append(repeat_id)

            # Process repeat sequence
            sequence = repeat_config.get("sequence", [])
            if not isinstance(sequence, list):
                sequence = [sequence] if sequence else []

            prev_id = repeat_id
            for seq_idx, seq_action in enumerate(sequence):
                seq_ids = self._process_action_recursive(
                    seq_action, seq_idx, graph, parent_id=repeat_id
                )
                if seq_ids:
                    if prev_id == repeat_id:
                        graph.edges.append(
                            AutomationEdge(
                                from_node=prev_id, to_node=seq_ids[0], label="loop"
                            )
                        )
                    else:
                        graph.edges.append(
                            AutomationEdge(from_node=prev_id, to_node=seq_ids[0])
                        )
                    for i in range(len(seq_ids) - 1):
                        graph.edges.append(
                            AutomationEdge(from_node=seq_ids[i], to_node=seq_ids[i + 1])
                        )
                    prev_id = seq_ids[-1]

        # Handle regular actions
        else:
            action_id = self._generate_node_id("action")
            label = self._format_action_label(action, index)

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

    def _summarize_conditions(self, conditions: list[dict[str, Any]]) -> str:
        """Create a summary of conditions for display.

        Args:
            conditions: List of condition configurations

        Returns:
            str: Summary string
        """
        if not conditions:
            return "condition"

        if len(conditions) == 1:
            cond = conditions[0]
            cond_type = cond.get("condition", "unknown")

            if cond_type == "state":
                entity = cond.get("entity_id", "entity")
                state = cond.get("state", "")
                if state:
                    return f"{entity} = {state}"
                return entity

            elif cond_type == "numeric_state":
                entity = cond.get("entity_id", "entity")
                above = cond.get("above", "")
                below = cond.get("below", "")
                if above and below:
                    return f"{entity}: {below} < x < {above}"
                elif above:
                    return f"{entity} > {above}"
                elif below:
                    return f"{entity} < {below}"
                return f"{entity} numeric"

            elif cond_type == "template":
                template = cond.get("value_template", "")
                if template and len(template) < 40:
                    return f"template: {template}"
                return "template"

            elif cond_type == "time":
                after = cond.get("after", "")
                before = cond.get("before", "")
                if after and before:
                    return f"time: {after}-{before}"
                elif after:
                    return f"time after {after}"
                elif before:
                    return f"time before {before}"
                return "time condition"

            elif cond_type == "sun":
                after = cond.get("after", "")
                before = cond.get("before", "")
                if after and before:
                    return f"sun: {after}-{before}"
                elif after:
                    return f"sun after {after}"
                elif before:
                    return f"sun before {before}"
                return "sun condition"

            elif cond_type == "zone":
                entity = cond.get("entity_id", "entity")
                zone = cond.get("zone", "zone")
                return f"{entity} in {zone}"

            elif cond_type == "device":
                device_type = cond.get("type", "")
                if device_type:
                    return f"device: {device_type}"
                return "device condition"

            elif cond_type == "or":
                sub_conditions = cond.get("conditions", [])
                return f"any of {len(sub_conditions)}"

            elif cond_type == "and":
                sub_conditions = cond.get("conditions", [])
                return f"all of {len(sub_conditions)}"

            elif cond_type == "not":
                return "NOT condition"

            else:
                return cond_type

        else:
            # Multiple conditions - show first one + count
            first_cond = conditions[0]
            cond_type = first_cond.get("condition", "")
            if cond_type == "state":
                entity = first_cond.get("entity_id", "")
                if entity:
                    return f"{entity}... +{len(conditions)-1} more"
            elif cond_type == "numeric_state":
                entity = first_cond.get("entity_id", "")
                if entity:
                    return f"{entity}... +{len(conditions)-1} more"

            return f"{len(conditions)} conditions"

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
        platform = trigger.get("platform", "")

        # Handle state triggers
        if platform == "state":
            entity_id = trigger.get("entity_id", [])
            # Handle multiple entities
            if isinstance(entity_id, list):
                entity_str = (
                    ", ".join(entity_id)
                    if len(entity_id) <= 2
                    else f"{entity_id[0]} +{len(entity_id)-1}"
                )
            else:
                entity_str = str(entity_id)

            to_state = trigger.get("to", "")
            from_state = trigger.get("from", "")

            if to_state and from_state:
                return f"State: {entity_str}\n{from_state} → {to_state}"
            elif to_state:
                return f"State: {entity_str} → {to_state}"
            elif from_state:
                return f"State: {entity_str}\nfrom {from_state}"
            else:
                return f"State: {entity_str}"

        # Handle time triggers
        elif platform == "time":
            at_time = trigger.get("at", "")
            if at_time:
                if isinstance(at_time, list):
                    at_time = ", ".join(str(t) for t in at_time)
                return f"Time: {at_time}"
            return "Time trigger"

        # Handle sun triggers
        elif platform == "sun":
            event = trigger.get("event", "rise")
            offset = trigger.get("offset", "")
            if offset:
                return f"Sun: {event} {offset}"
            return f"Sun: {event}"

        # Handle numeric state triggers
        elif platform == "numeric_state":
            entity_id = trigger.get("entity_id", [])
            if isinstance(entity_id, list):
                entity_str = (
                    ", ".join(entity_id)
                    if len(entity_id) <= 2
                    else f"{entity_id[0]} +{len(entity_id)-1}"
                )
            else:
                entity_str = str(entity_id)

            above = trigger.get("above", "")
            below = trigger.get("below", "")

            if above and below:
                return f"Numeric: {entity_str}\n{below} < value < {above}"
            elif above:
                return f"Numeric: {entity_str} > {above}"
            elif below:
                return f"Numeric: {entity_str} < {below}"
            else:
                return f"Numeric: {entity_str}"

        # Handle template triggers
        elif platform == "template":
            value_template = trigger.get("value_template", "")
            if value_template and len(value_template) < 30:
                return f"Template:\n{value_template}"
            return "Template trigger"

        # Handle time pattern triggers
        elif platform == "time_pattern":
            hours = trigger.get("hours", "*")
            minutes = trigger.get("minutes", "*")
            seconds = trigger.get("seconds", "*")
            return f"Time pattern:\n{hours}:{minutes}:{seconds}"

        # Handle webhook triggers
        elif platform == "webhook":
            webhook_id = trigger.get("webhook_id", "")
            return f"Webhook: {webhook_id}" if webhook_id else "Webhook trigger"

        # Handle event triggers
        elif platform == "event":
            event_type = trigger.get("event_type", "")
            return f"Event: {event_type}" if event_type else "Event trigger"

        # Handle MQTT triggers
        elif platform == "mqtt":
            topic = trigger.get("topic", "")
            return f"MQTT: {topic}" if topic else "MQTT trigger"

        # Handle zone triggers
        elif platform == "zone":
            entity_id = trigger.get("entity_id", "")
            zone = trigger.get("zone", "")
            event = trigger.get("event", "enter")
            if entity_id and zone:
                return f"Zone: {entity_id}\n{event} {zone}"
            return "Zone trigger"

        # Handle geo_location triggers
        elif platform == "geo_location":
            source = trigger.get("source", "")
            return f"Geo: {source}" if source else "Geo location trigger"

        # Handle homeassistant triggers
        elif platform == "homeassistant":
            event = trigger.get("event", "start")
            return f"Home Assistant: {event}"

        # Handle device triggers
        elif platform == "device":
            device_id = trigger.get("device_id", "")
            domain = trigger.get("domain", "")
            trigger_type = trigger.get("type", "")
            if trigger_type:
                return f"Device: {trigger_type}"
            elif domain:
                return f"Device: {domain}"
            return "Device trigger"

        # Handle tag triggers
        elif platform == "tag":
            tag_id = trigger.get("tag_id", "")
            return f"Tag: {tag_id}" if tag_id else "Tag scanned"

        # Handle calendar triggers
        elif platform == "calendar":
            entity_id = trigger.get("entity_id", "")
            event = trigger.get("event", "start")
            return f"Calendar: {entity_id}\n{event}"

        # Fallback for unknown or unhandled platforms
        elif platform:
            return f"Trigger: {platform}"

        # Last resort - check for 'id' or other identifying fields
        trigger_id = trigger.get("id", "")
        if trigger_id:
            return f"Trigger: {trigger_id}"

        # If we still don't have anything meaningful, check if there's any data
        if trigger:
            # Try to get the first non-platform key as a hint
            keys = [k for k in trigger.keys() if k not in ["platform", "id"]]
            if keys:
                return f"Trigger: {keys[0]}"

        return f"Trigger #{index + 1}"

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

        # Service calls
        if "service" in action:
            service = action.get("service", "unknown")

            # Extract target and data information
            target_info = ""
            data_info = ""
            target = action.get("target", {})
            data = action.get("data", {})

            # Try to get entity_id from various places
            entity_id = None
            if isinstance(target, dict):
                entity_id = target.get("entity_id")
            elif "entity_id" in action:
                entity_id = action.get("entity_id")
            elif isinstance(data, dict) and "entity_id" in data:
                entity_id = data.get("entity_id")

            # Format entity_id for display
            if entity_id:
                if isinstance(entity_id, list):
                    if len(entity_id) == 1:
                        target_info = f"{entity_id[0]}"
                    elif len(entity_id) <= 3:
                        target_info = f"{', '.join(entity_id)}"
                    else:
                        target_info = f"{entity_id[0]} +{len(entity_id)-1} more"
                else:
                    target_info = f"{entity_id}"

            # Check for area or device targets
            elif isinstance(target, dict):
                if "area_id" in target:
                    area = target.get("area_id")
                    if isinstance(area, list):
                        target_info = f"Area: {', '.join(area)}"
                    else:
                        target_info = f"Area: {area}"
                elif "device_id" in target:
                    device = target.get("device_id")
                    if isinstance(device, list):
                        target_info = f"{len(device)} devices"
                    else:
                        target_info = f"Device: {device}"

            # Extract and format data parameters
            data_parts = []
            if isinstance(data, dict):
                # Light-specific parameters
                if "brightness" in data:
                    brightness = data["brightness"]
                    if isinstance(brightness, int):
                        pct = int((brightness / 255) * 100)
                        data_parts.append(f"Brightness: {pct}%")
                    else:
                        data_parts.append(f"Brightness: {brightness}")

                if "brightness_pct" in data:
                    data_parts.append(f"Brightness: {data['brightness_pct']}%")

                if "rgb_color" in data:
                    rgb = data["rgb_color"]
                    if isinstance(rgb, list) and len(rgb) == 3:
                        data_parts.append(f"RGB: ({rgb[0]},{rgb[1]},{rgb[2]})")
                    else:
                        data_parts.append(f"RGB: {rgb}")

                if "kelvin" in data:
                    data_parts.append(f"Color temp: {data['kelvin']}K")

                if "color_temp" in data:
                    data_parts.append(f"Color temp: {data['color_temp']}")

                if "color_name" in data:
                    data_parts.append(f"Color: {data['color_name']}")

                # Climate parameters
                if "temperature" in data:
                    data_parts.append(f"Temp: {data['temperature']}°")

                if "target_temp_high" in data and "target_temp_low" in data:
                    data_parts.append(
                        f"Range: {data['target_temp_low']}-{data['target_temp_high']}°"
                    )
                elif "target_temp_high" in data:
                    data_parts.append(f"Max: {data['target_temp_high']}°")
                elif "target_temp_low" in data:
                    data_parts.append(f"Min: {data['target_temp_low']}°")

                if "hvac_mode" in data:
                    data_parts.append(f"Mode: {data['hvac_mode']}")

                if "fan_mode" in data:
                    data_parts.append(f"Fan: {data['fan_mode']}")

                # Cover parameters
                if "position" in data:
                    data_parts.append(f"Position: {data['position']}%")

                if "tilt_position" in data:
                    data_parts.append(f"Tilt: {data['tilt_position']}%")

                # Media player parameters
                if "media_content_id" in data:
                    content = str(data["media_content_id"])
                    if len(content) > 30:
                        content = content[:30] + "..."
                    data_parts.append(f"Media: {content}")

                if "volume_level" in data:
                    vol = int(float(data["volume_level"]) * 100)
                    data_parts.append(f"Volume: {vol}%")

                # Notification parameters
                if "message" in data:
                    msg = str(data["message"])
                    if len(msg) > 40:
                        msg = msg[:40] + "..."
                    data_parts.append(f'Message: "{msg}"')

                if "title" in data:
                    title = str(data["title"])
                    if len(title) > 30:
                        title = title[:30] + "..."
                    data_parts.append(f'Title: "{title}"')

                # Input parameters
                if "value" in data and "message" not in data:
                    data_parts.append(f"Value: {data['value']}")

                if "option" in data:
                    data_parts.append(f"Option: {data['option']}")

                # Timer/duration parameters
                if "duration" in data and "delay" not in action:
                    data_parts.append(f"Duration: {data['duration']}")

                # Generic state
                if "state" in data:
                    data_parts.append(f"State: {data['state']}")

            # Build the full label
            label_parts = [service]
            if target_info:
                label_parts.append(target_info)
            if data_parts:
                # Limit to 3 most important data parameters
                data_info = "\n".join(data_parts[:3])
                if len(data_parts) > 3:
                    data_info += f"\n+{len(data_parts)-3} more params"

            if data_info:
                return f"{label_parts[0]}\n{label_parts[1] if len(label_parts) > 1 else ''}\n{data_info}".strip()
            elif len(label_parts) > 1:
                return f"{label_parts[0]}\n{label_parts[1]}"
            else:
                return label_parts[0]

        # Delay
        elif "delay" in action:
            delay_str = action.get("delay", "unknown")
            if isinstance(delay_str, dict):
                # Handle delay as dict (hours, minutes, seconds)
                hours = delay_str.get("hours", 0)
                minutes = delay_str.get("minutes", 0)
                seconds = delay_str.get("seconds", 0)
                parts = []
                if hours:
                    parts.append(f"{hours}h")
                if minutes:
                    parts.append(f"{minutes}m")
                if seconds:
                    parts.append(f"{seconds}s")
                delay_str = " ".join(parts) if parts else "0s"
            return f"Delay: {delay_str}"

        # Wait for template
        elif "wait_template" in action:
            template = action.get("wait_template", "")
            timeout = action.get("timeout", "")
            if timeout:
                return f"Wait (timeout: {timeout})"
            return "Wait for template"

        # Wait for trigger
        elif "wait_for_trigger" in action:
            timeout = action.get("timeout", "")
            if timeout:
                return f"Wait for trigger\n(timeout: {timeout})"
            return "Wait for trigger"

        # Event
        elif "event" in action:
            event_name = action.get("event", "unknown")
            return f"Fire event: {event_name}"

        # Scene
        elif "scene" in action:
            scene = action.get("scene", "unknown")
            return f"Scene: {scene}"

        # Device action
        elif "device_id" in action:
            device_type = action.get("type", "")
            domain = action.get("domain", "")
            if device_type:
                return f"Device: {device_type}"
            elif domain:
                return f"Device: {domain}"
            return "Device action"

        # Stop action
        elif "stop" in action:
            stop_msg = action.get("stop", "")
            if stop_msg:
                return f"Stop: {stop_msg}"
            return "Stop"

        # Variables
        elif "variables" in action:
            var_dict = action.get("variables", {})
            if isinstance(var_dict, dict):
                var_names = list(var_dict.keys())
                if len(var_names) == 1:
                    return f"Set variable: {var_names[0]}"
                elif len(var_names) <= 3:
                    return f"Set variables:\n{', '.join(var_names)}"
                else:
                    return f"Set {len(var_names)} variables"
            return "Set variables"

        # These shouldn't appear here as they're handled in _process_action_recursive
        # but keep them as fallback
        elif "choose" in action:
            return "Choose/If-Then"
        elif "parallel" in action:
            return "Parallel actions"
        elif "repeat" in action:
            return "Repeat loop"
        elif "if" in action:
            return "If condition"

        # Unknown action - try to find any identifying info
        else:
            # Check for any keys that might give us a hint
            action_keys = [
                k
                for k in action.keys()
                if k not in ["alias", "enabled", "continue_on_error"]
            ]
            if action_keys:
                return f"Action: {action_keys[0]}"
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
