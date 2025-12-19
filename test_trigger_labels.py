"""Test script for trigger label formatting."""

import sys
sys.path.insert(0, "custom_components/visualautoview")

from graph_parser import AutomationGraphParser

# Sample automation with various trigger types
test_automation = {
    "alias": "Test Trigger Labels",
    "id": "test_triggers",
    "triggers": [
        {
            "platform": "state",
            "entity_id": "sensor.temperature",
            "from": "cool",
            "to": "hot"
        },
        {
            "platform": "time",
            "at": "08:00:00"
        },
        {
            "platform": "numeric_state",
            "entity_id": "sensor.humidity",
            "above": 70,
            "below": 90
        },
        {
            "platform": "sun",
            "event": "sunset",
            "offset": "-00:30:00"
        },
        {
            "platform": "time_pattern",
            "hours": "*",
            "minutes": "/5"
        },
        {
            "platform": "webhook",
            "webhook_id": "my_webhook"
        },
        {
            "platform": "mqtt",
            "topic": "home/sensors/door"
        },
        {
            "platform": "event",
            "event_type": "automation_triggered"
        },
        {
            "platform": "homeassistant",
            "event": "start"
        },
        {
            "platform": "tag",
            "tag_id": "my_nfc_tag"
        },
        {
            "platform": "device",
            "type": "turned_on"
        }
    ],
    "actions": [
        {
            "service": "light.turn_on",
            "target": {"entity_id": "light.living_room"}
        }
    ]
}

print("Testing trigger label formatting...")
parser = AutomationGraphParser()
graph = parser.parse_automation(test_automation)

print(f"\n=== Trigger Labels ===")
for node in graph.nodes:
    if node.type == "trigger":
        print(f"✓ {node.label}")

print("\n✅ Test completed successfully!")
print(f"Total triggers parsed: {len([n for n in graph.nodes if n.type == 'trigger'])}")
