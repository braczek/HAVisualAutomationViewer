# Feature-Based Folder Structure Plan for VisualAutoView

## Overview

Split the VisualAutoView Home Assistant integration into 8 feature-based folders to enable focused, context-efficient AI agent implementation. Each Feature_{name} folder will contain related components, documentation, and clear dependencies.

## Feature Breakdown

### 1. Feature_GraphParser (Backend Core)
**Purpose:** YAML automation parsing and graph data structure generation

**Components:**
- `graph_parser.py` - Main parser logic
- `data_models.py` - Python dataclasses (AutomationNode, AutomationEdge, AutomationGraph)
- `const.py` - Constants and enums
- `README.md` - Feature documentation

**Key Responsibilities:**
- Parse automation configuration from HA's automation registry
- Extract triggers, conditions, and actions
- Build graph data structure (nodes and edges)
- Handle complex automation structures (choose, if-then, parallel)

**Dependencies:** None (foundational feature)

**Implementation Functions:**
```python
def parse_automation(automation_config: dict) -> AutomationGraph
def extract_triggers(automation: dict) -> list[AutomationNode]
def extract_conditions(automation: dict) -> list[AutomationNode]
def extract_actions(automation: dict) -> list[AutomationNode]
def build_edges(nodes: list[AutomationNode]) -> list[AutomationEdge]
```

---

### 2. Feature_Integration (Backend Integration)
**Purpose:** Home Assistant custom component integration layer

**Components:**
- `__init__.py` - Integration setup and lifecycle
- `manifest.json` - Integration metadata
- `config_flow.py` - Optional configuration flow
- `services.yaml` - Service definitions (if needed)
- `api_endpoints.py` - REST/WebSocket API handlers
- `README.md` - Feature documentation

**Key Responsibilities:**
- Register custom panel for graph visualization
- Provide API endpoint for automation graph data
- Handle WebSocket communication with frontend
- Integration setup and configuration

**Dependencies:**
- Feature_GraphParser (imports graph data models and parser functions)

**API Endpoints:**
- `/api/visualautoview/graph/<automation_id>` - Get graph data for automation
- WebSocket command: `visualautoview/get_graph` - Real-time graph updates

---

### 3. Feature_GraphRenderer (Frontend Visualization)
**Purpose:** Interactive graph visualization using vis-network

**Components:**
- `src/automation-graph.ts` - Main graph rendering component
- `src/graph-config.ts` - vis-network configuration
- `src/graph-styles.ts` - Styling and theming
- `src/graph-interactions.ts` - User interaction handlers
- `README.md` - Feature documentation

**Key Responsibilities:**
- Initialize vis-network graph
- Render nodes and edges
- Handle user interactions (zoom, pan, click, hover)
- Apply hierarchical layout
- Color-coded nodes by type

**Dependencies:**
- Feature_Integration (fetches graph data from backend API)

**Key Features:**
- Hierarchical layout (top-to-bottom)
- Color scheme: Triggers (green), Conditions (amber), Actions (blue)
- Zoom and pan controls
- Node tooltips on hover
- Static layout (no physics simulation)

---

### 4. Feature_UIPanel (Frontend Panel)
**Purpose:** Home Assistant UI panel/modal integration

**Components:**
- `src/graph-view-panel.ts` - Main panel component
- `src/panel-types.ts` - TypeScript interfaces
- `src/panel-styles.ts` - Lit CSS styles
- `README.md` - Feature documentation

**Key Responsibilities:**
- Register as Home Assistant panel/dialog
- Fetch automation data from backend
- Manage panel lifecycle and state
- Handle user interactions (close, refresh)
- Loading states and error handling

**Dependencies:**
- Feature_GraphRenderer (embeds graph visualization)
- Feature_Integration (communicates with backend)

**UI Components:**
- Modal dialog using HA's `<ha-dialog>` component
- Header with automation name and close button
- Graph canvas filling available space
- Responsive sizing for mobile/tablet

---

### 5. Feature_MenuIntegration (UI Integration Point)
**Purpose:** Integration into automation editor's 3-dot overflow menu

**Components:**
- `src/menu-hook.ts` - Menu extension logic
- `src/automation-editor-extension.ts` - HA automation editor hooks
- `README.md` - Feature documentation

**Key Responsibilities:**
- Hook into automation editor component
- Add "View as Graph" to 3-dot overflow menu
- Implement menu action handler
- Trigger graph modal display
- Pass automation ID to panel

**Dependencies:**
- Feature_UIPanel (opens the graph panel)
- Feature_Integration (retrieves automation data)

**Integration Approach:**
```typescript
customElements.whenDefined('ha-automation-editor').then(() => {
  const AutomationEditor = customElements.get('ha-automation-editor');
  // Add graph view option to menu actions
});
```

---

### 6. Feature_Testing (Testing Infrastructure)
**Purpose:** Comprehensive test suite for backend and frontend

**Components:**
- `backend/test_graph_parser.py` - Parser unit tests
- `backend/test_init.py` - Integration tests
- `frontend/component-tests/` - Frontend component tests
- `integration/` - End-to-end tests
- `test-data/` - Sample automation configurations
- `README.md` - Testing documentation

**Key Responsibilities:**
- Unit tests for graph parser
- Integration tests for HA component
- Frontend component rendering tests
- Manual test scenarios
- CI/CD workflow integration

**Dependencies:**
- All features (tests all components)

**Test Coverage:**
- Simple automations (single trigger, condition, action)
- Complex conditions (nested and/or logic)
- Choose/if-then actions
- Parallel actions
- Multiple triggers
- Long action sequences
- Mobile/tablet interfaces
- Light and dark themes

---

### 7. Feature_Build (Build & Distribution)
**Purpose:** Frontend build pipeline and HACS distribution

**Components:**
- `frontend/package.json` - NPM dependencies
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/rollup.config.js` - Build configuration
- `frontend/dist/` - Built assets
- `.github/workflows/validate.yml` - CI/CD
- `hacs.json` - HACS metadata
- `build-scripts/` - Custom build utilities
- `README.md` - Build documentation

**Key Responsibilities:**
- Frontend build pipeline (TypeScript → JavaScript)
- Bundle optimization and minification
- HACS distribution configuration
- CI/CD automation
- Version management

**Dependencies:**
- Feature_GraphRenderer & Feature_UIPanel (builds frontend)
- Feature_Integration (packages integration)

**Build Output:**
- Single bundled JavaScript file (`visualautoview-card.js`)
- Source maps for debugging
- Optimized for production (terser minification)

---

### 8. Feature_Documentation (Documentation)
**Purpose:** User and developer documentation

**Components:**
- `README.md` - Main user documentation
- `info.md` - HACS info page
- `LICENSE` - MIT License
- `CONTRIBUTING.md` - Contribution guidelines
- `screenshots/` - UI screenshots
- `examples/` - Example automations
- `CHANGELOG.md` - Version history
- `README.md` - Documentation overview

**Key Responsibilities:**
- User installation and usage guides
- Developer setup instructions
- API documentation
- Troubleshooting guides
- Screenshots and examples

**Dependencies:**
- All features (documents all components)

**Documentation Sections:**
- Feature overview with screenshots
- Installation (HACS + manual)
- Usage guide (accessing from automation editor)
- Supported automation features
- Troubleshooting
- Contributing guidelines

---

## Folder Structure

```
VisualAutoView/
├── Feature_GraphParser/
│   ├── graph_parser.py
│   ├── data_models.py
│   ├── const.py
│   └── README.md
│
├── Feature_Integration/
│   ├── __init__.py
│   ├── manifest.json
│   ├── config_flow.py
│   ├── services.yaml
│   ├── api_endpoints.py
│   └── README.md
│
├── Feature_GraphRenderer/
│   ├── src/
│   │   ├── automation-graph.ts
│   │   ├── graph-config.ts
│   │   ├── graph-styles.ts
│   │   └── graph-interactions.ts
│   └── README.md
│
├── Feature_UIPanel/
│   ├── src/
│   │   ├── graph-view-panel.ts
│   │   ├── panel-types.ts
│   │   └── panel-styles.ts
│   └── README.md
│
├── Feature_MenuIntegration/
│   ├── src/
│   │   ├── menu-hook.ts
│   │   └── automation-editor-extension.ts
│   └── README.md
│
├── Feature_Testing/
│   ├── backend/
│   │   ├── test_graph_parser.py
│   │   └── test_init.py
│   ├── frontend/
│   │   └── component-tests/
│   ├── integration/
│   ├── test-data/
│   └── README.md
│
├── Feature_Build/
│   ├── frontend/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── rollup.config.js
│   ├── .github/
│   │   └── workflows/
│   │       └── validate.yml
│   ├── hacs.json
│   ├── build-scripts/
│   └── README.md
│
├── Feature_Documentation/
│   ├── README.md
│   ├── info.md
│   ├── LICENSE
│   ├── CONTRIBUTING.md
│   ├── screenshots/
│   ├── examples/
│   └── CHANGELOG.md
│
└── implementationPlan.md (original plan)
```

---

## Feature Dependency Map

```
Feature_GraphParser (Foundation)
    ↓
Feature_Integration (Backend API Layer)
    ↓
Feature_GraphRenderer ← Feature_UIPanel
    ↑                        ↓
    └────────────Feature_MenuIntegration
    
Feature_Testing → (Tests all above)
Feature_Build → (Builds & packages all)
Feature_Documentation → (Documents all)
```

**Implementation Order (Recommended):**
1. Feature_GraphParser (no dependencies)
2. Feature_Integration (depends on GraphParser)
3. Feature_GraphRenderer (depends on Integration)
4. Feature_UIPanel (depends on GraphRenderer)
5. Feature_MenuIntegration (depends on UIPanel)
6. Feature_Testing (tests all implemented features)
7. Feature_Build (packages everything)
8. Feature_Documentation (documents final product)

---

## Implementation Strategy

### Phase 1: Foundation (Weeks 1-2)
- Implement Feature_GraphParser
- Implement Feature_Integration
- Create basic backend infrastructure

### Phase 2: Visualization (Weeks 3-4)
- Implement Feature_GraphRenderer
- Implement Feature_UIPanel
- Create frontend components

### Phase 3: Integration (Weeks 5-6)
- Implement Feature_MenuIntegration
- Connect frontend to backend
- End-to-end functionality

### Phase 4: Quality (Weeks 7-8)
- Implement Feature_Testing
- Implement Feature_Build
- Polish and optimize

### Phase 5: Release (Weeks 9-10)
- Implement Feature_Documentation
- Final testing and validation
- HACS submission

---

## Key Considerations

### 1. Deployment Structure
**Question:** Should final `custom_components/visualautoview/` be assembled from features during build?

**Recommendation:** Use build-time assembly
- Features remain independent during development
- Build script assembles final structure for deployment
- Maintains clean separation of concerns
- Example: `Feature_GraphParser/graph_parser.py` → `custom_components/visualautoview/graph_parser.py`

### 2. Shared Types/Interfaces
**Question:** Create shared types folder or duplicate types in each feature?

**Recommendation:** Hybrid approach
- Core data models in Feature_GraphParser (single source of truth)
- Frontend types in Feature_GraphRenderer (TypeScript interfaces)
- API contracts defined in Feature_Integration (shared between backend/frontend)
- Minimal duplication, clear ownership

### 3. Implementation Order
**Question:** Follow dependency chain or prioritize high-value features?

**Recommendation:** Follow dependency chain with incremental testing
- Implement Feature_GraphParser first (foundation)
- Add Feature_Integration with minimal API
- Create Feature_GraphRenderer with test data (validate visualization early)
- Build Feature_UIPanel and Feature_MenuIntegration
- Backfill Feature_Testing, Feature_Build, Feature_Documentation

### 4. AI Agent Context Management
**Goal:** Each feature should fit within AI context window

**Strategy:**
- Each Feature_{name}/README.md contains complete context for that feature
- Include relevant code snippets from dependencies
- Document API contracts clearly
- Keep features focused (< 5 files per feature)
- Cross-reference related features in README

### 5. Testing Strategy
**Approach:** Test each feature independently before integration

- Feature_GraphParser: Unit tests with sample YAML
- Feature_Integration: Mock HA environment tests
- Feature_GraphRenderer: Component tests with mock data
- Feature_UIPanel: UI interaction tests
- Feature_MenuIntegration: Integration tests with HA
- Full integration: End-to-end scenarios

---

## Success Criteria

Each feature is complete when:
- [ ] All components implemented and functional
- [ ] README.md with clear documentation
- [ ] Tests passing (where applicable)
- [ ] Dependencies clearly documented
- [ ] Code follows HA development guidelines
- [ ] Works in isolation (with mocked dependencies)

Project is complete when:
- [ ] All 8 features implemented
- [ ] Integration tests passing
- [ ] Build pipeline functional
- [ ] Documentation complete
- [ ] Ready for HACS submission

---

## Next Steps

1. **Review and refine this plan** - Validate feature boundaries and dependencies
2. **Create folder structure** - Set up Feature_{name} directories
3. **Create feature READMEs** - Template for each feature's documentation
4. **Begin Phase 1 implementation** - Start with Feature_GraphParser
5. **Iterate and adapt** - Adjust plan based on implementation learnings
