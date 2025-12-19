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
  @property({ type: String }) preselectedAutomationId = '';
  @state() automations: Automation[] = [];
  @state() selectedAutomation: Automation | null = null;
  @state() selectedAutomationDetails: any = null;
  @state() loading = false;
  @state() detailsLoading = false;
  @state() error: string | null = null;
  @state() searchQuery = '';
  @state() selectedTheme = 'light';

  private api: VisualAutoViewApi | null = null;

  static styles = css`
    :host {
      display: block;
      background: var(--card-background, white);
      color: var(--text-color, #000);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
      background: var(--card-background, white);
      color: var(--text-color, #000);
    }

    .automation-item {
      padding: 8px;
      margin-bottom: 4px;
      background: var(--card-background, white);
      border-radius: 4px;
      cursor: pointer;
      border-left: 4px solid transparent;
      transition: all 0.2s ease;
      font-size: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      user-select: none;
      pointer-events: auto;
      touch-action: manipulation;
      color: var(#000);
    }

    .automation-item:hover {
      background: var(#f0f0f0);
      border-left-color: var(#2196F3);
    }

    .automation-item.selected {
      background: var(#2196F3);
      color: white;
      border-left-color: var(#FF5722);
    }

    .info-panel {
      display: flex;
      flex-direction: column;
    }

    .info-header {
      padding: 12px;
      background: var(#2196F3);
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
      color: var(#666);
      font-size: 11px;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .info-value {
      font-size: 14px;
      color: var(#000);
      word-break: break-word;
    }

    .stat-group {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
      margin: 12px 0;
    }

    .stat-box {
      background: var(white);
      padding: 12px;
      border-radius: 4px;
      text-align: center;
      border: 1px solid var(#ddd);
    }

    .stat-number {
      font-size: 20px;
      font-weight: 700;
      color: var(#2196F3);
    }

    .stat-label {
      font-size: 11px;
      color: var(#999);
      text-transform: uppercase;
      margin-top: 4px;
    }

    .controls {
      display: flex;
      gap: 8px;
      padding: 12px;
      background: var(#f9f9f9);
      border-top: 1px solid var(#e0e0e0);
    }

    button {
      flex: 1;
      padding: 8px;
      border: 1px solid var(#2196F3);
      background: var(white);
      color: var(#2196F3);
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      transition: all 0.2s ease;
    }

    button:hover {
      background: var(#2196F3);
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
      color: var(#999);
    }

    .spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid var(#ddd);
      border-top-color: var(#2196F3);
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
      background: var(#ffebee);
      color: var(--ha-error-text-color, #c62828);
      border-radius: 4px;
      margin-bottom: 12px;
      font-size: 12px;
    }

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(#999);
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
                              @click=${(e: Event) => {
                                console.log('Click event fired on:', automation.name);
                                this.selectAutomation(automation);
                              }}
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
              ? this.detailsLoading
                ? html`
                    <div class="loading">
                      <div class="spinner"></div>
                      <p>Loading automation details...</p>
                    </div>
                  `
                : html`
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
                        <div class="stat-number">${
                          this.selectedAutomationDetails?.statistics?.trigger_count ||
                          this.selectedAutomation.trigger_count
                        }</div>
                        <div class="stat-label">Triggers</div>
                      </div>
                      <div class="stat-box">
                        <div class="stat-number">${
                          this.selectedAutomationDetails?.statistics?.condition_count ||
                          this.selectedAutomation.condition_count
                        }</div>
                        <div class="stat-label">Conditions</div>
                      </div>
                      <div class="stat-box">
                        <div class="stat-number">${
                          this.selectedAutomationDetails?.statistics?.action_count ||
                          this.selectedAutomation.action_count
                        }</div>
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
              ? this.detailsLoading
                ? html`
                    <div class="loading">
                      <div class="spinner"></div>
                    </div>
                  `
                : html`
                    <vav-graph
                      .nodes=${this.selectedAutomationDetails?.nodes || []}
                      .edges=${this.selectedAutomationDetails?.edges || []}
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
    console.log('Loading automations... loading state:', this.loading);
    
    try {
      const result = await this.api!.listAutomations();
      console.log('API result:', result);
      
      // Backend returns: { success: true, data: { automations: [...] } }
      if (result.success && result.data?.automations) {
        // Map backend AutomationInfo to frontend Automation format
        this.automations = result.data.automations.map((auto: any) => ({
          entity_id: auto.automation_id,
          name: auto.alias,
          description: auto.description || '',
          trigger_count: auto.node_count || 0,
          condition_count: 0,
          action_count: 0,
        }));
        
        console.log('Loaded automations:', this.automations);
        
        // Check if there's a preselected automation from URL parameter
        if (this.preselectedAutomationId && this.automations.length > 0) {
          const preselected = this.automations.find(
            a => a.entity_id === this.preselectedAutomationId || 
                 a.entity_id === `automation.${this.preselectedAutomationId}` ||
                 a.entity_id.endsWith(`.${this.preselectedAutomationId}`)
          );
          
          if (preselected) {
            this.selectedAutomation = preselected;
            console.log('Auto-selected automation from URL:', this.preselectedAutomationId);
          } else {
            // If not found, select first one
            this.selectedAutomation = this.automations[0];
            console.warn('Automation not found:', this.preselectedAutomationId, 'Selecting first instead');
          }
        } else if (this.automations.length > 0) {
          // No preselection, select first
          this.selectedAutomation = this.automations[0];
        }
      } else {
        console.warn('No automations found in response:', result);
        this.automations = [];
      }
    } catch (err) {
      console.error('Failed to load automations:', err);
      this.error = `Failed to load automations: ${err instanceof Error ? err.message : 'Unknown error'}`;
      this.automations = [];
    } finally {
      this.loading = false;
      console.log('Loading complete. loading state:', this.loading, 'automations count:', this.automations.length);
      this.requestUpdate(); // Force re-render
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

  private async loadAutomationDetails(automationId: string) {
    try {
      const result = await this.api!.getAutomationGraph(automationId);
      if (result.success && result.data) {
        this.selectedAutomationDetails = result.data;
        this.error = null;
        console.log('Loaded automation details:', this.selectedAutomationDetails);
        console.log('Nodes:', this.selectedAutomationDetails.nodes);
        console.log('Edges:', this.selectedAutomationDetails.edges);
      } else {
        this.error = 'Failed to load automation details';
        console.warn('No details in response:', result);
      }
    } catch (err) {
      console.error('Failed to load automation details:', err);
      this.error = `Failed to load details: ${err instanceof Error ? err.message : 'Unknown error'}`;
    } finally {
      this.detailsLoading = false;
      this.requestUpdate();
    }
  }

  private selectAutomation(automation: Automation) {
    console.log('selectAutomation called with:', automation);
    this.selectedAutomation = automation;
    this.selectedAutomationDetails = null;
    this.detailsLoading = true;
    this.requestUpdate();
    this.loadAutomationDetails(automation.entity_id);
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
}

declare global {
  interface HTMLElementTagNameMap {
    'vav-dashboard': Dashboard;
  }
}

