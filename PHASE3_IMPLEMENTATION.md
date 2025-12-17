# Phase 3 Implementation Plan: Advanced Automation Analysis Features

**Project:** Visual AutoView - Home Assistant Automation Graph Visualization  
**Phase:** 3 (Advanced Features)  
**Status:** Planning & Design  
**Created:** December 17, 2025  
**Estimated Duration:** 3-4 weeks (35-50 hours)

---

## Phase 3 Overview

Phase 3 focuses on advanced analytics and visualization features that provide deeper insights into automation behavior, performance, and relationships. These features build on the Phase 1 graph visualization and Phase 2 dashboard/search capabilities.

### Phase 3 Feature Goals

1. **Entity Relationship View:** Understand which entities trigger/are affected by automations
2. **Dependency Graph:** Visualize automation chains and cascading effects
3. **Execution Path Highlighting:** Show which automation paths executed in real-time
4. **Performance Metrics:** Display execution time, frequency, and triggering patterns
5. **Template Expansion:** Preview Jinja2 templates with live entity states

---

## Feature 1: Entity Relationship View

### Purpose & Use Cases

**Primary Purpose:** Show the complete flow of entities through an automation and identify cross-automation dependencies at the entity level.

**User Scenarios:**
- Understand all entities affected by a single automation
- Find automations triggered by a specific entity
- Identify potential cascading effects (automation A triggers entity that triggers automation B)
- Detect unused entities in complex automations
- Visualize entity flow from trigger → condition → action

### Architecture Design

```
Entity Relationship View
│
├── Entity Interaction Tracking
│   ├── Trigger Entities (input)
│   ├── Condition Entities (checks)
│   ├── Service Target Entities (output)
│   └── Data Template Entities (references)
│
├── Relationship Graph
│   ├── Entity Nodes (grouped by type)
│   ├── Automation Nodes (connecting entities)
│   ├── Effect Edges (trigger/control/affect)
│   └── Relationship Metadata (type, strength)
│
├── Cross-Automation Links
│   ├── Automation A output → Automation B input
│   ├── Cascade detection
│   └── Dependency chain visualization
│
└── Analysis Features
    ├── Entity Impact Analysis
    ├── Orphaned Entity Detection
    ├── Relationship Strength Scoring
    └── Cascade Chain Identification
```

### Data Models

```python
@dataclass
class EntityRelationship:
    """Relationship between an entity and automation."""
    
    entity_id: str
    automation_id: str
    automation_alias: str
    
    relationship_type: Literal[
        'trigger',          # Entity state change triggers automation
        'condition',        # Entity used in condition
        'action_target',    # Entity is target of action
        'data_template',    # Entity referenced in template
        'service_param'     # Entity in service parameter
    ]
    
    direction: Literal['input', 'bidirectional', 'output']
    strength: float  # 0.0-1.0 (importance/impact)
    
    # Additional context
    data: dict[str, Any]  # Raw relationship details
    last_triggered: datetime | None
    interaction_count: int = 0

@dataclass
class EntityNode:
    """Node representing a single entity in relationship view."""
    
    entity_id: str
    entity_name: str
    entity_type: str  # light, switch, binary_sensor, etc.
    current_state: str
    
    relationships: list[EntityRelationship]
    incoming_relationships: int
    outgoing_relationships: int
    
    # Analytics
    is_trigger_source: bool
    is_action_target: bool
    is_condition_check: bool
    cascade_chains: list[str]  # automation IDs in chain

@dataclass
class RelationshipGraph:
    """Complete graph of entity relationships."""
    
    entities: dict[str, EntityNode]  # entity_id -> EntityNode
    relationships: list[EntityRelationship]
    
    # Cascade information
    cascade_chains: list[list[str]]  # List of automation chains
    critical_entities: list[str]  # Entities that affect multiple automations
    
    # Statistics
    total_entities: int
    total_relationships: int
    automation_count: int
    avg_relationships_per_entity: float
```

### Service Implementation Structure

```python
class EntityRelationshipService:
    """Service for analyzing entity relationships in automations."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the service."""
        self.hass = hass
        self._relationship_cache: dict[str, RelationshipGraph] = {}
    
    async def get_entity_relationships(
        self,
        automation_id: str | None = None,
        entity_id: str | None = None
    ) -> RelationshipGraph:
        """Get entity relationships for automation(s)."""
    
    async def analyze_entity_impact(
        self,
        entity_id: str
    ) -> dict[str, Any]:
        """Analyze impact of entity changes on all automations."""
    
    async def detect_cascades(
        self,
        automation_id: str
    ) -> list[list[str]]:
        """Detect cascading automation chains."""
    
    async def find_orphaned_entities(
        self,
        automation_id: str
    ) -> list[str]:
        """Find entities referenced but not actively used."""
    
    def calculate_relationship_strength(
        self,
        relationship: EntityRelationship
    ) -> float:
        """Calculate relationship importance score."""
    
    async def get_cross_automation_impacts(
        self,
        automation_id: str
    ) -> list[dict[str, Any]]:
        """Find other automations affected by this one."""
```

### API Endpoints

```
GET /api/visualautoview/entity-relationships/{automation_id}
  → RelationshipGraph for specific automation

GET /api/visualautoview/entity-relationships
  → All entity relationships across all automations

GET /api/visualautoview/entity-impact/{entity_id}
  → Impact analysis for specific entity

GET /api/visualautoview/automation-cascades/{automation_id}
  → Cascade chains starting from automation

POST /api/visualautoview/trace-entity-flow
  → Trace flow of entity through automations
  Params: { entity_id, automation_id }
```

### Frontend Components

**Primary Component:** `entity-relationship-view.ts`

```typescript
@customElement('entity-relationship-view')
export class EntityRelationshipView extends LitElement {
  @property() relationshipData?: RelationshipGraph;
  @property() selectedEntity?: string;
  @property() selectedAutomation?: string;
  
  // Multi-view support
  private currentView: 'graph' | 'table' | 'flow' = 'graph';
  
  // Event handlers
  onEntitySelect(entityId: string): void
  onAutomationSelect(automationId: string): void
  onCascadeSelected(chain: string[]): void
  
  // Visualization methods
  renderRelationshipGraph(): void
  renderEntityTable(): void
  renderFlowDiagram(): void
  
  // Analytics
  displayCriticalEntities(): void
  displayCascadeChains(): void
  showEntityImpact(entityId: string): void
}
```

### User Interface Flow

1. User opens automation editor and selects "Entity Relationships"
2. Service fetches all entities involved in automation
3. Frontend displays relationship graph with:
   - **Entities** as colored nodes (by type)
   - **Automations** as workflow nodes
   - **Relationships** as directed edges (with types)
4. User can:
   - Click entity to see all automations it triggers/affects
   - Click automation to see all entities it uses
   - View cascade chains (automation A triggers → entity → automation B)
   - Identify critical entities (affecting multiple automations)

### Performance Optimization

- **Caching:** Cache relationship graphs (5-min TTL)
- **Lazy Loading:** Load cascade data on demand
- **Indexing:** Index automations by entity dependencies
- **Batching:** Combine multiple entity lookups

---

## Feature 2: Dependency Graph

### Purpose & Use Cases

**Primary Purpose:** Visualize automation chains where one automation triggers another (either directly or through shared entities), showing cascading effects and dependencies.

**User Scenarios:**
- See automation chains (A → B → C)
- Identify automation loops/deadlocks
- Understand execution order
- Plan automation modifications (what breaks if I change this?)
- Optimize execution flow
- Detect race conditions

### Architecture Design

```
Dependency Graph
│
├── Direct Dependencies
│   ├── Automation A action triggers state that triggers Automation B
│   ├── Service call in A triggers entity causing B
│   └── Scene/Script call in A
│
├── Indirect Dependencies
│   ├── Through shared condition entity
│   ├── Through data template variables
│   └── Through intermediate automations
│
├── Circular Dependencies
│   ├── Loop detection
│   ├── Loop severity analysis
│   └── Prevention recommendations
│
├── Dependency Chain Analysis
│   ├── Critical path identification
│   ├── Parallel execution paths
│   └── Sequential dependency chains
│
└── Chain Optimization
    ├── Unnecessary intermediate steps
    ├── Consolidation opportunities
    └── Performance improvement suggestions
```

### Data Models

```python
@dataclass
class DependencyRelation:
    """Represents dependency between two automations."""
    
    source_automation_id: str
    target_automation_id: str
    source_alias: str
    target_alias: str
    
    dependency_type: Literal[
        'direct_trigger',       # Source action directly triggers target
        'entity_trigger',       # Source changes entity that triggers target
        'shared_entity',        # Both use same entity (indirect)
        'shared_condition',     # Both check same entity state
        'service_dependency',   # Both call same service
        'potential',            # Could trigger under certain conditions
    ]
    
    # Relationship properties
    is_required: bool  # Must happen before target
    likelihood: float  # Probability of triggering (0.0-1.0)
    delay: int | None  # Milliseconds between trigger and effect
    
    # Potential issues
    has_circular_dependency: bool
    could_cause_race_condition: bool
    could_cause_loop: bool

@dataclass
class DependencyChain:
    """A sequence of dependent automations."""
    
    automations: list[str]  # automation IDs in order
    aliases: list[str]      # automation aliases
    
    # Chain properties
    total_estimated_duration: int  # Total execution time (ms)
    is_circular: bool
    is_optimal: bool
    
    # Risk assessment
    risk_level: Literal['low', 'medium', 'high']
    potential_issues: list[str]
    optimization_suggestions: list[str]

@dataclass
class DependencyGraph:
    """Complete dependency graph of all automations."""
    
    nodes: list[str]  # automation IDs
    edges: list[DependencyRelation]
    
    # Derived data
    chains: list[DependencyChain]
    circular_dependencies: list[DependencyChain]
    
    # Statistics
    total_automations: int
    total_dependencies: int
    avg_chain_length: float
    has_circular_deps: bool
    critical_path_length: int
```

### Service Implementation Structure

```python
class DependencyGraphService:
    """Service for analyzing automation dependencies."""
    
    def __init__(self, hass: HomeAssistant, 
                 entity_service: EntityRelationshipService):
        """Initialize the service."""
        self.hass = hass
        self.entity_service = entity_service
        self._dependency_cache: DependencyGraph | None = None
    
    async def build_dependency_graph(self) -> DependencyGraph:
        """Build complete dependency graph for all automations."""
    
    async def find_chains(self) -> list[DependencyChain]:
        """Find all automation chains in the system."""
    
    async def detect_circular_dependencies(
        self
    ) -> list[DependencyChain]:
        """Detect circular automation dependencies."""
    
    async def analyze_automation_impact(
        self,
        automation_id: str
    ) -> dict[str, Any]:
        """Analyze cascading impact of one automation."""
    
    async def find_optimization_opportunities(
        self
    ) -> list[dict[str, Any]]:
        """Find consolidation and optimization suggestions."""
    
    def calculate_chain_risk(
        self,
        chain: DependencyChain
    ) -> dict[str, Any]:
        """Assess risk level of automation chain."""
    
    async def simulate_execution_order(
        self,
        trigger_automation_id: str
    ) -> list[dict[str, Any]]:
        """Simulate execution order of dependent automations."""
```

### API Endpoints

```
GET /api/visualautoview/dependency-graph
  → Complete dependency graph for all automations

GET /api/visualautoview/dependency-graph/{automation_id}
  → Dependencies for single automation (upstream and downstream)

GET /api/visualautoview/automation-chains
  → All detected automation chains

GET /api/visualautoview/circular-dependencies
  → Detect circular dependency issues

GET /api/visualautoview/execution-order/{automation_id}
  → Simulated execution order starting from automation

POST /api/visualautoview/analyze-impact
  → Analyze cascading impact
  Params: { automation_id }
```

### Frontend Components

**Primary Component:** `dependency-graph-view.ts`

```typescript
@customElement('dependency-graph-view')
export class DependencyGraphView extends LitElement {
  @property() graphData?: DependencyGraph;
  @property() selectedChain?: DependencyChain;
  
  private viewMode: 'graph' | 'chains' | 'risks' = 'graph';
  
  renderDependencyGraph(): void
  renderChainList(): void
  renderRiskAnalysis(): void
  
  highlightChain(chain: DependencyChain): void
  showCircularDependencies(): void
  displayOptimizationSuggestions(): void
  
  onAutomationHover(automationId: string): void
  onChainClick(chain: DependencyChain): void
}
```

### User Interface Flow

1. User navigates to "Dependency Graph" view
2. System analyzes all automation dependencies
3. Frontend displays:
   - **Graph view:** Automations as nodes, dependencies as edges
   - **Chain view:** Detected automation chains
   - **Risk view:** Circular dependencies and issues
4. User can:
   - Click automation to see upstream/downstream effects
   - View optimization suggestions
   - Identify and fix circular dependencies
   - Understand execution order

---

## Feature 3: Execution Path Highlighting

### Purpose & Use Cases

**Primary Purpose:** Show which automation triggered, what conditions were evaluated, and which actions executed in the last run (or real-time).

**User Scenarios:**
- Debug why automation didn't execute (condition failed)
- Trace execution flow through complex conditions
- Understand which actions actually ran
- Verify condition logic is correct
- See real-time execution as it happens
- Identify performance bottlenecks

### Architecture Design

```
Execution Path Highlighting
│
├── Execution Tracking
│   ├── Trigger Detection
│   ├── Condition Evaluation (pass/fail)
│   ├── Action Execution (success/failure)
│   └── Timing Information
│
├── Path Visualization
│   ├── Highlight nodes that executed
│   ├── Show condition evaluation (green=pass, red=fail)
│   ├── Shade by execution order
│   └── Color by success/failure
│
├── Execution History
│   ├── Last N executions
│   ├── Execution timeline
│   ├── Performance analysis
│   └── Error/failure analysis
│
├── Real-Time Monitoring
│   ├── WebSocket updates on trigger
│   ├── Live condition evaluation
│   ├── Action execution streaming
│   └── Performance metrics collection
│
└── Debugging Features
    ├── Breakpoint support
    ├── Variable inspection
    ├── Template evaluation preview
    └── Error message details
```

### Data Models

```python
@dataclass
class ConditionEvaluation:
    """Result of condition evaluation."""
    
    condition_id: str
    condition_label: str
    
    # Evaluation result
    result: bool  # True if condition passed
    start_time: datetime
    end_time: datetime
    duration_ms: int
    
    # Details
    condition_type: str
    condition_data: dict[str, Any]
    
    # Error tracking
    error: str | None = None
    warning: str | None = None
    
    # Template info
    template_evaluated: bool
    template_variables: dict[str, Any] | None = None

@dataclass
class ActionExecution:
    """Record of action execution."""
    
    action_id: str
    action_label: str
    
    # Execution info
    sequence_number: int
    start_time: datetime
    end_time: datetime
    duration_ms: int
    
    # Action details
    action_type: str  # 'service_call', 'delay', 'choose', etc.
    service: str | None
    target: dict[str, Any] | None
    
    # Result
    status: Literal['success', 'failed', 'skipped', 'running']
    result_data: dict[str, Any]
    error: str | None = None

@dataclass
class ExecutionPath:
    """Complete record of single automation execution."""
    
    execution_id: str
    automation_id: str
    automation_alias: str
    
    # Trigger info
    trigger_time: datetime
    trigger_entity: str | None
    trigger_platform: str
    trigger_data: dict[str, Any]
    
    # Execution flow
    condition_evaluations: list[ConditionEvaluation]
    actions_executed: list[ActionExecution]
    
    # Overall metrics
    start_time: datetime
    end_time: datetime
    total_duration_ms: int
    
    # Results
    execution_result: Literal['success', 'failed', 'stopped']
    executed_actions_count: int
    skipped_actions_count: int
    failed_actions_count: int
    
    # Error info
    error_message: str | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)
    
    # Context
    variables: dict[str, Any]  # Local variables during execution
    context_user_id: str | None = None
    context_automation_id: str | None = None

@dataclass
class ExecutionHistory:
    """History of automation executions."""
    
    automation_id: str
    executions: list[ExecutionPath]
    
    # Statistics
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    
    avg_duration_ms: int
    min_duration_ms: int
    max_duration_ms: int
    
    # Last execution
    last_execution: ExecutionPath | None
    last_triggered: datetime | None
    
    # Common errors
    common_failures: dict[str, int]  # error_message -> count
```

### Service Implementation Structure

```python
class ExecutionPathService:
    """Service for tracking and displaying automation execution paths."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the service."""
        self.hass = hass
        self._execution_history: dict[str, list[ExecutionPath]] = {}
        self._max_history_per_automation = 50  # Keep last 50 executions
    
    async def on_automation_triggered(
        self,
        automation_id: str,
        trigger_data: dict[str, Any]
    ) -> None:
        """Called when automation is triggered."""
    
    async def on_condition_evaluated(
        self,
        automation_id: str,
        execution_id: str,
        condition: ConditionEvaluation
    ) -> None:
        """Called when condition is evaluated."""
    
    async def on_action_executed(
        self,
        automation_id: str,
        execution_id: str,
        action: ActionExecution
    ) -> None:
        """Called when action completes."""
    
    async def on_automation_completed(
        self,
        automation_id: str,
        execution_id: str,
        result: dict[str, Any]
    ) -> None:
        """Called when automation execution completes."""
    
    async def get_execution_history(
        self,
        automation_id: str,
        limit: int = 20
    ) -> ExecutionHistory:
        """Get execution history for automation."""
    
    async def get_last_execution(
        self,
        automation_id: str
    ) -> ExecutionPath | None:
        """Get last execution details."""
    
    async def subscribe_execution_updates(
        self,
        automation_id: str,
        callback: Callable[[dict[str, Any]], None]
    ) -> Callable[[], None]:
        """Subscribe to real-time execution updates."""
    
    def analyze_failures(
        self,
        automation_id: str
    ) -> dict[str, Any]:
        """Analyze common failure patterns."""
```

### WebSocket Commands

```
# Subscribe to execution updates
visualautoview/subscribe_executions
  Params: { automation_id: str }
  
# Get execution history
visualautoview/get_execution_history
  Params: { automation_id: str, limit: int = 20 }
  
# Get current execution state
visualautoview/get_current_execution
  Params: { automation_id: str }
```

### Frontend Components

**Primary Component:** `execution-path-view.ts`

```typescript
@customElement('execution-path-view')
export class ExecutionPathView extends LitElement {
  @property() automationId?: string;
  @property() executionPath?: ExecutionPath;
  @property() executionHistory?: ExecutionHistory;
  
  private subscriptionId?: string;
  private isMonitoring = false;
  
  // Views
  private currentView: 'current' | 'timeline' | 'history' = 'current';
  
  renderCurrentExecution(): void
  renderExecutionTimeline(): void
  renderExecutionHistory(): void
  
  highlightExecutedPath(): void
  showConditionResults(): void
  showActionResults(): void
  
  startRealTimeMonitoring(): void
  stopRealTimeMonitoring(): void
  
  onExecutionUpdate(update: any): void
}
```

### User Interface Flow

1. User opens automation and selects "Execution History"
2. System shows last execution with:
   - **Green highlights:** Conditions that passed
   - **Red highlights:** Conditions that failed
   - **Gray shades:** Actions in execution order
   - **Timing info:** Duration of each step
3. User can:
   - Click condition to see why it passed/failed
   - Click action to see result and any errors
   - View execution timeline with durations
   - Enable real-time monitoring of next execution
   - Browse historical executions

---

## Feature 4: Performance Metrics

### Purpose & Use Cases

**Primary Purpose:** Display execution time, frequency, triggering patterns, and other performance data to help users understand automation behavior and optimize performance.

**User Scenarios:**
- Monitor execution frequency
- Track execution time trends
- Identify slow automations
- Find most frequently triggered automations
- Detect patterns (time of day, day of week)
- Plan optimization strategies
- Set up performance alerts

### Architecture Design

```
Performance Metrics
│
├── Execution Metrics
│   ├── Execution count (lifetime, today, this week)
│   ├── Execution duration (min, max, average, median)
│   ├── Success rate / failure rate
│   └── Error frequency
│
├── Temporal Patterns
│   ├── Execution frequency timeline
│   ├── Time of day patterns
│   ├── Day of week patterns
│   ├── Seasonal patterns
│   └── Trend analysis
│
├── Performance Analysis
│   ├── Slowest automations
│   ├── Most frequent triggers
│   ├── Peak load times
│   ├── Resource usage estimation
│   └── Bottleneck identification
│
├── Reliability Metrics
│   ├── Success/failure rate
│   ├── Common error types
│   ├── Error frequency trends
│   └── Recovery patterns
│
└── Comparison & Benchmarking
    ├── Compare against similar automations
    ├── Deviation from baseline
    ├── Performance ranking
    └── Optimization recommendations
```

### Data Models

```python
@dataclass
class ExecutionMetrics:
    """Metrics for automation executions."""
    
    automation_id: str
    
    # Count metrics
    total_executions: int
    successful_executions: int
    failed_executions: int
    skipped_executions: int
    
    # Success rate
    success_rate: float  # 0.0-1.0
    failure_rate: float
    
    # Duration metrics
    min_duration_ms: int
    max_duration_ms: int
    avg_duration_ms: float
    median_duration_ms: int
    p95_duration_ms: int  # 95th percentile
    p99_duration_ms: int  # 99th percentile
    
    # Failure metrics
    common_errors: dict[str, int]  # error_type -> count
    last_error: str | None
    last_error_time: datetime | None

@dataclass
class TemporalPattern:
    """Pattern of automation triggering over time."""
    
    pattern_type: Literal['hourly', 'daily', 'weekly', 'monthly']
    
    # Pattern data
    data: dict[str, float]  # time_period -> execution_count
    peak_time: str
    peak_count: int
    
    # Metrics
    average_per_period: float
    std_deviation: float
    trend: Literal['increasing', 'decreasing', 'stable']

@dataclass
class PerformanceMetricsReport:
    """Complete performance report for single automation."""
    
    automation_id: str
    automation_alias: str
    
    # Execution metrics
    metrics: ExecutionMetrics
    
    # Temporal patterns
    hourly_pattern: TemporalPattern
    daily_pattern: TemporalPattern
    weekly_pattern: TemporalPattern
    
    # Analysis
    is_high_frequency: bool  # Executes frequently
    is_slow: bool  # Takes longer than average
    is_unreliable: bool  # High failure rate
    
    # Recommendations
    optimization_suggestions: list[str]
    
    # Comparison
    performance_rank: int  # Percentile (1-100)
    comparison_group: str  # Similar automations
    above_average: bool
    
    # Time periods
    period_start: datetime
    period_end: datetime
    period_label: str  # e.g., "Last 30 days"

@dataclass
class SystemPerformanceMetrics:
    """System-wide performance metrics."""
    
    # Overall stats
    total_automations: int
    active_automations: int  # With executions in period
    total_executions: int
    total_failed_executions: int
    
    # Timing stats
    avg_execution_time_ms: float
    total_execution_time_ms: int
    peak_concurrent_executions: int
    
    # Reliability stats
    overall_success_rate: float
    most_common_error: str | None
    
    # Top performers
    slowest_automations: list[tuple[str, int]]  # (automation_id, duration_ms)
    most_frequent_automations: list[tuple[str, int]]  # (automation_id, count)
    most_failing_automations: list[tuple[str, float]]  # (automation_id, failure_rate)
    
    # Trends
    execution_trend: Literal['increasing', 'decreasing', 'stable']
    error_trend: Literal['improving', 'worsening', 'stable']
    
    period_start: datetime
    period_end: datetime
```

### Service Implementation Structure

```python
class PerformanceMetricsService:
    """Service for tracking and analyzing automation performance metrics."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the service."""
        self.hass = hass
        self._metrics_storage: dict[str, ExecutionMetrics] = {}
        self._pattern_analysis: dict[str, list[TemporalPattern]] = {}
    
    async def record_execution(
        self,
        automation_id: str,
        duration_ms: int,
        success: bool,
        error: str | None = None
    ) -> None:
        """Record execution metrics."""
    
    async def get_execution_metrics(
        self,
        automation_id: str,
        period: Literal['day', 'week', 'month', '30days', 'year'] = '30days'
    ) -> ExecutionMetrics:
        """Get execution metrics for specific automation."""
    
    async def analyze_temporal_patterns(
        self,
        automation_id: str,
        period: Literal['day', 'week', 'month'] = 'month'
    ) -> list[TemporalPattern]:
        """Analyze temporal patterns of automation."""
    
    async def get_performance_report(
        self,
        automation_id: str
    ) -> PerformanceMetricsReport:
        """Get comprehensive performance report."""
    
    async def get_system_metrics(
        self
    ) -> SystemPerformanceMetrics:
        """Get system-wide performance metrics."""
    
    async def identify_optimization_opportunities(
        self,
        automation_id: str
    ) -> list[str]:
        """Generate optimization suggestions."""
    
    def calculate_performance_rank(
        self,
        automation_id: str,
        metric: Literal['speed', 'frequency', 'reliability']
    ) -> int:
        """Calculate performance percentile (0-100)."""
    
    async def export_metrics(
        self,
        automation_ids: list[str],
        format: Literal['csv', 'json', 'pdf'] = 'json'
    ) -> bytes:
        """Export metrics in specified format."""
```

### API Endpoints

```
GET /api/visualautoview/metrics/{automation_id}
  → Execution metrics for specific automation
  Params: { period: 'day'|'week'|'month'|'30days'|'year' }

GET /api/visualautoview/metrics/{automation_id}/report
  → Complete performance report

GET /api/visualautoview/metrics/system/overview
  → System-wide performance metrics

GET /api/visualautoview/metrics/{automation_id}/patterns
  → Temporal patterns (hourly, daily, weekly)

GET /api/visualautoview/metrics/top
  → Top automations by various metrics
  Params: { metric: 'slowest'|'frequent'|'failures' }

POST /api/visualautoview/metrics/export
  → Export metrics data
  Params: { automation_ids: list[str], format: 'csv'|'json'|'pdf' }
```

### Frontend Components

**Primary Component:** `performance-metrics-view.ts`

```typescript
@customElement('performance-metrics-view')
export class PerformanceMetricsView extends LitElement {
  @property() automationId?: string;
  @property() metricsReport?: PerformanceMetricsReport;
  @property() systemMetrics?: SystemPerformanceMetrics;
  
  // View selection
  private currentView: 'dashboard' | 'details' | 'trends' | 'comparison' = 'dashboard';
  private timePeriod: 'day' | 'week' | 'month' | '30days' | 'year' = '30days';
  
  renderMetricsDashboard(): void
  renderDetailedMetrics(): void
  renderTrendsAnalysis(): void
  renderComparison(): void
  
  renderExecutionChart(metrics: ExecutionMetrics): void
  renderPatternChart(patterns: TemporalPattern[]): void
  renderTrendChart(): void
  
  onPeriodChange(period: string): void
  onExport(): void
}
```

---

## Feature 5: Template Expansion / Preview

### Purpose & Use Cases

**Primary Purpose:** Preview Jinja2 templates with current entity states, showing what values will be rendered when automation executes.

**User Scenarios:**
- Verify template syntax is correct
- Preview rendered output before automation runs
- Debug template variables and filters
- Test template with different entity states
- Understand template evaluation
- Identify missing entities or incorrect references

### Architecture Design

```
Template Expansion Service
│
├── Template Detection
│   ├── Find all templates in automation
│   ├── Extract template expressions
│   ├── Identify template variables/entities
│   └── Map to automation context
│
├── Template Evaluation
│   ├── Safe evaluation (no side effects)
│   ├── Variable substitution
│   ├── Function availability
│   ├── Error handling
│   └── Performance consideration
│
├── Context Building
│   ├── Current entity states
│   ├── Home Assistant variables
│   ├── Automation context
│   ├── User-defined variables
│   └── Time/date information
│
├── Preview Rendering
│   ├── Before/after display
│   ├── Variable inspection
│   ├── Error highlighting
│   └── Suggestion system
│
└── What-If Analysis
    ├── Simulate entity state changes
    ├── Preview different scenarios
    ├── Test conditional logic
    └── Validate templates safely
```

### Data Models

```python
@dataclass
class TemplateVariable:
    """Variable or entity used in template."""
    
    name: str
    type: Literal['entity', 'variable', 'builtin', 'function']
    
    # Current value
    current_value: Any
    value_type: str  # 'str', 'int', 'bool', 'float', etc.
    
    # Entity info (if applicable)
    entity_id: str | None = None
    entity_state: str | None = None
    entity_attributes: dict[str, Any] | None = None
    
    # Is required for template evaluation
    is_required: bool = True
    is_available: bool = True

@dataclass
class TemplateExpression:
    """Single Jinja2 template expression."""
    
    expression: str  # The template code
    location: dict[str, Any]  # Where in automation (service_param, etc.)
    
    # Variables used
    variables_required: list[str]
    
    # Current evaluation
    current_result: str  # Rendered output
    result_type: str
    is_valid: bool
    
    # Error info
    error: str | None = None
    error_type: str | None = None

@dataclass
class TemplateEvaluationContext:
    """Context for template evaluation."""
    
    # Time information
    now: datetime
    today: str
    
    # Home Assistant
    trigger_data: dict[str, Any]
    automation_context: dict[str, Any]
    
    # Entity states
    entity_states: dict[str, str]  # entity_id -> state
    entity_attributes: dict[str, dict[str, Any]]  # entity_id -> attributes
    
    # Variables
    variables: dict[str, Any]
    
    # Functions available
    available_functions: list[str]

@dataclass
class TemplatePreview:
    """Preview of template expansion."""
    
    automation_id: str
    automation_alias: str
    
    # All templates found
    expressions: list[TemplateExpression]
    variables: list[TemplateVariable]
    
    # Context
    evaluation_context: TemplateEvaluationContext
    
    # Summary
    total_expressions: int
    valid_expressions: int
    invalid_expressions: int
    missing_variables: list[str]
    
    # Errors
    errors: list[dict[str, str]]
    warnings: list[dict[str, str]]
    
    # Last evaluated
    evaluated_at: datetime
    evaluation_time_ms: float

@dataclass
class TemplateScenario:
    """What-if scenario for template testing."""
    
    scenario_name: str
    description: str
    
    # Modified entity states
    modified_entities: dict[str, str]  # entity_id -> new_state
    
    # Modified variables
    modified_variables: dict[str, Any]
    
    # Trigger data
    trigger_data: dict[str, Any]
    
    # Evaluated result
    template_results: list[TemplateExpression]
    evaluation_time_ms: float
```

### Service Implementation Structure

```python
class TemplateExpansionService:
    """Service for template expansion and preview."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the service."""
        self.hass = hass
        self._template_cache: dict[str, list[TemplateExpression]] = {}
        self._jinja_env = self._setup_jinja_environment()
    
    def _setup_jinja_environment(self) -> Any:
        """Set up Jinja2 environment with HA functions."""
    
    async def find_templates_in_automation(
        self,
        automation_config: dict[str, Any]
    ) -> list[TemplateExpression]:
        """Find all template expressions in automation."""
    
    async def get_template_variables(
        self,
        automation_id: str
    ) -> list[TemplateVariable]:
        """Get all variables/entities used in templates."""
    
    async def evaluate_template(
        self,
        template_expression: str,
        context: TemplateEvaluationContext | None = None
    ) -> dict[str, Any]:
        """Safely evaluate a single template expression."""
    
    async def preview_templates(
        self,
        automation_id: str
    ) -> TemplatePreview:
        """Get preview of all templates in automation."""
    
    async def build_evaluation_context(
        self,
        automation_id: str
    ) -> TemplateEvaluationContext:
        """Build current evaluation context."""
    
    async def test_scenario(
        self,
        automation_id: str,
        scenario: TemplateScenario
    ) -> TemplatePreview:
        """Evaluate templates with modified entity states."""
    
    async def validate_templates(
        self,
        automation_id: str
    ) -> dict[str, Any]:
        """Validate all templates for syntax errors."""
    
    def get_available_functions(self) -> list[str]:
        """List available Jinja2 functions."""
    
    def get_template_suggestions(
        self,
        partial_expression: str
    ) -> list[str]:
        """Get auto-complete suggestions for template."""
```

### API Endpoints

```
GET /api/visualautoview/templates/{automation_id}
  → Find all templates in automation

GET /api/visualautoview/templates/{automation_id}/preview
  → Preview expanded templates with current values

GET /api/visualautoview/templates/{automation_id}/variables
  → Get all variables/entities used in templates

POST /api/visualautoview/templates/{automation_id}/evaluate
  → Evaluate specific template expression
  Params: { expression: str }

POST /api/visualautoview/templates/{automation_id}/scenario
  → Test template with what-if scenario
  Params: { scenario: TemplateScenario }

GET /api/visualautoview/templates/functions
  → List available Jinja2 functions

GET /api/visualautoview/templates/validate/{automation_id}
  → Validate all templates for errors
```

### Frontend Components

**Primary Component:** `template-preview-panel.ts`

```typescript
@customElement('template-preview-panel')
export class TemplatePreviewPanel extends LitElement {
  @property() automationId?: string;
  @property() templatePreview?: TemplatePreview;
  
  private currentView: 'preview' | 'variables' | 'scenarios' = 'preview';
  private selectedScenario?: string;
  
  // Editor
  private templateEditor?: CodeEditorElement;
  
  renderPreview(): void
  renderVariables(): void
  renderScenarios(): void
  
  renderTemplateExpression(expr: TemplateExpression): void
  renderVariableInspector(variable: TemplateVariable): void
  
  onExpressionClick(expr: TemplateExpression): void
  onEditTemplate(expr: TemplateExpression): void
  onTestScenario(scenario: TemplateScenario): void
  
  createScenario(): void
  deleteScenario(name: string): void
}
```

---

## Implementation Architecture Overview

### Integration Points

All Phase 3 services integrate with Phase 1 and Phase 2:

```
Phase 1: Graph Parser + Visualization
    ↓ (uses)
Phase 2: Dashboard, Search, Export, Themes
    ↓ (uses)
Phase 3: Advanced Analysis
    ├── Entity Relationship View
    ├── Dependency Graph
    ├── Execution Path Highlighting
    ├── Performance Metrics
    └── Template Expansion
```

### Backend Service Architecture

```python
# In custom_components/visualautoview/__init__.py

from .services import (
    EntityRelationshipService,
    DependencyGraphService,
    ExecutionPathService,
    PerformanceMetricsService,
    TemplateExpansionService,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Phase 3 services."""
    
    # Initialize services
    entity_service = EntityRelationshipService(hass)
    dependency_service = DependencyGraphService(hass, entity_service)
    execution_service = ExecutionPathService(hass)
    metrics_service = PerformanceMetricsService(hass)
    template_service = TemplateExpansionService(hass)
    
    # Store in hass.data
    hass.data[DOMAIN]['services'] = {
        'entity_relationships': entity_service,
        'dependencies': dependency_service,
        'execution': execution_service,
        'metrics': metrics_service,
        'templates': template_service,
    }
    
    # Register API endpoints
    await _register_phase3_endpoints(hass)
    
    # Set up WebSocket handlers
    await _setup_websocket_handlers(hass)
    
    # Set up execution tracking
    await _setup_execution_tracking(hass, execution_service, metrics_service)
    
    return True
```

### Frontend Architecture

```
Frontend Structure:
├── Views
│   ├── entity-relationship-view.ts
│   ├── dependency-graph-view.ts
│   ├── execution-path-view.ts
│   ├── performance-metrics-view.ts
│   └── template-preview-panel.ts
│
├── Components
│   ├── charts/ (Chart.js/Plotly for visualizations)
│   ├── graphs/ (vis-network extensions)
│   ├── tables/ (Data tables for metrics)
│   └── modals/ (Dialog components)
│
├── Services
│   ├── api.ts (API communication)
│   ├── websocket.ts (Real-time updates)
│   └── data-transforms.ts (Data processing)
│
└── Utils
    ├── formatting.ts
    ├── calculations.ts
    └── constants.ts
```

---

## Development Timeline

### Phase 3 Development Breakdown

| Feature | Hours | Dependencies | Priority |
|---------|-------|--------------|----------|
| Entity Relationship View | 8-10 | GraphParser, Phase2 | High |
| Dependency Graph | 8-10 | Entity Relationships | High |
| Execution Path Tracking | 10-12 | Integration hooks | Critical |
| Performance Metrics | 8-10 | Execution tracking | High |
| Template Expansion | 8-10 | Graph Parser | Medium |
| **Frontend Components** | 15-20 | All backends | High |
| Testing & Documentation | 8-10 | All services | High |
| **Total** | **55-72 hours** | - | - |

### Recommended Execution Order

1. **Week 1: Foundation Services**
   - Entity Relationship Service (8-10h)
   - Execution Path Service setup (6-8h)

2. **Week 2: Analysis Services**
   - Dependency Graph Service (8-10h)
   - Performance Metrics Service (8-10h)

3. **Week 3: Advanced Features**
   - Template Expansion Service (8-10h)
   - Frontend components (10-12h)

4. **Week 4: Integration & Polish**
   - API endpoint registration (4-6h)
   - WebSocket handlers (4-6h)
   - Frontend integration (6-8h)
   - Testing & documentation (8-10h)

---

## File Structure (Phase 3)

```
custom_components/visualautoview/
├── services/
│   ├── __init__.py
│   ├── entity_relationship_service.py    (NEW)
│   ├── dependency_graph_service.py       (NEW)
│   ├── execution_path_service.py         (NEW)
│   ├── performance_metrics_service.py    (NEW)
│   └── template_expansion_service.py     (NEW)
│
├── api/
│   ├── __init__.py
│   ├── entity_relationship_api.py        (NEW)
│   ├── dependency_graph_api.py           (NEW)
│   ├── execution_path_api.py             (NEW)
│   ├── performance_metrics_api.py        (NEW)
│   └── template_expansion_api.py         (NEW)
│
├── __init__.py (modified)
├── const.py (modified for new constants)
└── graph_parser.py (existing)

Feature_EntityRelationships/
├── README.md
└── src/
    └── entity_relationship_service.py (alternate location)

Feature_DependencyGraph/
├── README.md
└── src/
    └── dependency_graph_service.py

Feature_ExecutionPathHighlighting/
├── README.md
└── src/
    └── execution_path_service.py

Feature_PerformanceMetrics/
├── README.md
└── src/
    └── performance_metrics_service.py

Feature_TemplateExpansion/
├── README.md
└── src/
    └── template_expansion_service.py

frontend/src/
├── phase3/
│   ├── entity-relationship-view.ts
│   ├── dependency-graph-view.ts
│   ├── execution-path-view.ts
│   ├── performance-metrics-view.ts
│   ├── template-preview-panel.ts
│   └── phase3-types.ts
│
└── (integrate with existing frontend)
```

---

## Success Criteria

### Phase 3 Complete When:

1. ✅ All 5 services fully implemented and tested
2. ✅ All API endpoints functional
3. ✅ Frontend components render correctly
4. ✅ Real-time execution tracking working
5. ✅ Performance metrics collecting data
6. ✅ Template preview feature functional
7. ✅ Comprehensive documentation written
8. ✅ Integration tests passing (>90% coverage)
9. ✅ No critical bugs
10. ✅ Performance targets met:
    - Entity relationships: < 200ms for 50 automations
    - Dependency graph: < 300ms for 100 automations
    - Execution tracking: < 50ms overhead per execution
    - Metrics query: < 100ms for recent data
    - Template preview: < 500ms for complex automations

---

## Next Steps

1. **Confirm Phase 3 scope** with stakeholders
2. **Create detailed service specifications** (this document is the start)
3. **Set up development environment** and branches
4. **Begin implementing services** in recommended order
5. **Create comprehensive tests** as you build
6. **Build frontend components** in parallel with services
7. **Integration testing** of all Phase 3 features
8. **Documentation** and polish

---

## Questions & Clarifications Needed

1. Should execution tracking be opt-in or automatic?
2. How much historical data should be retained?
3. What's the acceptable overhead for real-time tracking?
4. Should template expansion include custom functions?
5. UI preference for metrics (graphs, tables, both)?
6. Should performance alerts be configurable?

---

**Document Version:** 1.0  
**Status:** Ready for Development  
**Created:** December 17, 2025  
**Next Review:** After Phase 3 Feature 1 completion
