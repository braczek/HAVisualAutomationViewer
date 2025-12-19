"""Test enhanced action details."""

import sys
sys.path.insert(0, "custom_components/visualautoview")

from graph_parser import AutomationGraphParser

# Sample automation with detailed service calls
test_automation = {
    "alias": "Test Detailed Actions",
    "id": "test_details",
    "triggers": [
        {
            "platform": "state",
            "entity_id": "binary_sensor.motion",
            "to": "on"
        }
    ],
    "actions": [
        # Light with brightness and color
        {
            "service": "light.turn_on",
            "target": {
                "entity_id": "light.living_room"
            },
            "data": {
                "brightness": 200,
                "rgb_color": [255, 128, 0],
                "transition": 2
            }
        },
        # Climate with temperature
        {
            "service": "climate.set_temperature",
            "target": {
                "entity_id": "climate.bedroom"
            },
            "data": {
                "temperature": 22,
                "hvac_mode": "heat"
            }
        },
        # Notification with title and message
        {
            "service": "notify.mobile_app",
            "data": {
                "title": "Motion Alert",
                "message": "Motion detected in the living room at the front door area"
            }
        },
        # Cover with position
        {
            "service": "cover.set_cover_position",
            "target": {
                "entity_id": ["cover.bedroom_blinds", "cover.living_room_blinds"]
            },
            "data": {
                "position": 75
            }
        },
        # Media player
        {
            "service": "media_player.play_media",
            "target": {
                "entity_id": "media_player.spotify"
            },
            "data": {
                "media_content_id": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
                "media_content_type": "playlist",
                "volume_level": 0.5
            }
        },
        # Input number
        {
            "service": "input_number.set_value",
            "target": {
                "entity_id": "input_number.temperature_setpoint"
            },
            "data": {
                "value": 21.5
            }
        },
        # Light with brightness percentage
        {
            "service": "light.turn_on",
            "target": {
                "entity_id": "light.kitchen"
            },
            "data": {
                "brightness_pct": 80,
                "kelvin": 3000,
                "transition": 1
            }
        },
        # Simple service with no data
        {
            "service": "switch.turn_off",
            "target": {
                "entity_id": "switch.fan"
            }
        }
    ]
}

print("Testing enhanced action details...\n")
parser = AutomationGraphParser()
graph = parser.parse_automation(test_automation)

print("=== Action Details ===\n")
for node in graph.nodes:
    if node.type == "action":
        print(f"✓ {node.label}")
        print("  " + "-" * 50)

print(f"\n✅ Test completed!")
print(f"Total nodes: {len(graph.nodes)}")
