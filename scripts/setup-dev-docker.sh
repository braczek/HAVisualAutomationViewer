#!/bin/bash
set -e

echo "🔨 Setting up Visual AutoView development environment..."

# Create directories
mkdir -p dev/ha-config/{custom_components,www}
mkdir -p dev/ha-config/blueprints/automation

# Create Home Assistant configuration
cat > dev/ha-config/configuration.yaml << 'EOF'
homeassistant:
  name: Visual AutoView Dev
  latitude: 0
  longitude: 0
  elevation: 0
  unit_system: metric
  time_zone: UTC

logger:
  default: debug
  logs:
    custom_components.visualautoview: debug

http:
  cors_allowed_origins:
    - http://localhost:5173
    - http://localhost:3000

automation: !include automations.yaml
script: !include scripts.yaml
EOF

# Create empty automation files
cat > dev/ha-config/automations.yaml << 'EOF'
[]
EOF

cat > dev/ha-config/scripts.yaml << 'EOF'
EOF

echo "✓ Configuration created"
echo "🐳 Starting Docker containers..."

docker-compose -f docker-compose.dev.yml up -d

echo "✓ Development environment ready!"
echo ""
echo "Home Assistant: http://localhost:8123"
echo "Frontend Dev: http://localhost:5173"
echo "API Base URL: http://localhost:8123/api"
