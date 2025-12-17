#!/bin/bash
set -e

echo "🔄 Running full development checks..."

# Backend checks
echo "Backend checks..."
./scripts/quality-check.sh

# Backend tests
echo ""
echo "Backend tests..."
./scripts/run-tests.sh

# Frontend checks
echo ""
echo "Frontend checks..."
cd frontend
npm run type-check
npm run lint
npm run build
cd ..

echo ""
echo "✅ All checks passed! Ready to commit."
