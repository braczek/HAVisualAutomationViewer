#!/bin/bash
set -e

echo "🔍 Running quality checks..."

echo "📏 Formatting check (Black)..."
black --check custom_components/visualautoview tests

echo "📦 Import check (isort)..."
isort --check-only custom_components/visualautoview tests

echo "🐍 Linting (Flake8)..."
flake8 custom_components/visualautoview tests

echo "🔤 Type checking (mypy)..."
mypy custom_components/visualautoview --ignore-missing-imports

echo "✅ All quality checks passed!"
