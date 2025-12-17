/**
 * Main Application Component
 * Orchestrates the entire VisualAutoView UI
 */

import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import './views/dashboard';
import './views/analytics';
import './components/graph';

@customElement('vav-app')
export class VisualAutoViewApp extends LitElement {
  @state() currentView = 'dashboard';
  @state() selectedAutomation = '';

  static styles = css`
    :host {
      display: block;
      --primary-color: #2196F3;
      --accent-color: #FF9800;
      --divider-color: #e0e0e0;
      --panel-background: #f5f5f5;
      --card-background: white;
      --text-color: #000;
      --secondary-text: #666;
      --hover-background: #f0f0f0;
      --control-background: #f9f9f9;
      --metric-bg: #f9f9f9;
      --success-color: #4CAF50;
      --warning-color: #FFC107;
      --error-color: #F44336;

      height: 100vh;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
        Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    .app-container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--primary-color);
      color: white;
      padding: 12px 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      z-index: 100;
    }

    .header-title {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 18px;
      font-weight: 600;
    }

    .header-icon {
      font-size: 24px;
    }

    .nav-buttons {
      display: flex;
      gap: 8px;
    }

    .nav-button {
      padding: 8px 12px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: rgba(255, 255, 255, 0.1);
      color: white;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .nav-button:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.5);
    }

    .nav-button.active {
      background: rgba(255, 255, 255, 0.3);
      border-color: white;
    }

    .content {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    vav-dashboard,
    vav-analytics {
      display: none;
      height: 100%;
    }

    vav-dashboard.active,
    vav-analytics.active {
      display: block;
    }

    .footer {
      padding: 8px 16px;
      background: var(--control-background);
      border-top: 1px solid var(--divider-color);
      font-size: 12px;
      color: var(--secondary-text);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--success-color);
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%,
      100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }
  `;

  render() {
    return html`
      <div class="app-container">
        <div class="header">
          <div class="header-title">
            <span class="header-icon">📊</span>
            <span>Visual AutoView</span>
          </div>
          <div class="nav-buttons">
            <button
              class="nav-button ${this.currentView === 'dashboard' ? 'active' : ''}"
              @click=${() => this.switchView('dashboard')}
            >
              Dashboard
            </button>
            <button
              class="nav-button ${this.currentView === 'analytics' ? 'active' : ''}"
              @click=${() => this.switchView('analytics')}
            >
              Analytics
            </button>
          </div>
        </div>

        <div class="content">
          <vav-dashboard
            class="${this.currentView === 'dashboard' ? 'active' : ''}"
            @compare-requested=${this.onCompareRequested}
          ></vav-dashboard>

          <vav-analytics
            class="${this.currentView === 'analytics' ? 'active' : ''}"
            .selectedAutomation=${this.selectedAutomation}
          ></vav-analytics>
        </div>

        <div class="footer">
          <div class="status-indicator">
            <div class="status-dot"></div>
            <span>Connected to Home Assistant</span>
          </div>
          <span>Visual AutoView v1.0.0</span>
        </div>
      </div>
    `;
  }

  private switchView(view: string) {
    this.currentView = view;
  }

  private onCompareRequested(e: CustomEvent) {
    // Handle automation comparison
    console.log('Compare requested:', e.detail);
    // Would open comparison modal here
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'vav-app': VisualAutoViewApp;
  }
}
