# GitHub Copilot Instructions for HAVisualAutomationViewer

This file provides guidelines for GitHub Copilot to ensure generated code passes all CI/CD checks in the GitHub Actions build pipeline.

## Project Overview

**Visual AutoView** is a Home Assistant integration for visualizing and analyzing automation graphs and dependencies.

### Project Goals
- Provide comprehensive visualization of Home Assistant automations
- Analyze automation dependencies and execution paths
- Offer advanced analytics and performance metrics
- Enable search, filtering, and comparison of automations
- Support automation template expansion and theme management

### Technology Stack
- **Backend**: Python 3.11+ (Home Assistant Custom Component)
- **Frontend**: TypeScript with Vite build system
- **Integration Type**: Home Assistant system integration
- **Minimum HA Version**: 2023.11.0

## Project Structure

```
HAVisualAutomationViewer/
├── custom_components/visualautoview/    # Main Home Assistant integration
│   ├── __init__.py                      # Integration setup
│   ├── const.py                         # Constants and configuration
│   ├── manifest.json                    # Integration metadata
│   ├── graph_parser.py                  # YAML automation graph parsing
│   ├── api/                             # REST API endpoints
│   │   ├── base.py                      # Base API class
│   │   ├── models.py                    # Data models
│   │   ├── phase1_api.py                # Core graph APIs
│   │   ├── phase2_api.py                # Dashboard & management APIs
│   │   └── phase3_api.py                # Analytics APIs
│   └── services/                        # Business logic services
│       ├── all_automations_service.py   # Automation collection
│       ├── comparison_engine.py         # Automation comparison
│       ├── dependency_graph_service.py  # Graph analysis
│       ├── entity_relationship_service.py
│       ├── execution_path_service.py    # Execution flow analysis
│       ├── export_service.py            # Export functionality
│       ├── performance_metrics_service.py
│       ├── search_engine.py             # Search capabilities
│       ├── template_expansion_service.py
│       └── theme_manager.py             # Theme support
├── frontend/                            # Web UI (TypeScript/Vite)
│   ├── src/
│   │   ├── main.ts                      # Entry point
│   │   ├── app.ts                       # Main application
│   │   ├── components/                  # UI components
│   │   ├── services/                    # Frontend services
│   │   ├── utils/                       # Utility functions
│   │   └── views/                       # Page views
│   ├── package.json
│   └── vite.config.ts
├── tests/                               # Python unit tests
│   ├── test_graph_parser.py
│   └── conftest.py
├── .github/
│   ├── workflows/build.yml              # CI/CD pipeline
│   └── COPILOT_INSTRUCTIONS.md         # This file
├── hacs.json                            # HACS integration manifest
├── pyproject.toml                       # Python project configuration
└── requirements-dev.txt                 # Development dependencies
```

## Key Components to Know

### Phase 1 (Core Graph Analysis)
- Graph parsing from YAML automations
- Dependency visualization
- Relationship mapping between entities

### Phase 2 (Dashboard & Management)
- Automation dashboard
- Management endpoints
- Template expansion
- Theme support

### Phase 3 (Advanced Analytics)
- Performance metrics
- Execution path analysis
- Entity relationship analysis
- Comparison engine
- Search functionality

## Output Guidelines

**IMPORTANT**: When generating code or making changes:
- **Do NOT create summary or status markdown files** (e.g., IMPLEMENTATION_COMPLETE.md, STATUS_REPORT.md)
- **Do NOT generate documentation summaries after running commands or making changes**
- **Keep output minimal** - only generate/modify code that is necessary
- **No documentation files** unless explicitly requested
- **Focus on implementation** - let the code speak for itself
- **Direct commits** - make changes and commit without intermediate documentation
- **Concise responses** - confirm completion without lengthy explanations

When asked to add features or fix issues:
1. Generate/modify only the necessary code files
2. Ensure code passes all linting and formatting checks
3. Commit changes with clear, descriptive messages
4. No extra markdown files or documentation summaries
5. Brief confirmation only - avoid detailed summaries of what was done

## Python Code Standards

### Black Formatting
- **Line length**: 88 characters maximum
- **Indentation**: 4 spaces
- **String quotes**: Prefer double quotes for consistency
- Always run `black` on modified Python files before committing

Example of correct formatting:
```python
def calculate_automation_metrics(
    automations: list[dict], entity_map: dict
) -> dict:
    """Calculate performance metrics for automations."""
    metrics = {}
    for automation in automations:
        metrics[automation["id"]] = {
            "execution_time": automation.get("execution_time", 0),
            "success_rate": automation.get("success_rate", 0),
        }
    return metrics
```

### Import Sorting (isort)
- **Profile**: Use `black` profile for compatibility
- **Order**: Standard library → Third-party → First-party imports
- **Grouping**: Separate groups with blank lines
- Always run `isort` before committing

Example of correct import order:
```python
import json
import logging
from pathlib import Path
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant

from visualautoview.api.base import BaseAPI
from visualautoview.services.search_engine import SearchEngine
```

**First-party modules** (visualautoview package):
- `from visualautoview.api import ...`
- `from visualautoview.services import ...`
- `from visualautoview.graph_parser import ...`

### Code Style Guidelines

1. **Type Hints**: Always add type hints to function signatures
   ```python
   def process_automation(automation_id: str) -> dict[str, Any]:
       pass
   ```

2. **Docstrings**: Use triple-quoted strings for all public functions/classes
   ```python
   def get_dependency_graph(automation_id: str) -> dict:
       """Retrieve the dependency graph for an automation.
       
       Args:
           automation_id: The unique identifier of the automation.
           
       Returns:
           A dictionary containing the dependency graph structure.
       """
   ```

3. **Line Length**: Never exceed 88 characters per line
   - Break long function arguments across multiple lines
   - Break long strings using implicit concatenation

4. **Blank Lines**:
   - 2 blank lines between top-level class/function definitions
   - 1 blank line between methods in a class
   - 1 blank line between logical sections within functions

### Pre-commit Checklist
When writing Python code, ensure:
- [ ] Imports are sorted with isort
- [ ] Code passes black formatting
- [ ] Type hints are present on all functions
- [ ] Docstrings exist for public APIs
- [ ] No trailing whitespace
- [ ] Line length ≤ 88 characters

## Node.js / TypeScript Code Standards

### ESLint & Prettier Configuration
- **Line length**: 100 characters
- **Semicolons**: Required
- **Quotes**: Double quotes
- **Tab width**: 2 spaces
- **Arrow functions**: Parentheses around parameters

Example of correct TypeScript formatting:
```typescript
interface GraphNode {
  id: string;
  label: string;
  dependencies: string[];
}

async function fetchAutomationGraph(
  automationId: string
): Promise<GraphNode[]> {
  const response = await fetch(
    `/api/automation/${automationId}/graph`
  );
  return response.json();
}

const processGraph = (nodes: GraphNode[]): Map<string, Set<string>> => {
  const dependencies = new Map<string, Set<string>>();
  nodes.forEach((node) => {
    dependencies.set(node.id, new Set(node.dependencies));
  });
  return dependencies;
};
```

### TypeScript Best Practices

1. **Type Definitions**: Always define types explicitly
   ```typescript
   type AutomationStatus = "running" | "stopped" | "paused";
   
   interface Automation {
     id: string;
     name: string;
     status: AutomationStatus;
     lastExecuted?: Date;
   }
   ```

2. **Async/Await**: Prefer async/await over promises
   ```typescript
   async function loadData() {
     try {
       const data = await fetchData();
       return processData(data);
     } catch (error) {
       console.error("Failed to load data:", error);
       throw error;
     }
   }
   ```

3. **Optional Chaining & Nullish Coalescing**:
   ```typescript
   const name = automation?.config?.name ?? "Unknown";
   const value = data?.nested?.property ?? defaultValue;
   ```

4. **Avoid `any` Type**: Use specific types or generics
   ```typescript
   // ❌ Bad
   function process(data: any): any {}
   
   // ✅ Good
   function process<T>(data: T): T {}
   ```

### Code Style Guidelines

1. **Naming Conventions**:
   - Classes: PascalCase (`GraphParser`, `DependencyService`)
   - Functions/variables: camelCase (`fetchGraph`, `automationId`)
   - Constants: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`, `API_TIMEOUT`)
   - Types/Interfaces: PascalCase (`GraphNode`, `AutomationConfig`)

2. **Function Length**: Keep functions under 30 lines
   - Extract complex logic into smaller functions
   - Use descriptive function names

3. **Comments**: Only for "why", not "what"
   ```typescript
   // ❌ Bad
   // Increment counter
   count++;
   
   // ✅ Good
   // Increment counter to track retry attempts for rate limiting
   retryCount++;
   ```

4. **Error Handling**: Always handle potential errors
   ```typescript
   try {
     await operation();
   } catch (error) {
     if (error instanceof NetworkError) {
       // Handle network error
     } else if (error instanceof ValidationError) {
       // Handle validation error
     } else {
       throw error;
     }
   }
   ```

### Pre-commit Checklist
When writing Node.js/TypeScript code, ensure:
- [ ] Code passes ESLint checks
- [ ] Code is formatted with Prettier
- [ ] Types are properly defined
- [ ] No `any` types used
- [ ] Proper error handling implemented
- [ ] Line length ≤ 100 characters
- [ ] Async operations properly handled

## GitHub Actions Workflow Requirements

When generating code that affects CI/CD:

1. **Action Versions**: Use latest stable versions
   - `actions/checkout@v4`
   - `actions/setup-python@v4`
   - `actions/setup-node@v4`
   - `actions/upload-artifact@v4`

2. **Python Version**: Target 3.11 minimum

3. **Node Version**: Target 18.x LTS or newer

4. **Linting Steps**: Ensure workflow includes:
   ```yaml
   - name: Run isort check
     run: isort --check-only custom_components/visualautoview tests
   
   - name: Run black check
     run: black --check custom_components/visualautoview tests
   ```

5. **Build Steps**: Verify all dependencies install correctly

## Common Mistakes to Avoid

### Python
- ❌ Mixing import styles: `from module import *`
- ❌ Using `type` comments instead of annotations: `x = 5  # type: int`
- ❌ Lines exceeding 88 characters without breaking
- ❌ Inconsistent quote styles
- ❌ Missing blank lines between functions

### Node.js/TypeScript
- ❌ Using `var` instead of `const`/`let`
- ❌ Implicit `any` types
- ❌ Promise chains instead of async/await
- ❌ Magic numbers without constants
- ❌ Mixing quote styles

## Quick Reference Commands

### Python
```bash
# Format with black
black custom_components/visualautoview tests

# Sort imports with isort
isort custom_components/visualautoview tests

# Check formatting without modifying
black --check custom_components/visualautoview tests
isort --check-only custom_components/visualautoview tests
```

### Node.js
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm ci

# Run linter
npm run lint

# Format code
npm run format

# Build project
npm run build
```

## Integration with VS Code

Use these extensions for real-time formatting:
- **Python**: ms-python.python + ms-python.vscode-pylance
- **Node.js**: ESLint + Prettier - Code formatter

With proper `.vscode/settings.json` configuration, code will format automatically on save.

## Questions or Updates?

If you encounter formatting issues during code generation:
1. Check the error message in the GitHub Actions build log
2. Run the appropriate formatter locally
3. Verify against these guidelines
4. Commit the formatted code

For more information, see:
- Black documentation: https://black.readthedocs.io/
- isort documentation: https://pycqa.github.io/isort/
- ESLint documentation: https://eslint.org/
- Prettier documentation: https://prettier.io/
