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
  @property({ attribute: false }) hass: any; // Home Assistant object
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
  @state() isFullscreen = false;
  @state() selectedNodeDetails: any = null;

  private api: VisualAutoViewApi | null = null;

  static styles = css`
    :host {
      display: block;
      background: var(--primary-background-color);
      color: var(--primary-text-color);
      font-family: var(--paper-font-body1_-_font-family);
      height: 100%;
      overflow: hidden;
    }

    .container {
      display: grid;
      grid-template-columns: 250px 1fr;
      grid-template-rows: auto 1fr;
      height: 100%;
      gap: 12px;
      padding: 12px;
    }

    .automations-panel {
      grid-row: 1 / 3;
    }

    .details-panel {
      grid-column: 2;
      grid-row: 1;
      max-height: 400px;
    }

    .graph-panel {
      grid-column: 2;
      grid-row: 2;
    }

    .panel {
      display: flex;
      flex-direction: column;
      background: var(--card-background-color);
      border-radius: var(--ha-card-border-radius, 12px);
      overflow: hidden;
      border: 1px solid var(--divider-color);
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
      transition: all 0.3s ease;
    }

    .panel-header {
      padding: 12px;
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
      font-weight: 600;
      font-size: 14px;
      border-bottom: 1px solid var(--divider-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      user-select: none;
    }

    .fullscreen-button {
      background: var(--primary-color);
      color: var(--text-primary-color, white);
      border: none;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 11px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: all 0.2s ease;
      white-space: nowrap;
      flex-shrink: 0;
      flex: none;
      width: auto;
    }

    .fullscreen-button:hover {
      background: var(--accent-color);
      transform: scale(1.05);
    }

    .fullscreen-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .fullscreen-button:disabled:hover {
      transform: none;
    }

    .panel-title {
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .panel-content {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }

    .search-box {
      padding: 8px;
      margin-bottom: 8px;
      border: 1px solid var(--divider-color);
      border-radius: 4px;
      font-size: 14px;
      width: 100%;
      box-sizing: border-box;
      background: var(--card-background-color);
      color: var(--primary-text-color);
    }

    .search-box:focus {
      outline: none;
      border-color: var(--primary-color);
    }

    .automation-item {
      padding: 8px;
      margin-bottom: 4px;
      background: var(--card-background-color);
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
      color: var(--primary-text-color);
    }

    .automation-item:hover {
      background: var(--secondary-background-color);
      border-left-color: var(--primary-color);
    }

    .automation-item.selected {
      background: var(--primary-color);
      color: var(--text-primary-color, white);
      border-left-color: var(--accent-color);
      font-weight: 600;
    }

    .info-panel {
      display: flex;
      flex-direction: column;
    }

    .info-header {
      padding: 12px;
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
      font-weight: 600;
      border-bottom: 1px solid var(--divider-color);
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
      color: var(--secondary-text-color);
      font-size: 11px;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .info-value {
      font-size: 14px;
      color: var(--primary-text-color);
      word-break: break-word;
    }

    .stat-group {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
      margin: 12px 0;
    }

    .stat-box {
      background: var(--card-background-color);
      padding: 12px;
      border-radius: 4px;
      text-align: center;
      border: 1px solid var(--divider-color);
    }

    .stat-number {
      font-size: 20px;
      font-weight: 700;
      color: var(--primary-color);
    }

    .stat-label {
      font-size: 11px;
      color: var(--secondary-text-color);
      text-transform: uppercase;
      margin-top: 4px;
    }

    .controls {
      display: flex;
      gap: 8px;
      padding: 12px;
      background: var(--secondary-background-color);
      border-top: 1px solid var(--divider-color);
    }

    button {
      flex: 1;
      padding: 8px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      color: var(--primary-text-color);
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      transition: all 0.2s ease;
    }

    button:hover {
      background: var(--primary-color);
      color: var(--text-primary-color, white);
      border-color: var(--primary-color);
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
      color: var(--secondary-text-color);
    }

    .spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid var(--divider-color);
      border-top-color: var(--primary-color);
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
      background: var(--error-color, #ffebee);
      color: var(--error-state-color, #c62828);
      border-radius: 4px;
      margin-bottom: 12px;
      font-size: 12px;
    }

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: var(--secondary-text-color);
      text-align: center;
      padding: 20px;
    }

    .graph-panel {
      grid-column: 2 / 4;
    }

    .fullscreen-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: var(--primary-background-color);
      z-index: 9999;
      display: flex;
      flex-direction: column;
    }

    .fullscreen-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      background: var(--secondary-background-color);
      border-bottom: 1px solid var(--divider-color);
    }

    .fullscreen-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--primary-text-color);
    }

    .close-fullscreen-button {
      background: var(--error-color, #d32f2f);
      color: white;
      border: none;
      padding: 6px 14px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
      white-space: nowrap;
      flex-shrink: 0;
      flex: none;
      width: auto;
    }

    .close-fullscreen-button:hover {
      background: var(--error-color-dark, #b71c1c);
      transform: scale(1.05);
    }

    .node-details {
      margin-top: 16px;
      padding: 12px;
      background: var(--secondary-background-color);
      border-radius: 4px;
      border: 1px solid var(--divider-color);
    }

    .node-details-header {
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--primary-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .node-type-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .node-type-trigger {
      background: var(--success-color, #4CAF50);
      color: white;
    }

    .node-type-condition {
      background: var(--info-color, #2196F3);
      color: white;
    }

    .node-type-action {
      background: var(--accent-color, #FF9800);
      color: white;
    }

    .yaml-content {
      margin-top: 8px;
      padding: 8px;
      background: var(--primary-background-color);
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      overflow-x: auto;
      max-height: 200px;
      overflow-y: auto;
      white-space: pre;
      color: var(--primary-text-color);
      border: 1px solid var(--divider-color);
    }

    .clear-selection {
      background: var(--secondary-background-color);
      color: var(--primary-text-color);
      border: 1px solid var(--divider-color);
      padding: 4px 8px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 11px;
      transition: all 0.2s ease;
    }

    .clear-selection:hover {
      background: var(--divider-color);
    }

    .fullscreen-content {
      flex: 1;
      overflow: hidden;
      padding: 16px;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.api = new VisualAutoViewApi();
    this.loadAutomations();
  }

  render() {
    return html`
      ${this.isFullscreen ? html`
        <div class="fullscreen-overlay">
          <div class="fullscreen-header">
            <div class="fullscreen-title">
              🔍 ${this.selectedAutomation?.name || 'Automation Graph'}
            </div>
            <button class="close-fullscreen-button" @click=${this.toggleFullscreen}>
              <span>✕</span>
              <span>Close Fullscreen</span>
            </button>
          </div>
          <div class="fullscreen-content">
            ${this.selectedAutomation && !this.detailsLoading
              ? html`
                  <vav-graph
                    .nodes=${this.selectedAutomationDetails?.nodes || []}
                    .edges=${this.selectedAutomationDetails?.edges || []}
                    @graph-doubleclick=${this.onGraphClick}
                  ></vav-graph>
                `
              : html`
                  <div class="empty-state">
                    ${this.detailsLoading ? html`<div class="spinner"></div>` : 'Select an automation to view its graph'}
                  </div>
                `}
          </div>
        </div>
      ` : ''}
      <div class="container">
        <!-- Automations List Panel -->
        <div class="panel automations-panel">
          <div class="panel-header">
            <span class="panel-title">Automations</span>
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
                                e.stopPropagation();
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
        <div class="panel details-panel">
          <div class="panel-header">
            <span class="panel-title">Details</span>
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
                    ${this.selectedNodeDetails ? html`
                      <div class="node-details">
                        <div class="node-details-header">
                          <div>
                            <span class="node-type-badge node-type-${this.selectedNodeDetails.type}">
                              ${this.selectedNodeDetails.type}
                            </span>
                            ${this.selectedNodeDetails.label}
                          </div>
                          <button class="clear-selection" @click=${this.clearNodeSelection}>
                            ✕ Clear
                          </button>
                        </div>
                        ${this.selectedNodeDetails.data ? html`
                          <div class="yaml-content">${this.formatYaml(this.selectedNodeDetails.data)}</div>
                        ` : ''}
                      </div>
                    ` : ''}
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
            <span class="panel-title">Graph View</span>
            <button class="fullscreen-button" @click=${this.toggleFullscreen} ?disabled=${!this.selectedAutomation}>
              <span>⛶</span>
              <span>Fullscreen</span>
            </button>
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
                      @graph-doubleclick=${this.onGraphClick}
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

  private toggleFullscreen() {
    this.isFullscreen = !this.isFullscreen;
    this.requestUpdate();
  }

  private onSearchInput(e: Event) {
    this.searchQuery = (e.target as HTMLInputElement).value;
    this.requestUpdate();
  }

  private async exportAutomation() {
    if (!this.selectedAutomation) return;
    try {
      const result = await this.api!.exportAutomation(this.selectedAutomation.entity_id, 'json');
      
      if (result.success && result.data?.download_url) {
        // Trigger file download
        const link = document.createElement('a');
        link.href = result.data.download_url;
        link.download = `${this.selectedAutomation.entity_id}_export.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        this.error = 'Export failed: No download URL returned';
      }
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

  private onGraphClick(e: CustomEvent) {
    const { nodes, edges } = e.detail;
    
    if (nodes && nodes.length > 0) {
      // Node was clicked
      const nodeId = nodes[0];
      const node = this.selectedAutomationDetails?.nodes?.find((n: any) => n.id === nodeId);
      
      if (node) {
        this.selectedNodeDetails = {
          id: node.id,
          label: node.label,
          type: node.type,
          data: node.data
        };
        this.requestUpdate();
      }
    } else if (edges && edges.length > 0) {
      // Edge was clicked
      const edgeId = edges[0];
      const edge = this.selectedAutomationDetails?.edges?.find((e: any) => 
        `${e.from}-${e.to}` === edgeId || e.id === edgeId
      );
      
      if (edge) {
        this.selectedNodeDetails = {
          id: edgeId,
          label: edge.label || 'Connection',
          type: 'edge',
          data: {
            from: edge.from,
            to: edge.to,
            label: edge.label
          }
        };
        this.requestUpdate();
      }
    }
  }

  private clearNodeSelection() {
    this.selectedNodeDetails = null;
    this.requestUpdate();
  }

  private getEntityName(entityId: string): string | null {
    if (!this.hass || !entityId) return null;
    
    const state = this.hass.states[entityId];
    if (state?.attributes?.friendly_name) {
      return state.attributes.friendly_name;
    }
    
    return null;
  }

  private getDeviceName(deviceId: string): string | null {
    if (!this.hass || !deviceId) return null;
    
    // Try to get device info from device registry
    const deviceRegistry = this.hass.devices;
    if (deviceRegistry && deviceRegistry[deviceId]) {
      return deviceRegistry[deviceId].name_by_user || deviceRegistry[deviceId].name || null;
    }
    
    // Fallback: try to find an entity with this device_id and use its friendly name
    for (const [_entityId, state] of Object.entries(this.hass.states)) {
      if ((state as any).attributes?.device_id === deviceId) {
        const friendlyName = (state as any).attributes?.friendly_name;
        if (friendlyName) {
          return friendlyName;
        }
      }
    }
    
    return null;
  }

  private formatValueWithLabel(key: string, value: string): string {
    let label: string | null = null;
    
    if (key === 'entity_id') {
      label = this.getEntityName(value);
    } else if (key === 'device_id') {
      label = this.getDeviceName(value);
    }
    
    if (label) {
      return `${value} (${label})`;
    }
    
    return value;
  }

  private formatYaml(data: any, indent: number = 0): string {
    if (data === null || data === undefined) {
      return 'null';
    }

    if (typeof data === 'string') {
      return data;
    }

    if (typeof data === 'number' || typeof data === 'boolean') {
      return String(data);
    }

    if (Array.isArray(data)) {
      if (data.length === 0) return '[]';
      const spaces = '  '.repeat(indent);
      return data.map((_item) => {
        if (typeof _item === 'object') {
          const formatted = this.formatYaml(_item, indent + 1);
          return `${spaces}- ${formatted.replace(/^\s+/, '')}`;
        }
        return `${spaces}- ${_item}`;
      }).join('\n');
    }

    if (typeof data === 'object') {
      const spaces = '  '.repeat(indent);
      return Object.entries(data)
        .map(([key, value]) => {
          if (typeof value === 'object' && value !== null) {
            if (Array.isArray(value)) {
              if (value.length === 0) return `${spaces}${key}: []`;
              const arrayContent = this.formatYaml(value, indent + 1);
              return `${spaces}${key}:\n${arrayContent}`;
            } else {
              const objContent = this.formatYaml(value, indent + 1);
              return `${spaces}${key}:\n${objContent}`;
            }
          }
          // Add friendly names/labels for entity_id and device_id
          const formattedValue = typeof value === 'string' ? this.formatValueWithLabel(key, value) : value;
          return `${spaces}${key}: ${formattedValue}`;
        })
        .join('\n');
    }

    return String(data);
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'vav-dashboard': Dashboard;
  }
}

