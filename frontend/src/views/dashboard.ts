/**
 * Dashboard View Component
 * Main panel for viewing and managing automations
 */

import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { VisualAutoViewApi } from '../services/api';
import '../components/graph';

interface Automation {
  entity_id: string;
  name: string;
  description?: string;
  trigger_count: number;
  condition_count: number;
  action_count: number;
}

@customElement('vav-dashboard')
export class Dashboard extends LitElement {
  @property({ type: Object }) config: any = {};
  @state() automations: Automation[] = [];
  @state() selectedAutomation: Automation | null = null;
  @state() loading = false;
  @state() error: string | null = null;
  @state() searchQuery = '';
  @state() selectedTheme = 'light';

  private api: VisualAutoViewApi | null = null;

  static styles = css`
    :host {
      display: block;
      background: var(--card-background, white);
      color: var(--text-color, #000);
      font-family: var(--font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
      height: 100vh;
      overflow: hidden;
    }

    .container {
      display: grid;
      grid-template-columns: 250px 1fr 1fr;
      height: 100%;
      gap: 12px;
      padding: 12px;
    }

    .panel {
      display: flex;
      flex-direction: column;
      background: var(--panel-background, #f5f5f5);
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--divider-color, #e0e0e0);
    }

    .panel-header {
      padding: 12px;
      background: var(--primary-color, #2196F3);
      color: white;
      font-weight: 600;
      font-size: 14px;
    }

    .panel-content {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }

    .search-box {
      padding: 8px;
      margin-bottom: 8px;
      border: 1px solid var(--divider-color, #ddd);
      border-radius: 4px;
      font-size: 14px;
      width: 100%;
      box-sizing: border-box;
    }

    .automation-item {
      padding: 8px;
      margin-bottom: 4px;
      background: white;
      border-radius: 4px;
      cursor: pointer;
      border-left: 4px solid transparent;
      transition: all 0.2s ease;
      font-size: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .automation-item:hover {
      background: var(--hover-background, #f0f0f0);
      border-left-color: var(--primary-color, #2196F3);
    }

    .automation-item.selected {
      background: var(--primary-color, #2196F3);
      color: white;
      border-left-color: var(--accent-color, #FF5722);
    }

    .info-panel {
      display: flex;
      flex-direction: column;
    }

    .info-header {
      padding: 12px;
      background: var(--primary-color, #2196F3);
      color: white;
      font-weight: 600;
    }

    .info-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
    }

    .info-item {
      margin-bottom: 12px;
      font-size: 13px;
    }

    .info-label {
      font-weight: 600;
      color: var(--secondary-text, #666);
      font-size: 11px;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .info-value {
      font-size: 14px;
      color: var(--text-color, #000);
      word-break: break-word;
    }

    .stat-group {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
      margin: 12px 0;
    }

    .stat-box {
      background: white;
      padding: 12px;
      border-radius: 4px;
      text-align: center;
      border: 1px solid var(--divider-color, #ddd);
    }

    .stat-number {
      font-size: 20px;
      font-weight: 700;
      color: var(--primary-color, #2196F3);
    }

    .stat-label {
      font-size: 11px;
      color: var(--secondary-text, #999);
      text-transform: uppercase;
      margin-top: 4px;
    }

    .controls {
      display: flex;
      gap: 8px;
      padding: 12px;
      background: var(--control-background, #f9f9f9);
      border-top: 1px solid var(--divider-color, #e0e0e0);
    }

    button {
      flex: 1;
      padding: 8px;
      border: 1px solid var(--primary-color, #2196F3);
      background: white;
      color: var(--primary-color, #2196F3);
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      transition: all 0.2s ease;
    }

    button:hover {
      background: var(--primary-color, #2196F3);
      color: white;
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--secondary-text, #999);
    }

    .spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
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
      margin-bottom: 12px;
      font-size: 12px;
    }

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--secondary-text, #999);
      text-align: center;
      padding: 20px;
    }

    .graph-panel {
      grid-column: 2 / 4;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.api = new VisualAutoViewApi();
    this.loadAutomations();
  }

  render() {
    return html`
      <div class="container">
        <!-- Automations List Panel -->
        <div class="panel">
          <div class="panel-header">
            Automations
          </div>
          <div class="panel-content">
            ${this.loading && this.automations.length === 0
              ? html`
                  <div class="loading">
                    <div class="spinner"></div>
                  </div>
                `
              : html`
                  <input
                    type="text"
                    class="search-box"
                    placeholder="Search..."
                    .value=${this.searchQuery}
                    @input=${this.onSearchInput}
                  />
                  ${this.getFilteredAutomations().length === 0
                    ? html`
                        <div class="empty-state">
                          No automations found
                        </div>
                      `
                    : html`
                        ${this.getFilteredAutomations().map(
                          (automation) => html`
                            <div
                              class="automation-item ${this.selectedAutomation?.entity_id === automation.entity_id
                                ? 'selected'
                                : ''}"
                              @click=${() => this.selectAutomation(automation)}
                              title="${automation.name}"
                            >
                              ${automation.name}
                            </div>
                          `
                        )}
                      `}
                `}
          </div>
        </div>

        <!-- Info Panel -->
        <div class="panel info-panel">
          <div class="panel-header">
            Details
          </div>
          <div class="panel-content">
            ${this.error ? html` <div class="error">${this.error}</div> ` : ''}
            ${this.selectedAutomation
              ? html`
                  <div class="info-item">
                    <div class="info-label">Entity ID</div>
                    <div class="info-value">${this.selectedAutomation.entity_id}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Name</div>
                    <div class="info-value">${this.selectedAutomation.name}</div>
                  </div>
                  ${this.selectedAutomation.description
                    ? html`
                        <div class="info-item">
                          <div class="info-label">Description</div>
                          <div class="info-value">${this.selectedAutomation.description}</div>
                        </div>
                      `
                    : ''}
                  <div class="stat-group">
                    <div class="stat-box">
                      <div class="stat-number">${this.selectedAutomation.trigger_count}</div>
                      <div class="stat-label">Triggers</div>
                    </div>
                    <div class="stat-box">
                      <div class="stat-number">${this.selectedAutomation.condition_count}</div>
                      <div class="stat-label">Conditions</div>
                    </div>
                    <div class="stat-box">
                      <div class="stat-number">${this.selectedAutomation.action_count}</div>
                      <div class="stat-label">Actions</div>
                    </div>
                  </div>
                `
              : html`
                  <div class="empty-state">
                    Select an automation to view details
                  </div>
                `}
          </div>
          <div class="controls">
            <button @click=${this.exportAutomation} ?disabled=${!this.selectedAutomation}>
              Export
            </button>
            <button @click=${this.compareAutomations} ?disabled=${!this.selectedAutomation}>
              Compare
            </button>
          </div>
        </div>

        <!-- Graph Panel -->
        <div class="panel graph-panel">
          <div class="panel-header">
            Graph View
          </div>
          <div class="panel-content">
            ${this.selectedAutomation
              ? html`
                  <vav-graph
                    .nodes=${this.getGraphNodes()}
                    .edges=${this.getGraphEdges()}
                  ></vav-graph>
                `
              : html`
                  <div class="empty-state">
                    Select an automation to view its graph
                  </div>
                `}
          </div>
        </div>
      </div>
    `;
  }

  private async loadAutomations() {
    this.loading = true;
    this.error = null;
    try {
      const result = await this.api!.listAutomations();
      this.automations = result.automations || [];
      if (this.automations.length > 0) {
        this.selectedAutomation = this.automations[0];
      }
    } catch (err) {
      this.error = `Failed to load automations: ${err instanceof Error ? err.message : 'Unknown error'}`;
    } finally {
      this.loading = false;
    }
  }

  private getFilteredAutomations(): Automation[] {
    if (!this.searchQuery) return this.automations;
    const query = this.searchQuery.toLowerCase();
    return this.automations.filter(
      (a) =>
        a.name.toLowerCase().includes(query) ||
        a.entity_id.toLowerCase().includes(query)
    );
  }

  private selectAutomation(automation: Automation) {
    this.selectedAutomation = automation;
  }

  private onSearchInput(e: Event) {
    this.searchQuery = (e.target as HTMLInputElement).value;
  }

  private async exportAutomation() {
    if (!this.selectedAutomation) return;
    try {
      await this.api!.exportAutomation(this.selectedAutomation.entity_id, 'json');
    } catch (err) {
      this.error = `Export failed: ${err instanceof Error ? err.message : 'Unknown error'}`;
    }
  }

  private async compareAutomations() {
    if (!this.selectedAutomation) return;
    const event = new CustomEvent('compare-requested', {
      detail: { automation: this.selectedAutomation },
    });
    this.dispatchEvent(event);
  }

  private getGraphNodes() {
    if (!this.selectedAutomation) return [];
    return [
      {
        id: 'triggers',
        label: `Triggers (${this.selectedAutomation.trigger_count})`,
        type: 'trigger' as const,
      },
      {
        id: 'conditions',
        label: `Conditions (${this.selectedAutomation.condition_count})`,
        type: 'condition' as const,
      },
      {
        id: 'actions',
        label: `Actions (${this.selectedAutomation.action_count})`,
        type: 'action' as const,
      },
    ];
  }

  private getGraphEdges() {
    return [
      { from: 'triggers', to: 'conditions', arrows: 'to' },
      { from: 'conditions', to: 'actions', arrows: 'to' },
    ];
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'vav-dashboard': Dashboard;
  }
}
