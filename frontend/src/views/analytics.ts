/**
 * Analytics Panel Component
 * Displays performance metrics, dependency analysis, and entity relationships
 */

import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { VisualAutoViewApi } from '../services/api';

interface PerformanceMetric {
  automation_id: string;
  avg_execution_time: number;
  min_execution_time: number;
  max_execution_time: number;
  total_executions: number;
  success_rate: number;
}

interface DependencyInfo {
  automation_id: string;
  dependent_automations: string[];
  circular_dependencies: boolean;
  chain_depth: number;
}

interface EntityRelationship {
  entity_id: string;
  related_automations: string[];
  relationship_strength: number;
}

@customElement('vav-analytics')
export class AnalyticsPanel extends LitElement {
  @property({ attribute: false }) hass: any; // Home Assistant object
  @property({ type: String }) selectedAutomation = '';
  @state() activeTab = 'performance';
  @state() performanceMetrics: PerformanceMetric | null = null;
  @state() dependencyInfo: DependencyInfo | null = null;
  @state() entityRelationships: EntityRelationship[] = [];
  @state() loading = false;
  @state() error: string | null = null;

  private api: VisualAutoViewApi | null = null;

  static styles = css`
    :host {
      display: block;
      background: var(--primary-background-color);
      color: var(--primary-text-color);
      font-family: var(--paper-font-body1_-_font-family);
    }

    .container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    .tabs {
      display: flex;
      gap: 0;
      border-bottom: 2px solid var(--divider-color);
      background: var(--card-background-color);
    }

    .tab-button {
      padding: 12px 16px;
      background: transparent;
      border: none;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
      border-bottom: 3px solid transparent;
      transition: all 0.2s ease;
      position: relative;
      bottom: -2px;
    }

    .tab-button:hover {
      color: var(--primary-text-color);
      background: var(--secondary-background-color);
    }

    .tab-button.active {
      color: var(--primary-color);
      border-bottom-color: var(--primary-color);
    }

    .content {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    }

    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
    }

    .metric-card {
      background: var(--card-background-color);
      border: 1px solid var(--divider-color);
      border-radius: var(--ha-card-border-radius, 12px);
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
    }

    .metric-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .metric-title {
      font-weight: 600;
      font-size: 14px;
      color: var(--primary-text-color);
    }

    .metric-badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      background: var(--secondary-background-color);
      font-size: 11px;
      font-weight: 600;
    }

    .metric-badge.success {
      background: var(--success-color, #c8e6c9);
      color: var(--success-state-color, #2e7d32);
    }

    .metric-badge.warning {
      background: var(--warning-color, #fff3cd);
      color: var(--warning-state-color, #856404);
    }

    .metric-badge.danger {
      background: var(--error-color, #f8d7da);
      color: var(--error-state-color, #721c24);
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 12px;
    }

    .metric-item {
      background: var(--secondary-background-color);
      padding: 12px;
      border-radius: 4px;
      text-align: center;
    }

    .metric-value {
      font-size: 20px;
      font-weight: 700;
      color: var(--primary-color, #2196F3);
    }

    .metric-label {
      font-size: 11px;
      color: var(--secondary-text, #999);
      text-transform: uppercase;
      margin-top: 4px;
    }

    .chart-container {
      background: white;
      border: 1px solid var(--divider-color, #e0e0e0);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
      min-height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--secondary-text, #999);
    }

    .list-item {
      padding: 10px;
      background: white;
      border: 1px solid var(--divider-color, #e0e0e0);
      border-radius: 4px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .list-item-label {
      flex: 1;
      font-size: 13px;
    }

    .list-item-value {
      font-weight: 600;
      color: var(--primary-color, #2196F3);
      font-size: 12px;
    }

    .warning-item {
      background: #fffbea;
      border-left: 4px solid #ffa500;
    }

    .danger-item {
      background: #ffe0e0;
      border-left: 4px solid #ff0000;
    }

    .success-item {
      background: #e8f5e9;
      border-left: 4px solid #4caf50;
    }

    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 200px;
      color: var(--secondary-text, #999);
    }

    .spinner {
      display: inline-block;
      width: 24px;
      height: 24px;
      border: 3px solid var(--divider-color, #ddd);
      border-top-color: var(--primary-color, #2196F3);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }

    .error {
      padding: 12px;
      background: #ffebee;
      color: #c62828;
      border-radius: 4px;
      font-size: 13px;
    }

    .empty-state {
      text-align: center;
      padding: 40px 20px;
      color: var(--secondary-text, #999);
    }

    .progress-bar {
      height: 8px;
      background: var(--divider-color, #e0e0e0);
      border-radius: 4px;
      overflow: hidden;
      margin-top: 8px;
    }

    .progress-fill {
      height: 100%;
      background: var(--primary-color, #2196F3);
      transition: width 0.3s ease;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.api = new VisualAutoViewApi();
    this.loadAnalytics();
  }

  updated(changedProperties: Map<string, any>) {
    if (changedProperties.has('selectedAutomation')) {
      this.loadAnalytics();
    }
  }

  render() {
    return html`
      <div class="container">
        <div class="tabs">
          <button
            class="tab-button ${this.activeTab === 'performance' ? 'active' : ''}"
            @click=${() => this.switchTab('performance')}
          >
            Performance
          </button>
          <button
            class="tab-button ${this.activeTab === 'dependencies' ? 'active' : ''}"
            @click=${() => this.switchTab('dependencies')}
          >
            Dependencies
          </button>
          <button
            class="tab-button ${this.activeTab === 'entities' ? 'active' : ''}"
            @click=${() => this.switchTab('entities')}
          >
            Entities
          </button>
        </div>

        <div class="content">
          ${this.error ? html` <div class="error">${this.error}</div> ` : ''}

          <!-- Performance Tab -->
          <div class="tab-content ${this.activeTab === 'performance' ? 'active' : ''}">
            ${this.renderPerformanceTab()}
          </div>

          <!-- Dependencies Tab -->
          <div class="tab-content ${this.activeTab === 'dependencies' ? 'active' : ''}">
            ${this.renderDependenciesTab()}
          </div>

          <!-- Entities Tab -->
          <div class="tab-content ${this.activeTab === 'entities' ? 'active' : ''}">
            ${this.renderEntitiesTab()}
          </div>
        </div>
      </div>
    `;
  }

  private renderPerformanceTab() {
    if (this.loading) {
      return html`
        <div class="loading">
          <div class="spinner"></div>
        </div>
      `;
    }

    if (!this.performanceMetrics) {
      return html`
        <div class="empty-state">
          ${this.selectedAutomation ? 'Loading performance metrics...' : 'System-wide performance data'}
        </div>
      `;
    }

    const metrics = this.performanceMetrics;
    const isSlowRate = metrics.avg_execution_time > 5000;
    const isUnreliable = metrics.success_rate < 90;

    return html`
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Execution Time</span>
          <span class="metric-badge ${isSlowRate ? 'warning' : 'success'}">
            ${isSlowRate ? 'Slow' : 'Optimal'}
          </span>
        </div>
        <div class="metric-grid">
          <div class="metric-item">
            <div class="metric-value">${Math.round(metrics.avg_execution_time)}ms</div>
            <div class="metric-label">Average</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">${Math.round(metrics.min_execution_time)}ms</div>
            <div class="metric-label">Minimum</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">${Math.round(metrics.max_execution_time)}ms</div>
            <div class="metric-label">Maximum</div>
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Reliability</span>
          <span class="metric-badge ${isUnreliable ? 'warning' : 'success'}">
            ${isUnreliable ? 'Needs Attention' : 'Reliable'}
          </span>
        </div>
        <div class="metric-grid">
          <div class="metric-item">
            <div class="metric-value">${metrics.total_executions}</div>
            <div class="metric-label">Total Runs</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">${Math.round(metrics.success_rate)}%</div>
            <div class="metric-label">Success Rate</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">${Math.round(100 - metrics.success_rate)}%</div>
            <div class="metric-label">Failure Rate</div>
          </div>
        </div>
        <div style="margin-top: 12px;">
          <div style="font-size: 12px; color: var(--secondary-text, #666); margin-bottom: 4px;">
            Success Rate Progress
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${metrics.success_rate}%"></div>
          </div>
        </div>
      </div>

      <div class="chart-container">
        📊 Performance Timeline (Chart Component)
      </div>
    `;
  }

  private renderDependenciesTab() {
    if (this.loading) {
      return html`
        <div class="loading">
          <div class="spinner"></div>
        </div>
      `;
    }

    if (!this.dependencyInfo) {
      return html`
        <div class="empty-state">
          ${this.selectedAutomation ? 'No dependency information found' : 'Loading system dependencies...'}
        </div>
      `;
    }

    const deps = this.dependencyInfo;

    return html`
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Dependency Status</span>
          <span class="metric-badge ${deps.circular_dependencies ? 'danger' : 'success'}">
            ${deps.circular_dependencies ? 'Circular Detected' : 'No Cycles'}
          </span>
        </div>
        <div class="metric-grid">
          <div class="metric-item">
            <div class="metric-value">${deps.dependent_automations.length}</div>
            <div class="metric-label">Dependencies</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">${deps.chain_depth}</div>
            <div class="metric-label">Chain Depth</div>
          </div>
          <div class="metric-item">
            <div class="metric-value ${deps.circular_dependencies ? 'danger' : 'success'}">
              ${deps.circular_dependencies ? '⚠️' : '✓'}
            </div>
            <div class="metric-label">Status</div>
          </div>
        </div>
      </div>

      ${deps.dependent_automations.length > 0
        ? html`
            <div class="metric-card">
              <div class="metric-title" style="margin-bottom: 12px;">
                Dependent Automations
              </div>
              ${deps.dependent_automations.map(
                (auto) =>
                  html`
                    <div class="list-item">
                      <div class="list-item-label">${auto}</div>
                    </div>
                  `
              )}
            </div>
          `
        : ''}

      <div class="chart-container">
        🔗 Dependency Graph Visualization
      </div>
    `;
  }

  private renderEntitiesTab() {
    if (this.loading) {
      return html`
        <div class="loading">
          <div class="spinner"></div>
        </div>
      `;
    }

    if (this.entityRelationships.length === 0) {
      return html`
        <div class="empty-state">
          ${this.selectedAutomation ? 'No entity relationships found' : 'Loading entity relationships...'}
        </div>
      `;
    }

    return html`
      <div class="metric-card">
        <div class="metric-title" style="margin-bottom: 12px;">
          Related Entities (${this.entityRelationships.length})
        </div>
        ${this.entityRelationships.map(
          (rel) =>
            html`
              <div class="list-item">
                <div class="list-item-label">${rel.entity_id}</div>
                <div class="list-item-value">
                  ${Math.round(rel.relationship_strength * 100)}% strength
                </div>
              </div>
            `
        )}
      </div>

      <div class="metric-card">
        <div class="metric-title" style="margin-bottom: 12px;">
          Related Automations
        </div>
        ${this.entityRelationships.flatMap((rel) =>
          rel.related_automations.map(
            (auto) =>
              html`
                <div class="list-item">
                  <div class="list-item-label">${auto}</div>
                </div>
              `
          )
        )}
      </div>
    `;
  }

  private async loadAnalytics() {
    if (!this.api) return;

    this.loading = true;
    this.error = null;

    try {
      // If an automation is selected, load specific analytics
      if (this.selectedAutomation) {
        // Load performance metrics
        const perfResult = await this.api.getPerformanceMetrics(this.selectedAutomation);
        this.performanceMetrics = perfResult.data || null;

        // Load dependency info
        const depResult = await this.api.getDependencyGraph();
        const depInfo = depResult.data?.automations?.find(
          (a: any) => a.id === this.selectedAutomation
        );
        if (depInfo) {
          this.dependencyInfo = {
            automation_id: depInfo.id,
            dependent_automations: depInfo.dependencies || [],
            circular_dependencies: depInfo.has_circular || false,
            chain_depth: depInfo.depth || 0,
          };
        }

        // Load entity relationships for the specific automation
        const relResult = await this.api.getEntityRelationships(this.selectedAutomation);
        this.entityRelationships = relResult.data?.relationships || [];
      } else {
        // No automation selected - show system-wide stats
        // Load system performance
        const sysResult = await this.api.getSystemPerformance();
        if (sysResult.data) {
          // Create a summary performance metric from system data
          this.performanceMetrics = {
            automation_id: 'system',
            avg_execution_time: sysResult.data.avg_execution_time || 0,
            min_execution_time: sysResult.data.min_execution_time || 0,
            max_execution_time: sysResult.data.max_execution_time || 0,
            total_executions: sysResult.data.total_executions || 0,
            success_rate: sysResult.data.success_rate || 0,
          };
        }

        // Load overall dependency graph
        const depResult = await this.api.getDependencyGraph();
        this.dependencyInfo = {
          automation_id: 'system',
          dependent_automations: depResult.data?.automations?.map((a: any) => a.id) || [],
          circular_dependencies: depResult.data?.has_circular_dependencies || false,
          chain_depth: depResult.data?.max_chain_depth || 0,
        };

        // Load all entity relationships
        const relResult = await this.api.getEntityRelationships();
        this.entityRelationships = relResult.data?.relationships || [];
      }
    } catch (err) {
      this.error = `Failed to load analytics: ${err instanceof Error ? err.message : 'Unknown error'}`;
    } finally {
      this.loading = false;
    }
  }

  private switchTab(tab: string) {
    this.activeTab = tab;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'vav-analytics': AnalyticsPanel;
  }
}

