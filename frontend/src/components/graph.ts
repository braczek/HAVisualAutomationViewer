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
      border: 1px solid var(--divider-color, #e0e0e0);
      border-radius: 4px;
      overflow: hidden;
    }

    .controls {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      padding: 8px;
    }

    button {
      padding: 6px 12px;
      border: 1px solid var(--primary-color, #2196F3);
      background: white;
      color: var(--primary-color, #2196F3);
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.3s ease;
    }

    button:hover {
      background: var(--primary-color, #2196F3);
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
      color: var(--secondary-text, #666);
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
      background: var(--accent-color, #f5f5f5);
      font-weight: 500;
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
    this.initializeGraph();
  }

  updated(changedProperties: Map<string, any>) {
    if (changedProperties.has('nodes') || changedProperties.has('edges')) {
      this.updateGraph();
    }
  }

  private initializeGraph() {
    if (!this.graphContainer) return;

    const nodes = new DataSet(this.getStyledNodes());
    const edges = new DataSet(this.edges as any);

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
          color: 'black',
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
          color: '#999',
          highlight: '#2196F3',
          hover: '#666',
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

    this.network = new Network(this.graphContainer, { nodes, edges } as any, options);

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
    const typeColors = {
      trigger: '#4CAF50',
      condition: '#2196F3',
      action: '#FF9800',
    };

    const typeShapes = {
      trigger: 'diamond',
      condition: 'box',
      action: 'circle',
    };

    return this.nodes.map(node => ({
      ...node,
      color: typeColors[node.type],
      shape: typeShapes[node.type],
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
