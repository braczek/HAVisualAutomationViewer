# Phase 2 Implementation: Enhanced Features & User Experience

**Status:** In Development  
**Date Started:** December 16, 2025  
**Estimated Completion:** Week 3-4 of Phase 2  
**Deliverable:** Enhanced visualization dashboard, export capabilities, search, theming, and comparison tools

## Overview

Phase 2 expands the core VisualAutoView functionality from single-automation visualization to a comprehensive automation management and analysis suite. This phase adds dashboard capabilities, data export, intelligent search, customizable theming, and comparative analysis tools.

## Phase 2 Features Implementation

### 1. All Automations Dashboard View

**Purpose:** Provide users with a complete overview of all their automations in a grid dashboard format, with each automation displayed as a mini-graph.

**Components:**
- **Backend API:** `GET /api/visualautoview/automations/all`
- **Service:** `visualautoview.get_all_automations_graphs`
- **Cache:** LRU cache with 5-minute TTL for performance
- **Filters:** By automation state (enabled/disabled), automation type (trigger platform)

**Key Files:**
```
Feature_AllAutomationsView/
├── README.md
├── src/
│   ├── all_automations_service.py       # Backend service
│   ├── cache_manager.py                 # Caching logic
│   └── automation_indexer.py            # Index builder
└── test_all_automations.py
```

**Data Model:**
```python
@dataclass
class MiniGraphData:
    automation_id: str
    alias: str
    description: str
    enabled: bool
    graph: AutomationGraph
    node_count: int
    edge_count: int
    primary_triggers: list[str]
    execution_time: float | None = None
    last_triggered: datetime | None = None

@dataclass
class AllAutomationsResponse:
    total_count: int
    enabled_count: int
    disabled_count: int
    automations: list[MiniGraphData]
    cache_timestamp: datetime
```

**Backend Implementation Tasks:**
- [ ] Create service to fetch all automations from HA registry
- [ ] Build mini-graph generator (simplified graph rendering)
- [ ] Implement LRU cache with TTL
- [ ] Add indexing for fast filtering
- [ ] Create API endpoint handler
- [ ] Implement pagination (500+ automations support)
- [ ] Add performance metrics tracking
- [ ] Error handling for complex automations

---

### 2. Export Functionality

**Purpose:** Allow users to export automation graphs in multiple formats (PNG, SVG, PDF) with customizable quality and layout options.

**Components:**
- **Export Formats:** PNG, SVG, PDF
- **Quality Options:** Low (web), Medium (print preview), High (publication)
- **Batch Export:** Export multiple automations as PDF report
- **Services:**
  - `visualautoview.export_graph` - Single automation export
  - `visualautoview.export_batch` - Batch export service

**Key Files:**
```
Feature_ExportFunctionality/
├── README.md
├── src/
│   ├── export_service.py                # Main export orchestrator
│   ├── png_exporter.py                  # PNG generation (puppeteer/html2image)
│   ├── svg_exporter.py                  # SVG export
│   ├── pdf_exporter.py                  # PDF generation (reportlab)
│   └── quality_presets.py               # Export quality configurations
└── test_export.py
```

**Export Configuration:**
```python
@dataclass
class ExportOptions:
    format: Literal['png', 'svg', 'pdf']
    quality: Literal['low', 'medium', 'high']
    include_metadata: bool = True
    include_description: bool = True
    width: int = 1200
    height: int = 800
    dpi: int = 96
    background_color: str = '#ffffff'
    theme: str = 'default'

@dataclass
class ExportResult:
    automation_id: str
    format: str
    file_size: int
    file_path: str
    generation_time: float
    success: bool
    error: str | None = None
```

**Backend Implementation Tasks:**
- [ ] Set up image generation library (consider html2canvas approach)
- [ ] Implement PNG exporter using headless rendering
- [ ] Implement SVG exporter (vis-network export)
- [ ] Implement PDF exporter (multi-page support for batch)
- [ ] Create quality presets (resolution, compression)
- [ ] Add watermarking option
- [ ] Implement file storage/retrieval
- [ ] Add batch export with progress tracking
- [ ] Error handling and validation

**Export Quality Levels:**
```python
QUALITY_PRESETS = {
    'low': {
        'dpi': 72,
        'compression': 'high',
        'max_width': 800,
        'max_height': 600
    },
    'medium': {
        'dpi': 150,
        'compression': 'medium',
        'max_width': 1200,
        'max_height': 900
    },
    'high': {
        'dpi': 300,
        'compression': 'low',
        'max_width': 2400,
        'max_height': 1800
    }
}
```

---

### 3. Search & Filter Functionality

**Purpose:** Enable intelligent search across all automations to find specific triggers, conditions, or actions with relevance scoring.

**Components:**
- **Search Index:** Full-text search on automation metadata, components, entities
- **Filter Engine:** Multi-criteria filtering
- **Relevance Scoring:** Rank results by relevance
- **Services:**
  - `visualautoview.search` - Full-text search
  - `visualautoview.filter` - Advanced filtering

**Key Files:**
```
Feature_SearchAndFilter/
├── README.md
├── src/
│   ├── search_engine.py                 # Search implementation
│   ├── index_builder.py                 # Search index management
│   ├── filter_engine.py                 # Filter logic
│   └── relevance_scorer.py              # Result ranking
└── test_search.py
```

**Search Data Model:**
```python
@dataclass
class SearchResult:
    automation_id: str
    alias: str
    relevance_score: float  # 0-100
    match_type: Literal['trigger', 'condition', 'action', 'metadata']
    matched_text: str
    context: str  # Surrounding text
    graph_preview: AutomationGraph

@dataclass
class SearchQuery:
    text: str
    search_in: list[str] = None  # ['triggers', 'conditions', 'actions', 'metadata']
    filters: dict[str, Any] = None
    limit: int = 50
    offset: int = 0

@dataclass
class FilterCriteria:
    automation_state: Literal['enabled', 'disabled', 'all'] = 'all'
    trigger_platforms: list[str] = None
    entity_ids: list[str] = None
    services_called: list[str] = None
    has_conditions: bool | None = None
    automation_type: str | None = None  # script, automation, trigger
```

**Search Features:**
- Full-text search with wildcards
- Entity ID search (find automations using specific entity)
- Service search (find automations calling specific service)
- Trigger platform search
- Condition type search
- Action type search
- Combined filters (AND/OR logic)

**Backend Implementation Tasks:**
- [ ] Build search index builder
- [ ] Create full-text search engine
- [ ] Implement filter engine with composable filters
- [ ] Add relevance scoring algorithm
- [ ] Create search API endpoint
- [ ] Add query validation and sanitization
- [ ] Implement caching for common searches
- [ ] Performance optimization for large automation sets
- [ ] Search result pagination

**Search Index Structure:**
```python
SEARCH_INDEX = {
    'metadata': {  # alias, description, id
        'automation_id_1': 'Motion Sensor Light Control',
        ...
    },
    'entities': {  # entities mentioned in automation
        'binary_sensor.motion': ['automation_id_1', 'automation_id_5'],
        ...
    },
    'services': {  # services called
        'light.turn_on': ['automation_id_1', 'automation_id_3'],
        ...
    },
    'triggers': {
        'state': ['automation_id_1', ...],
        'time': ['automation_id_2', ...],
        ...
    }
}
```

---

### 4. Theme Customization

**Purpose:** Allow users to create and apply custom color schemes for different automation types or personal preferences.

**Components:**
- **Theme Manager:** Create, store, apply themes
- **Preset Themes:** Default, dark, high-contrast, colorblind
- **Color Palette Editor:** Interactive theme customization UI
- **Services:**
  - `visualautoview.set_theme` - Apply theme
  - `visualautoview.create_theme` - Create custom theme
  - `visualautoview.list_themes` - Get available themes

**Key Files:**
```
Feature_ThemeCustomization/
├── README.md
├── src/
│   ├── theme_manager.py                 # Theme storage and application
│   ├── theme_definitions.py             # Built-in themes
│   ├── color_utils.py                   # Color manipulation utilities
│   └── theme_validator.py               # Theme validation
└── test_themes.py
```

**Theme Data Model:**
```python
@dataclass
class ColorScheme:
    primary: str          # Main action color
    secondary: str        # Secondary action color
    success: str          # Success/enabled color
    warning: str          # Warning color
    error: str            # Error color
    background: str       # Background color
    text: str             # Text color
    border: str           # Border color

@dataclass
class AutomationTheme:
    name: str
    description: str
    author: str | None = None
    
    # Node colors by type
    trigger_color: str
    condition_color: str
    action_color: str
    metadata_color: str
    
    # Advanced options
    color_scheme: ColorScheme
    edge_color: str
    highlight_color: str
    disabled_color: str
    
    # UI theme settings
    card_background: str
    card_border: str
    text_color: str
    accent_color: str
    
    created_at: datetime = field(default_factory=datetime.now)
    user_created: bool = False
```

**Built-in Themes:**
```python
THEME_PRESETS = {
    'default': {
        'trigger_color': '#4CAF50',      # Green
        'condition_color': '#FFC107',    # Amber
        'action_color': '#2196F3',       # Blue
        'metadata_color': '#9E9E9E',     # Grey
        'description': 'Default Material Design colors'
    },
    'dark': {
        'trigger_color': '#81C784',
        'condition_color': '#FFD54F',
        'action_color': '#64B5F6',
        'metadata_color': '#BDBDBD',
        'description': 'Dark theme optimized for night viewing'
    },
    'high_contrast': {
        'trigger_color': '#00AA00',
        'condition_color': '#FFAA00',
        'action_color': '#0066FF',
        'metadata_color': '#333333',
        'description': 'High contrast for accessibility'
    },
    'colorblind_deuteranopia': {
        'trigger_color': '#0173B2',
        'condition_color': '#DE8F05',
        'action_color': '#CC78BC',
        'metadata_color': '#999999',
        'description': 'Optimized for deuteranopia'
    }
}
```

**Backend Implementation Tasks:**
- [ ] Create theme storage mechanism (JSON files)
- [ ] Implement theme manager service
- [ ] Add built-in theme definitions
- [ ] Create theme validation logic
- [ ] Add theme import/export functionality
- [ ] Implement theme application to graphs
- [ ] Add theme caching
- [ ] Create API endpoints for theme management
- [ ] Add user preference storage

---

### 5. Automation Comparison View

**Purpose:** Display multiple automations side-by-side to identify similarities, differences, and potential consolidation opportunities.

**Components:**
- **Comparison Engine:** Analyze automation differences
- **Diff Visualization:** Highlight additions/removals/changes
- **Similarity Scoring:** Calculate automation similarity
- **Services:**
  - `visualautoview.compare_automations` - Compare 2+ automations
  - `visualautoview.find_similar` - Find similar automations

**Key Files:**
```
Feature_AutomationComparison/
├── README.md
├── src/
│   ├── comparison_engine.py             # Comparison logic
│   ├── diff_generator.py                # Diff creation
│   ├── similarity_calculator.py         # Similarity scoring
│   └── consolidation_suggester.py       # Suggest consolidations
└── test_comparison.py
```

**Comparison Data Model:**
```python
@dataclass
class DiffItem:
    type: Literal['added', 'removed', 'modified', 'same']
    component_type: Literal['trigger', 'condition', 'action']
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    path: str = ''  # JSON path to the change

@dataclass
class AutomationDiff:
    automation_id_1: str
    automation_id_2: str
    triggers_diff: list[DiffItem]
    conditions_diff: list[DiffItem]
    actions_diff: list[DiffItem]
    metadata_diff: list[DiffItem]
    total_differences: int
    similarity_score: float  # 0-100

@dataclass
class SimilarityMatch:
    automation_id: str
    alias: str
    similarity_score: float
    match_reasons: list[str]  # ['same trigger platform', 'same service calls', ...]

@dataclass
class ConsolidationSuggestion:
    automations: list[str]
    suggestion: str
    consolidation_level: Literal['high', 'medium', 'low']
    estimated_components_reduction: int
    potential_benefits: list[str]
```

**Comparison Features:**
- Side-by-side graph visualization
- Diff highlighting (green = same, red = removed, blue = added, yellow = modified)
- Component-by-component comparison
- Similarity scoring (0-100%)
- Consolidation suggestions
- Common pattern detection

**Similarity Scoring Algorithm:**
```python
# Score based on:
# - Same trigger platforms (20%)
# - Same conditions (20%)
# - Same services called (20%)
# - Same entities involved (20%)
# - Similar metadata (10%)
# - Similar graph structure (10%)
```

**Backend Implementation Tasks:**
- [ ] Build comparison engine
- [ ] Implement diff algorithm (JSON diff)
- [ ] Create similarity scorer
- [ ] Add consolidation suggestion engine
- [ ] Create comparison API endpoint
- [ ] Add support for comparing 2-5 automations
- [ ] Implement caching for comparison results
- [ ] Add detailed diff reporting
- [ ] Create side-by-side graph merge visualization

---

## Architecture & Integration

### Backend Services Layer

```
custom_components/visualautoview/
├── services/
│   ├── __init__.py
│   ├── all_automations_service.py
│   ├── export_service.py
│   ├── search_service.py
│   ├── theme_service.py
│   └── comparison_service.py
├── models/
│   ├── theme.py
│   ├── search.py
│   ├── comparison.py
│   └── export.py
├── utils/
│   ├── cache.py
│   ├── indexer.py
│   └── validators.py
└── api/
    ├── all_automations.py
    ├── export.py
    ├── search.py
    ├── themes.py
    └── comparison.py
```

### Frontend Components

```
Feature_UIPanel/src/
├── components/
│   ├── all-automations-dashboard.ts      # Dashboard grid view
│   ├── export-panel.ts                   # Export dialog
│   ├── search-filter-panel.ts            # Search/filter UI
│   ├── theme-selector.ts                 # Theme picker
│   └── comparison-view.ts                # Side-by-side comparison
├── services/
│   ├── export-client.ts
│   ├── search-client.ts
│   ├── theme-client.ts
│   └── comparison-client.ts
└── styles/
    └── phase2-components.ts
```

### API Endpoints (New)

```
GET    /api/visualautoview/automations/all
       - Fetch all automations as mini-graphs
       - Params: page, per_page, filter, sort
       
POST   /api/visualautoview/export
       - Export automation graph(s)
       - Body: automation_ids[], format, options
       
POST   /api/visualautoview/search
       - Search automations
       - Body: query, filters, limit
       
GET    /api/visualautoview/themes
       - List available themes
       
POST   /api/visualautoview/themes/apply
       - Apply theme
       - Body: theme_name
       
POST   /api/visualautoview/compare
       - Compare automations
       - Body: automation_ids[]
```

---

## Implementation Timeline

### Week 1-2: All Automations Dashboard
- [ ] Backend service implementation (all_automations_service.py)
- [ ] Mini-graph generator
- [ ] API endpoint
- [ ] Caching layer
- [ ] Frontend dashboard component
- [ ] Unit & integration tests

### Week 2-3: Export Functionality
- [ ] Export service implementation
- [ ] PNG/SVG/PDF exporters
- [ ] Quality presets
- [ ] Batch export support
- [ ] Frontend export dialog
- [ ] File handling & retrieval

### Week 3: Search & Filter
- [ ] Search engine implementation
- [ ] Index builder
- [ ] Filter engine
- [ ] Relevance scorer
- [ ] Frontend search panel
- [ ] API endpoints

### Week 3: Theme Customization
- [ ] Theme manager
- [ ] Built-in themes
- [ ] Theme validator
- [ ] Frontend theme selector
- [ ] User theme storage
- [ ] API endpoints

### Week 4: Automation Comparison
- [ ] Comparison engine
- [ ] Diff generator
- [ ] Similarity calculator
- [ ] Consolidation suggester
- [ ] Frontend comparison view
- [ ] API endpoints

### Week 4: Testing & Polish
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] Frontend component tests
- [ ] Performance testing
- [ ] Bug fixes & refinement
- [ ] Documentation

---

## Performance Targets

- **All Automations Dashboard:** < 500ms for 100+ automations
- **Search:** < 100ms for typical query
- **Export PNG:** < 2s for single automation
- **Comparison:** < 200ms for comparing 2-5 automations
- **Theme Application:** Instant (< 50ms)

---

## Success Criteria

✓ All 5 features implemented and tested  
✓ API endpoints functional  
✓ Frontend components responsive  
✓ Performance targets met  
✓ No critical bugs  
✓ Documentation complete  
✓ User satisfaction with new features  

---

## Dependencies & Libraries

### Backend Additions
- `Pillow` - Image processing (optional, for advanced PNG operations)
- `cairosvg` - SVG to PNG conversion (optional)
- `reportlab` - PDF generation (for batch exports)

### Frontend Additions
- Already have: `vis-network`, `lit`, Home Assistant APIs

---

## Testing Strategy

### Unit Tests
- Service logic validation
- Data model validation
- Filter/search correctness
- Export format generation
- Theme application
- Comparison accuracy

### Integration Tests
- API endpoint functionality
- Frontend-backend data flow
- File export and retrieval
- Search index building
- Theme persistence

### Manual Testing
- Dashboard with 50+ automations
- Export to multiple formats
- Search with various queries
- Theme switching
- Comparison views
- Mobile responsiveness

---

## Documentation

- Feature-specific READMEs in each Feature_ folder
- Updated implementationPlan.md with Phase 2 details
- User guide (PHASE2_README.md)
- API documentation
- Component documentation

---

## Notes & Considerations

1. **Caching Strategy:** Use LRU cache with 5-minute TTL for all automations, longer for search indexes
2. **File Storage:** Export files stored in HA's config directory, auto-cleaned after 7 days
3. **Search Index:** Built incrementally on startup, cached for subsequent searches
4. **Theme Storage:** User themes stored in JSON files, synced with HA config
5. **Comparison:** Limited to 5 automations max for performance
6. **Batch Export:** Chunked processing for 50+ automations
7. **Mobile:** Dashboard uses responsive grid, export uses smaller resolution on mobile

---

**Document Version:** 1.0  
**Status:** In Progress  
**Phase:** 2 of 5  
**Target Completion:** 2 weeks  
