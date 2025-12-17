#!/bin/bash
set -e

echo "🧪 Running tests..."

pytest \
    --cov=custom_components/visualautoview \
    --cov-report=term-missing:skip-covered \
    --cov-report=html \
    --junitxml=test-results.xml \
    --verbose

echo "✅ Tests passed!"
echo "📊 Coverage report: htmlcov/index.html"
