# Contributing to Visual AutoView

Thank you for your interest in contributing to Visual AutoView! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to a community code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git
- Docker (for testing)

### Setup Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/visualautoview.git
   cd visualautoview
   ```

2. **Run setup script**:
   ```bash
   chmod +x scripts/setup-dev-env.sh
   ./scripts/setup-dev-env.sh
   ```

3. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

## Making Changes

### Branch Strategy

Create a feature branch from `develop`:
```bash
git checkout -b feature/your-feature-name
git checkout -b bugfix/your-bug-fix
git checkout -b docs/your-documentation
```

### Code Style

We use automated code formatting tools:

```bash
# Format code
black custom_components/visualautoview tests

# Sort imports
isort custom_components/visualautoview tests

# Check linting
flake8 custom_components/visualautoview tests

# Type checking
mypy custom_components/visualautoview --ignore-missing-imports
```

Or run all checks at once:
```bash
./scripts/dev-check.sh
```

### Commit Messages

Follow the conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, perf, test, chore
**Scope**: graph-parser, api, frontend, etc.
**Subject**: Imperative, lowercase, no period

**Examples**:
```
feat(graph-parser): add circular dependency detection

fix(api): handle invalid automation YAML gracefully

docs(readme): update installation instructions

test(graph-parser): add tests for edge cases
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=custom_components/visualautoview --cov-report=html
```

### Run Specific Tests
```bash
pytest tests/unit/test_graph_parser.py
pytest -k test_parse_automation
```

### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Pull Request Process

1. **Ensure your branch is up to date**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run full test suite**:
   ```bash
   ./scripts/dev-check.sh
   ```

3. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature
   ```

4. **Create pull request** on GitHub with:
   - Clear description of changes
   - Reference to related issues (#123)
   - Screenshots for UI changes
   - List of testing performed

5. **Address review feedback** and push additional commits

6. **After approval**, maintainers will merge

## Reporting Issues

### Bug Reports
Please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (HA version, Python version, browser)
- Relevant logs

### Feature Requests
Please include:
- Problem statement
- Proposed solution
- Alternative approaches considered
- Implementation ideas (if any)

## Documentation

- Update docstrings for new functions/classes
- Update README.md for user-facing changes
- Update CHANGELOG.md with changes
- Add comments for complex logic

## Merging to Main

Only maintainers can merge to `main`. The process:

1. Feature is merged to `develop` via PR
2. Tested in `develop` branch
3. Merged to `main` as part of release
4. Tagged with semantic version (v1.0.0)
5. GitHub Release created automatically

## Release Process

See CHANGELOG.md and release-related scripts for details.

## Questions?

- Create a GitHub Discussion
- Open an issue with [QUESTION] tag
- Comment on existing issues

Thank you for contributing! 🎉
