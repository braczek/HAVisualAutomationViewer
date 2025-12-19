"""Test enhanced action and condition labels."""

import sys
sys.path.insert(0, "custom_components/visualautoview")

from graph_parser import AutomationGraphParser

# Sample automation with detailed actions and conditions
test_automation = {
    "alias": "Test Enhanced Labels",
    "id": "test_labels",
    "triggers": [
        {
            "platform": "state",
            "entity_id": "binary_sensor.motion",
            "to": "on"
        }
    ],
    "actions": [
        {
            "service": "light.turn_on",
            "target": {
                "entity_id": "light.living_room"
            },
            "data": {
                "brightness": 255,
                "rgb_color": [255, 0, 0]
            }
        },
        {
            "service": "notify.mobile_app",
            "data": {
                "message": "Motion detected in living room!"
            }
        },
        {
            "if": [
                {
                    "condition": "numeric_state",
                    "entity_id": "sensor.temperature",
                    "above": 20,
                    "below": 25
                }
            ],
            "then": [
                {
                    "service": "climate.set_temperature",
                    "target": {
                        "entity_id": ["climate.bedroom", "climate.living_room"]
                    },
                    "data": {
                        "temperature": 22
                    }
                }
            ],
            "else": [
                {
                    "service": "switch.turn_off",
                    "target": {
                        "entity_id": ["switch.heater_1", "switch.heater_2", "switch.heater_3", "switch.heater_4"]
                    }
                }
            ]
        },
        {
            "choose": [
                {
                    "conditions": [
                        {
                            "condition": "state",
                            "entity_id": "sun.sun",
                            "state": "below_horizon"
                        },
                        {
                            "condition": "time",
                            "after": "18:00:00",
                            "before": "23:00:00"
                        }
                    ],
                    "sequence": [
                        {
                            "service": "light.turn_on",
                            "target": {
                                "area_id": "living_room"
                            }
                        }
                    ]
                }
            ],
            "default": [
                {
                    "service": "light.turn_off",
                    "target": {
                        "area_id": ["bedroom", "kitchen"]
                    }
                }
            ]
        },
        {
            "delay": {
                "hours": 1,
                "minutes": 30
            }
        },
        {
            "event": "custom_event",
            "event_data": {
                "source": "automation"
            }
        },
        {
            "variables": {
                "my_var": "test_value",
                "another_var": 123
            }
        }
    ]
}

print("Testing enhanced action and condition labels...")
parser = AutomationGraphParser()
graph = parser.parse_automation(test_automation)

print(f"\n=== Enhanced Labels ===")
print("\n--- Actions ---")
for node in graph.nodes:
    if node.type == "action":
        print(f"✓ {node.label}")

print("\n--- Conditions ---")
for node in graph.nodes:
    if node.type == "condition":
        print(f"✓ {node.label}")

print("\n--- Triggers ---")
for node in graph.nodes:
    if node.type == "trigger":
        print(f"✓ {node.label}")

print(f"\n✅ Test completed!")
print(f"Total nodes: {len(graph.nodes)}")
print(f"Total edges: {len(graph.edges)}")
