"""Constants for Visual AutoView integration."""

DOMAIN = "visualautoview"

# Component types
COMP_TYPE_TRIGGER = "trigger"
COMP_TYPE_CONDITION = "condition"
COMP_TYPE_ACTION = "action"
COMP_TYPE_METADATA = "metadata"

# Color scheme for nodes
COLORS = {
    COMP_TYPE_TRIGGER: "#4CAF50",  # Green
    COMP_TYPE_CONDITION: "#FFC107",  # Amber
    COMP_TYPE_ACTION: "#2196F3",  # Blue
    COMP_TYPE_METADATA: "#9E9E9E",  # Grey
}

# Default values
DEFAULT_NODE_ID_PREFIX = "node_"
DEFAULT_EDGE_LABEL = None
