# Husky Pre-Commit Hooks

This project uses Husky to automatically run code quality checks before commits. This ensures all code meets quality standards before being pushed.

## What Gets Checked

### Backend (Python)
1. **Black Formatting** - Code formatting compliance
2. **isort** - Import sorting consistency
3. **pytest** - Unit tests pass (22 tests)

### Frontend (TypeScript)
1. **TypeScript Type Check** - Type safety validation
2. **ESLint** - Code style and quality rules

## Installation

Husky is automatically installed with the project dependencies:

```bash
npm install
```

The pre-commit hook is automatically set up in `.husky/pre-commit`.

## How It Works

When you run `git commit`, Husky will:

1. ✅ Check Python code formatting with Black
2. ✅ Check import ordering with isort
3. ✅ Run Python tests with pytest
4. ✅ Type-check TypeScript/JavaScript
5. ✅ Lint frontend code with ESLint

If any check fails, the commit is **blocked** and you'll see which check failed.

## Fixing Common Issues

### Black Formatting Failed
```bash
black custom_components/visualautoview tests
```

### isort Failed
```bash
isort custom_components/visualautoview tests
```

### Python Tests Failed
```bash
pytest custom_components/visualautoview tests
```

### TypeScript Type Check Failed
```bash
cd frontend
npm run type-check
```

### ESLint Failed
```bash
cd frontend
npm run lint
```

## Bypassing Checks (Not Recommended)

If you absolutely need to bypass pre-commit checks:

```bash
git commit --no-verify
```

⚠️ **Warning:** This should only be used in emergencies. Commit checks exist to maintain code quality.

## Updating the Pre-Commit Hook

To modify what's checked, edit `.husky/pre-commit`:

```bash
# Backend checks
python -m black --check custom_components/visualautoview tests
python -m isort --check-only custom_components/visualautoview tests
pytest custom_components/visualautoview tests --tb=short

# Frontend checks
cd frontend
npm run type-check
npm run lint
```

## Troubleshooting

### Husky Hook Not Running

If the hook doesn't run on commit:

1. Verify Husky is installed:
   ```bash
   npm ls husky
   ```

2. Check hook file exists and is executable:
   ```bash
   ls -la .husky/pre-commit
   ```

3. Re-initialize Husky:
   ```bash
   npm install
   npx husky-init
   ```

### Hook Permissions

On Unix/Linux/macOS, the hook file needs execute permissions:

```bash
chmod +x .husky/pre-commit
```

On Windows (Git Bash):
```bash
git update-index --chmod=+x .husky/pre-commit
```

## CI/CD Integration

The same checks run in GitHub Actions:
- `.github/workflows/lint.yml` - Code quality
- `.github/workflows/tests.yml` - Unit tests

These checks must pass before PRs can be merged.

## Benefits

✅ **Catch Issues Early** - Prevents bad code from being committed
✅ **Maintain Consistency** - All code follows same standards
✅ **Save CI Time** - Failed checks don't reach CI/CD
✅ **Better Code Review** - Reviewers focus on logic, not formatting
✅ **Team Confidence** - Know all code meets quality bar

## Disabling Husky

If you need to disable Husky temporarily:

```bash
# Disable
npm uninstall husky

# Re-enable later
npm install husky --save-dev
```

---

**Setup Date:** 2025-12-23
**Husky Version:** Latest
**Included Checks:** 5 (Python linting, tests, TypeScript, ESLint)
