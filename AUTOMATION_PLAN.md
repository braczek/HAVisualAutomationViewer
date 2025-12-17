# Visual AutoView - Automation Plan

## 1. GitHub Publishing

### 1.1 Repository Setup

#### Initial Repository Creation
1. Create new GitHub repository `visualautoview` under your account
2. Set repository visibility to **Public** for community access
3. Configure repository settings:
   - **Branch protection**: Require pull requests for main/release branches
   - **Require status checks**: Enable before merge
   - **Require reviews**: Minimum 1 review for production branches
   - **Automatically delete head branches**: Enable after PR merge

#### Repository Structure
```
visualautoview/
├── .github/
│   ├── workflows/               # CI/CD automation
│   │   ├── tests.yml
│   │   ├── lint.yml
│   │   ├── build.yml
│   │   └── release.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── custom_components/visualautoview/  # Home Assistant integration
├── frontend/                    # Web frontend
├── tests/                       # Test suite
├── docs/                        # Documentation
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── 
├── CHANGELOG.md
├── CONTRIBUTING.md
└── AUTOMATION_PLAN.md
```

#### .gitignore Configuration
Create `.gitignore` in project root:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
ENV/
env/

# Frontend
node_modules/
dist/
.env
.env.local
*.tsbuildinfo

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# CI/CD
.github/workflows/logs/
```

### 1.2 Branch Strategy

#### Branching Model
- **main**: Production-ready code, protected branch
- **develop**: Integration branch for features, staging tests
- **feature/**: Feature branches (feature/graph-optimization)
- **bugfix/**: Bug fix branches (bugfix/parser-issue)
- **release/**: Release preparation (release/v1.0.0)
- **hotfix/**: Emergency production fixes (hotfix/critical-bug)

#### Branch Naming Convention
```
feature/<feature-name>      # New features
bugfix/<bug-description>    # Bug fixes
docs/<doc-topic>           # Documentation
chore/<task-description>   # Maintenance tasks
```

#### Branch Merge Requirements
```yaml
- All CI checks must pass
- Code review approval required
- All conversations must be resolved
- Branch must be up to date with base branch
```

### 1.3 Commit and PR Strategy

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, perf, test, chore

Example:
```
feat(graph-parser): add circular dependency detection

- Implements cycle detection algorithm
- Validates automation chains for loops
- Reports circular dependencies in API response

Fixes #123
```

#### Pull Request Template
File: `.github/PULL_REQUEST_TEMPLATE.md`
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests passed
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] CHANGELOG.md updated
```

---

## 2. CI/CD Automation

### 2.1 GitHub Actions Setup

#### Testing Workflow
File: `.github/workflows/tests.yml`
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests with coverage
      run: |
        pytest --cov=custom_components/visualautoview \
                --cov-report=xml \
                --cov-report=html \
                --junitxml=test-results.xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.python-version }}
        path: test-results.xml

  frontend-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Type check
      run: cd frontend && npm run type-check
    
    - name: Lint
      run: cd frontend && npm run lint
```

#### Linting Workflow
File: `.github/workflows/lint.yml`
```yaml
name: Lint & Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run Black formatter check
      run: black --check custom_components/visualautoview tests
    
    - name: Run isort import check
      run: isort --check-only custom_components/visualautoview tests
    
    - name: Run Flake8
      run: flake8 custom_components/visualautoview tests
    
    - name: Run mypy type checker
      run: mypy custom_components/visualautoview --ignore-missing-imports
    
    - name: YAML validation
      run: |
        python -c "
        import yaml
        import glob
        for yaml_file in glob.glob('custom_components/visualautoview/**/*.yaml', recursive=True):
            with open(yaml_file) as f:
                yaml.safe_load(f)
        print('All YAML files valid')
        "
```

#### Build Workflow
File: `.github/workflows/build.yml`
```yaml
name: Build

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-backend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Validate integration structure
      run: |
        python -c "
        import json
        import os
        manifest_path = 'custom_components/visualautoview/manifest.json'
        with open(manifest_path) as f:
            manifest = json.load(f)
        required_fields = ['domain', 'name', 'version', 'documentation']
        for field in required_fields:
            assert field in manifest, f'Missing {field} in manifest'
        print(f'✓ Integration manifest valid (v{manifest[\"version\"]})')
        "
    
    - name: Create backend artifact
      run: |
        mkdir -p artifacts
        cd custom_components && zip -r ../artifacts/visualautoview-backend-${{ github.sha }}.zip visualautoview -x "*/.*" && cd ..
    
    - name: Upload backend artifact
      uses: actions/upload-artifact@v3
      with:
        name: backend-artifacts
        path: artifacts/

  build-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build
    
    - name: Create frontend artifact
      run: |
        mkdir -p artifacts
        cd frontend/dist && zip -r ../../artifacts/visualautoview-frontend-${{ github.sha }}.zip . && cd ../..
    
    - name: Upload frontend artifact
      uses: actions/upload-artifact@v3
      with:
        name: frontend-artifacts
        path: artifacts/
```

#### Release Workflow
File: `.github/workflows/release.yml`
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Build artifacts
      run: |
        mkdir -p release
        cp -r custom_components/visualautoview release/
        
        cd frontend
        npm ci
        npm run build
        mkdir -p ../release/visualautoview/frontend_dist
        cp -r dist/* ../release/visualautoview/frontend_dist/
        cd ..
    
    - name: Generate changelog
      id: changelog
      run: |
        VERSION=${GITHUB_REF#refs/tags/v}
        echo "version=$VERSION" >> $GITHUB_OUTPUT
        git log --oneline --no-decorate $(git describe --tags --abbrev=0 HEAD^)..HEAD > changelog.txt || echo "Initial release" > changelog.txt
    
    - name: Create release archive
      run: |
        VERSION=${{ steps.changelog.outputs.version }}
        cd release && zip -r ../visualautoview-$VERSION.zip visualautoview && cd ..
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: visualautoview-${{ steps.changelog.outputs.version }}.zip
        body_path: changelog.txt
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Update HACS validation
      run: |
        echo "Release ${{ steps.changelog.outputs.version }} ready for HACS"
```

### 2.2 CI/CD Configuration

#### GitHub Actions Configuration
- **Python versions tested**: 3.10, 3.11, 3.12
- **Node version**: 18+
- **Home Assistant minimum version**: 2023.11.0
- **Run on**: Every push to main/develop, all PRs

#### Protected Branch Rules
```yaml
main:
  required_status_checks:
    - tests (3.10)
    - tests (3.11)
    - tests (3.12)
    - frontend-test
    - lint
    - build-backend
    - build-frontend
  required_approving_reviews: 1
  require_code_owner_reviews: true
  dismiss_stale_reviews: false
  require_branches_to_be_up_to_date: true

develop:
  required_status_checks:
    - tests (3.11)
    - frontend-test
    - lint
  required_approving_reviews: 0
  require_branches_to_be_up_to_date: true
```

---

## 3. Deployment Automation

### 3.1 Docker-Based Development

#### Development Docker Setup
File: `docker-compose.dev.yml`
```yaml
version: '3.8'

services:
  home-assistant:
    image: homeassistant/home-assistant:latest
    container_name: ha-dev
    ports:
      - "8123:8123"
    environment:
      TZ: UTC
    volumes:
      - ./dev/ha-config:/config
      - ./custom_components/visualautoview:/config/custom_components/visualautoview:ro
      - ./frontend/dist:/config/www/visualautoview:ro
    restart: unless-stopped

  api-tester:
    image: node:18-alpine
    container_name: api-tester
    working_dir: /app
    volumes:
      - ./:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    command: sh -c "cd frontend && npm install && npm run dev"
    environment:
      VITE_API_URL: http://home-assistant:8123/api
```

#### Development Setup Script
File: `scripts/setup-dev-docker.sh`
```bash
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
```

### 3.2 Local Test Deployment Scripts

#### Quick Test Script
File: `scripts/test-extension.sh`
```bash
#!/bin/bash
set -e

EXTENSION_PATH="$HOME/.homeassistant/custom_components/visualautoview"

echo "📦 Installing Visual AutoView extension..."

# Backup existing extension
if [ -d "$EXTENSION_PATH" ]; then
    echo "⚠️  Backing up existing extension..."
    mv "$EXTENSION_PATH" "${EXTENSION_PATH}.backup.$(date +%s)"
fi

# Copy extension
mkdir -p "$(dirname "$EXTENSION_PATH")"
cp -r custom_components/visualautoview "$EXTENSION_PATH"

echo "✓ Extension installed"
echo "🔄 Restarting Home Assistant..."

# Restart Home Assistant (adjust command based on your setup)
curl -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/services/homeassistant/restart \
  2>/dev/null || echo "⚠️  Auto-restart failed. Please restart manually."

echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Visit http://localhost:8123"
echo "2. Go to Settings → Devices & Services → Integrations"
echo "3. Search for 'Visual AutoView'"
echo "4. Click 'Create Integration' and set up endpoints"
```

#### Frontend Build and Deploy
File: `scripts/build-and-deploy.sh`
```bash
#!/bin/bash
set -e

FRONTEND_BUILD_DIR="frontend/dist"
HA_WWW_DIR="$HOME/.homeassistant/www/visualautoview"

echo "🏗️  Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✓ Build complete"
echo "📁 Deploying frontend files..."

mkdir -p "$HA_WWW_DIR"
rm -rf "$HA_WWW_DIR"/*
cp -r "$FRONTEND_BUILD_DIR"/* "$HA_WWW_DIR/"

echo "✓ Frontend deployed"
echo "📍 Access at: http://localhost:8123/static/visualautoview/"

# Update manifest version
TIMESTAMP=$(date +%s)
cat custom_components/visualautoview/manifest.json | \
  jq ".version = \"dev-$TIMESTAMP\"" > temp.json && \
  mv temp.json custom_components/visualautoview/manifest.json

echo "✓ Manifest updated"
```

### 3.3 Automated Testing Environment

#### Integration Test Script
File: `scripts/run-integration-tests.sh`
```bash
#!/bin/bash
set -e

echo "🧪 Running integration tests..."

# Check if Docker is running
docker ps > /dev/null 2>&1 || {
    echo "❌ Docker is not running"
    exit 1
}

# Start test environment
docker-compose -f docker-compose.dev.yml up -d

# Wait for Home Assistant to be ready
echo "⏳ Waiting for Home Assistant..."
for i in {1..30}; do
    if curl -s http://localhost:8123/api/ > /dev/null 2>&1; then
        echo "✓ Home Assistant is ready"
        break
    fi
    sleep 2
done

# Run backend tests
echo "🧪 Running backend tests..."
python -m pytest tests/ \
    --cov=custom_components/visualautoview \
    --cov-report=html \
    --cov-report=term

# Run frontend tests
echo "🧪 Running frontend tests..."
cd frontend
npm test

echo "✓ All integration tests passed"
echo "📊 Coverage report: htmlcov/index.html"
```

---

## 4. Testing Automation

### 4.1 Pytest Configuration

#### pytest.ini Enhancement
```ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
addopts = -v --strict-markers --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    requires_ha: Tests requiring Home Assistant
minversion = 7.0
```

#### Conftest Setup
File: `conftest.py`
```python
import pytest
import yaml
from pathlib import Path

@pytest.fixture
def sample_automation():
    """Load sample automation YAML for testing."""
    yaml_path = Path(__file__).parent / "tests" / "fixtures" / "sample_automation.yaml"
    with open(yaml_path) as f:
        return yaml.safe_load(f)

@pytest.fixture
def api_client():
    """Provide mock API client."""
    from unittest.mock import MagicMock
    return MagicMock()

@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide temporary configuration directory."""
    config_dir = tmp_path / "ha-config"
    config_dir.mkdir()
    (config_dir / "automations.yaml").write_text("[]")
    return config_dir

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
```

### 4.2 Test Structure

#### Backend Test Layout
```
tests/
├── __init__.py
├── conftest.py
├── fixtures/
│   ├── sample_automation.yaml
│   ├── complex_graph.yaml
│   └── edge_cases.yaml
├── unit/
│   ├── test_graph_parser.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_validators.py
├── integration/
│   ├── test_phase1_api.py
│   ├── test_phase2_api.py
│   ├── test_phase3_api.py
│   └── test_api_endpoints.py
└── performance/
    ├── test_parser_performance.py
    └── test_api_response_times.py
```

#### Test Execution Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components/visualautoview --cov-report=html

# Run specific test file
pytest tests/unit/test_graph_parser.py

# Run only integration tests
pytest -m integration

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Run with detailed output
pytest -vv --tb=long

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Generate JUnit XML for CI
pytest --junitxml=test-results.xml
```

### 4.3 Code Quality Checks

#### Pre-Commit Hook Configuration
File: `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: ["--profile=black"]

  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ["--max-line-length=100"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        args: ["--ignore-missing-imports"]
```

#### Install Pre-Commit Hooks
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Run manually on all files
```

### 4.4 Coverage Reporting

#### Coverage Configuration
File: `.coveragerc`
```ini
[run]
branch = True
source = custom_components/visualautoview
omit =
    */tests/*
    */__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:

precision = 2
skip_covered = False

[html]
directory = htmlcov
```

#### Coverage Targets
```yaml
overall: 80%
critical_modules:
  graph_parser: 90%
  api_base: 85%
  services: 80%
```

---

## 5. Distribution Methods

### 5.1 HACS Integration

#### HACS Configuration
Update `manifest.json`:
```json
{
    "domain": "visualautoview",
    "name": "Visual AutoView - Automation Graph Visualization",
    "version": "1.0.0",
    "documentation": "https://github.com/yourusername/visualautoview",
    "issue_tracker": "https://github.com/yourusername/visualautoview/issues",
    "requirements": [],
    "codeowners": ["@yourusername"],
    "iot_class": "calculated",
    "config_flow": false,
    "integration_type": "system",
    "homeassistant": "2023.11.0"
}
```

#### HACS Validation Workflow
File: `.github/workflows/hacs-validation.yml`
```yaml
name: HACS Validation

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: HACS Validation
        uses: hacs/action@22.5.0
        with:
          category: integration
          ignore: missing-readme,missing-version
```

#### HACS Submission Checklist
- [ ] Repository is public
- [ ] Manifest has valid domain name
- [ ] README.md includes all required fields
- [ ] README.md contains proper documentation
- [ ] No external dependencies (or clearly documented)
- [ ] Code follows Home Assistant coding standards
- [ ] Version number follows semantic versioning
- [ ] CHANGELOG.md documents all releases

#### HACS Installation Instructions
```markdown
### Installation via HACS

1. In Home Assistant, go to **Settings** → **Devices & Services** → **HACS**
2. Click **+ Explore & Download Repositories**
3. Search for "Visual AutoView"
4. Click the integration and select **Download**
5. Restart Home Assistant
6. Go to **Settings** → **Devices & Services** → **Create Integration**
7. Search for "Visual AutoView" and configure
```

### 5.2 GitHub Releases

#### Release Process Automation
File: `scripts/create-release.sh`
```bash
#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    echo "Usage: ./create-release.sh <version>"
    echo "Example: ./create-release.sh 1.0.0"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🚀 Creating release $VERSION..."

# Update version in manifest
jq ".version = \"$VERSION\"" \
    custom_components/visualautoview/manifest.json > temp.json && \
    mv temp.json custom_components/visualautoview/manifest.json

# Update frontend version
jq ".version = \"$VERSION\"" \
    frontend/package.json > temp.json && \
    mv temp.json frontend/package.json

# Commit version bump
git add custom_components/visualautoview/manifest.json frontend/package.json
git commit -m "chore: bump version to $VERSION"

# Create tag
git tag -a "$TAG" -m "Release $VERSION"

echo "✓ Release prepared"
echo ""
echo "Next steps:"
echo "1. Review changes: git log --oneline -5"
echo "2. Push to repository: git push origin main --tags"
echo "3. GitHub Actions will automatically create a release"
```

#### GitHub Release Assets
```yaml
assets:
  - visualautoview-<version>.zip
    - custom_components/visualautoview/
    - frontend/dist/
  - CHANGELOG.md
  - Installation instructions
```

### 5.3 Direct Distribution

#### Installation via Raw GitHub
```bash
# Method 1: Direct download
wget https://github.com/yourusername/visualautoview/releases/download/v1.0.0/visualautoview-1.0.0.zip
unzip visualautoview-1.0.0.zip -d ~/.homeassistant/custom_components/

# Method 2: Clone repository
git clone https://github.com/yourusername/visualautoview.git
cp -r visualautoview/custom_components/visualautoview ~/.homeassistant/custom_components/
```

#### Docker Installation Template
```dockerfile
FROM homeassistant/home-assistant:latest

# Copy Visual AutoView extension
COPY custom_components/visualautoview /config/custom_components/visualautoview/

# Copy frontend
COPY frontend/dist /config/www/visualautoview/
```

### 5.4 Distribution Communication

#### Release Announcement Template
```markdown
## Visual AutoView v1.0.0 Released 🎉

### Features
- [x] Feature 1
- [x] Feature 2
- [x] Bug fixes

### Installation
- **HACS**: Search for "Visual AutoView" in HACS
- **Manual**: Download from [GitHub Releases](...)
- **Docker**: See documentation

### Documentation
- [Quick Start Guide](QUICK_START.md)
- [API Documentation](API_IMPLEMENTATION_COMPLETE.md)
- [Contributing Guidelines](CONTRIBUTING.md)

### Support
- Report issues: [GitHub Issues](...)
- Discussions: [GitHub Discussions](...)
```

---

## 6. Local Development Setup

### 6.1 Developer Environment Setup

#### Initial Setup Script
File: `scripts/setup-dev-env.sh`
```bash
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
```

#### Development Environment Requirements
File: `requirements-dev.txt`
```
# Testing
pytest>=9.0.0
pytest-cov>=4.0.0
pytest-xdist>=3.0.0
pytest-mock>=3.0.0

# Code Quality
black>=23.0.0
flake8>=6.0.0
isort>=5.13.0
mypy>=1.0.0
pylint>=3.0.0

# YAML Support
PyYAML>=6.0

# Pre-commit
pre-commit>=3.0.0

# Development utilities
ipython>=8.0.0
ipdb>=0.13.0
```

### 6.2 Pre-Commit Hooks Automation

#### Setup Pre-Commit
```bash
# Install
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

#### Pre-Commit Workflow
```yaml
hooks:
  - Code formatting (Black)
  - Import sorting (isort)
  - Linting (Flake8)
  - Type checking (mypy)
  - YAML validation
  - JSON validation
  - Trailing whitespace removal
```

### 6.3 Local Testing Commands

#### Quick Test Suite
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=custom_components/visualautoview --cov-report=term-missing

# Run specific test
pytest tests/unit/test_graph_parser.py::TestGraphParser::test_parse

# Run in watch mode (requires pytest-watch)
ptw

# Run and show output
pytest -s tests/

# Profile test execution
pytest --durations=10
```

#### Code Quality Checks
```bash
# Format code
black custom_components/visualautoview tests

# Sort imports
isort custom_components/visualautoview tests

# Lint Python
flake8 custom_components/visualautoview tests

# Type checking
mypy custom_components/visualautoview --ignore-missing-imports

# All checks at once
./scripts/quality-check.sh
```

#### Frontend Development
```bash
# Development server
cd frontend
npm run dev

# Build for production
npm run build

# Type check
npm run type-check

# Lint
npm run lint

# Preview production build
npm run preview
```

### 6.4 Development Scripts

#### Quality Check Script
File: `scripts/quality-check.sh`
```bash
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
```

#### Test and Coverage Script
File: `scripts/run-tests.sh`
```bash
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
```

#### Full Development Check
File: `scripts/dev-check.sh`
```bash
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
```

#### Full Development Check
File: `scripts/dev-check.sh`
```bash
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
```

### 6.5 Git Workflow Automation

#### Feature Branch Workflow
```bash
# Create and switch to feature branch
git checkout -b feature/graph-optimization

# Make changes, commit frequently
git commit -m "feat(graph): optimize parsing algorithm"

# Push to remote
git push -u origin feature/graph-optimization

# Create pull request on GitHub

# After approval, merge to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/graph-optimization
git push origin develop

# Delete feature branch
git branch -d feature/graph-optimization
git push origin --delete feature/graph-optimization
```

#### Convenient Git Alias Setup
```bash
# Add to .git/config or ~/.gitconfig
[alias]
    feature = checkout -b
    review = log --oneline -10
    stats = shortlog -sn
    ready = !git status && git log -1 --pretty=fuller
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Create GitHub repository with proper structure
- [x] Configure branch protection rules
- [x] Set up basic CI/CD workflows (tests, lint)
- [x] Create .gitignore and pre-commit configuration
- [x] Write CONTRIBUTING.md

### Phase 2: Testing & Quality (Weeks 3-4)
- [x] Enhance pytest configuration and test coverage
- [x] Set up code coverage reporting
- [x] Add linting and type-checking workflows
- [x] Create test fixtures and helpers
- [ ] Achieve 80%+ code coverage

### Phase 3: Deployment (Weeks 5-6)
- [x] Create Docker development environment
- [ ] Develop deployment scripts
- [x] Set up automated build workflows
- [ ] Test in Docker containers
- [ ] Create deployment documentation

### Phase 4: Distribution (Weeks 7-8)
- [ ] Prepare HACS submission
- [x] Set up GitHub Releases automation
- [ ] Create release documentation
- [ ] Set up distribution channels
- [ ] Test installation methods

### Phase 5: Documentation & Community (Weeks 9-10)
- [x] Finalize all documentation
- [x] Create issue and PR templates
- [ ] Set up GitHub Discussions
- [ ] Create community contribution guide
- [ ] Prepare for public release

### Phase 6: Maintenance & Operations (Ongoing)
- [ ] Monitor CI/CD performance
- [ ] Maintain test coverage
- [ ] Process releases monthly
- [ ] Support community contributions
- [ ] Plan feature releases
