#!/bin/bash
set -e

echo "🛠️  Setting up Visual AutoView development environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || {
    echo "❌ Python 3 is required but not installed."
    exit 1
}

command -v node >/dev/null 2>&1 || {
    echo "❌ Node.js is required but not installed."
    exit 1
}

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm ci
npm run build
cd ..

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pip install pre-commit
pre-commit install

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Create feature branch: git checkout -b feature/your-feature"
echo "3. Make changes and test"
echo "4. Run tests: pytest"
echo "5. Commit and push: git push origin feature/your-feature"
