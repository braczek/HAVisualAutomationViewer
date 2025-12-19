"""Test script for nested action parsing."""

import sys
sys.path.insert(0, "custom_components/visualautoview")

from graph_parser import AutomationGraphParser

# Sample automation with nested choose structure
test_automation = {
    "alias": "Test Nested Actions",
    "id": "test_nested",
    "triggers": [
        {
            "platform": "state",
            "entity_id": "sensor.temperature",
            "to": "hot"
        }
    ],
    "actions": [
        {
            "choose": [
                {
                    "conditions": [
                        {
                            "condition": "state",
                            "entity_id": "light.living_room",
                            "state": "on"
                        }
                    ],
                    "sequence": [
                        {
                            "service": "light.turn_off",
                            "target": {"entity_id": "light.living_room"}
                        },
                        {
                            "delay": "00:00:05"
                        }
                    ]
                },
                {
                    "conditions": [
                        {
                            "condition": "state",
                            "entity_id": "switch.fan",
                            "state": "on"
                        }
                    ],
                    "sequence": [
                        {
                            "service": "switch.turn_off",
                            "target": {"entity_id": "switch.fan"}
                        }
                    ]
                }
            ],
            "default": [
                {
                    "service": "notify.mobile_app",
                    "data": {"message": "No conditions matched"}
                }
            ]
        },
        {
            "if": [
                {
                    "condition": "numeric_state",
                    "entity_id": "sensor.humidity",
                    "above": 70
                }
            ],
            "then": [
                {
                    "service": "fan.turn_on",
                    "target": {"entity_id": "fan.bedroom"}
                }
            ],
            "else": [
                {
                    "service": "fan.turn_off",
                    "target": {"entity_id": "fan.bedroom"}
                }
            ]
        }
    ]
}

print("Testing nested action parsing...")
parser = AutomationGraphParser()
graph = parser.parse_automation(test_automation)

print(f"\n=== Graph Statistics ===")
print(f"Total nodes: {len(graph.nodes)}")
print(f"Total edges: {len(graph.edges)}")

print(f"\n=== Nodes ===")
for node in graph.nodes:
    print(f"- {node.id}: [{node.type}] {node.label}")

print(f"\n=== Edges ===")
for edge in graph.edges:
    label_str = f" ({edge.label})" if edge.label else ""
    print(f"- {edge.from_node} -> {edge.to_node}{label_str}")

print("\n✅ Test completed successfully!")
