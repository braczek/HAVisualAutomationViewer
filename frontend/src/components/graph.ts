/**
 * Graph Visualization Component
 * Displays automation graph using vis-network
 */

import { LitElement, html, css } from 'lit';
import { customElement, property, query } from 'lit/decorators.js';
import { Network, DataSet } from 'vis-network/standalone';

interface Node {
  id: string;
  label: string;
  type: 'trigger' | 'condition' | 'action';
  color?: string;
  shape?: string;
}

interface Edge {
  from: string;
  to: string;
  arrows?: string;
  color?: string;
}

@customElement('vav-graph')
export class GraphVisualization extends LitElement {
  @property({ type: Array }) nodes: Node[] = [];
  @property({ type: Array }) edges: Edge[] = [];
  @property({ type: Boolean }) interactive = true;
  @property({ type: String }) theme = 'light';

  @query('#graph-container')
  graphContainer!: HTMLElement;

  private network: Network | null = null;

  static styles = css`
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    #graph-container {
      width: 100%;
      height: 600px;
      border: 1px solid var(--divider-color);
      border-radius: 4px;
      overflow: hidden;
      background: var(--card-background-color);
    }

    .controls {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      padding: 8px;
    }

    button {
      padding: 6px 12px;
      border: 1px solid var(--primary-color);
      background: var(--card-background-color);
      color: var(--primary-color);
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.3s ease;
    }

    button:hover {
      background: var(--primary-color);
      color: white;
    }

    button:active {
      transform: scale(0.95);
    }

    .stats {
      display: flex;
      gap: 16px;
      margin-top: 12px;
      font-size: 12px;
      color: var(--secondary-text-color);
    }

    .stat-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .stat-badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 3px;
      background: var(--secondary-background-color);
      font-weight: 500;
      color: var(--primary-text-color);
    }
  `;

  render() {
    return html`
      <div class="controls">
        <button @click=${this.zoomIn}>Zoom In</button>
        <button @click=${this.zoomOut}>Zoom Out</button>
        <button @click=${this.fitToView}>Fit View</button>
        <button @click=${this.centerGraph}>Center</button>
        <button @click=${this.resetLayout}>Reset Layout</button>
      </div>
      <div id="graph-container"></div>
      <div class="stats">
        <div class="stat-item">
          Nodes: <span class="stat-badge">${this.nodes.length}</span>
        </div>
        <div class="stat-item">
          Edges: <span class="stat-badge">${this.edges.length}</span>
        </div>
        <div class="stat-item">
          Triggers: <span class="stat-badge">${this.nodes.filter(n => n.type === 'trigger').length}</span>
        </div>
        <div class="stat-item">
          Conditions: <span class="stat-badge">${this.nodes.filter(n => n.type === 'condition').length}</span>
        </div>
        <div class="stat-item">
          Actions: <span class="stat-badge">${this.nodes.filter(n => n.type === 'action').length}</span>
        </div>
      </div>
    `;
  }

  firstUpdated() {
    console.log('firstUpdated called');
    // Use setTimeout to ensure DOM is fully rendered
    setTimeout(() => {
      this.initializeGraph();
    }, 0);
  }

  updated(changedProperties: Map<string, any>) {
    console.log('Graph component updated, changedProperties:', changedProperties);
    console.log('Current nodes:', this.nodes);
    console.log('Current edges:', this.edges);
    if (changedProperties.has('nodes') || changedProperties.has('edges')) {
      console.log('Nodes or edges changed, updating graph');
      this.updateGraph();
    }
  }

  private initializeGraph() {
    const container = this.renderRoot.querySelector('#graph-container') as HTMLElement;
    if (!container) {
      console.error('Graph container not found!');
      return;
    }

    console.log('Initializing graph with nodes:', this.nodes, 'edges:', this.edges);

    try {
      const nodes = new DataSet(this.getStyledNodes());
      const edges = new DataSet(this.edges as any);

      console.log('DataSets created. Nodes count:', nodes.length, 'Edges count:', edges.length);

      // Get colors from CSS variables
      const computedStyle = getComputedStyle(document.body);
      const edgeColor = computedStyle.getPropertyValue('--divider-color').trim() || '#999';
      const highlightColor = computedStyle.getPropertyValue('--primary-color').trim() || '#2196F3';
      const textColor = computedStyle.getPropertyValue('--primary-text-color').trim() || '#212121';

      const options = {
        physics: {
          enabled: true,
          stabilization: {
            iterations: 200,
          },
        },
        nodes: {
          font: {
            size: 14,
            color: textColor,
          },
          borderWidth: 2,
          borderWidthSelected: 4,
        },
        edges: {
          arrows: {
            to: {
              enabled: true,
              scaleFactor: 0.5,
            },
          },
          smooth: {
            enabled: true,
            type: 'continuous',
            roundness: 0.5,
          },
          color: {
            color: edgeColor,
            highlight: highlightColor,
            hover: edgeColor,
          },
          width: 2,
          hoverWidth: 3,
        },
        interaction: {
          navigationButtons: true,
          keyboard: true,
          zoomView: true,
          dragView: true,
        },
      };

      this.network = new Network(container, { nodes, edges } as any, options);
      console.log('Network created successfully');

      // Event listeners
      if (this.network) {
        this.network.on('click', (params) => {
          const event = new CustomEvent('graph-click', {
            detail: params,
          });
          this.dispatchEvent(event);
        });

        this.network.on('doubleClick', (params) => {
          const event = new CustomEvent('graph-doubleclick', {
            detail: params,
          });
          this.dispatchEvent(event);
        });
      }
    } catch (error) {
      console.error('Error initializing graph:', error);
    }
  }

  private updateGraph() {
    if (!this.network) {
      this.initializeGraph();
      return;
    }

    const nodes = new DataSet(this.getStyledNodes());
    const edges = new DataSet(this.edges as any);

    this.network.setData({ nodes, edges } as any);
  }

  private getStyledNodes(): Node[] {
    // Get colors from CSS variables with fallbacks
    const computedStyle = getComputedStyle(document.body);
    const typeColors = {
      trigger: computedStyle.getPropertyValue('--success-color').trim() || '#4CAF50',
      condition: computedStyle.getPropertyValue('--info-color').trim() || 
                 computedStyle.getPropertyValue('--primary-color').trim() || '#2196F3',
      action: computedStyle.getPropertyValue('--accent-color').trim() || '#FF9800',
    };

    const typeShapes = {
      trigger: 'diamond',
      condition: 'box',
      action: 'circle',
    };

    return this.nodes.map(node => ({
      ...node,
      color: typeColors[node.type] || '#999',
      shape: typeShapes[node.type] || 'dot',
    }));
  }

  zoomIn() {
    if (this.network) {
      const zoom = this.network.getScale() * 1.2;
      this.network.moveTo({
        scale: Math.min(zoom, 3),
        animation: true,
      });
    }
  }

  zoomOut() {
    if (this.network) {
      const zoom = this.network.getScale() / 1.2;
      this.network.moveTo({
        scale: Math.max(zoom, 0.1),
        animation: true,
      });
    }
  }

  fitToView() {
    if (this.network) {
      this.network.fit({ animation: true });
    }
  }

  centerGraph() {
    if (this.network) {
      this.network.moveTo({
        position: { x: 0, y: 0 },
        animation: true,
      });
    }
  }

  resetLayout() {
    if (this.network) {
      this.network.fit({ animation: true });
    }
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'vav-graph': GraphVisualization;
  }
}

