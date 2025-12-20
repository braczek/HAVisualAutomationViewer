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
  @state() isDarkMode = false;

  connectedCallback() {
    super.connectedCallback();
    this.detectTheme();
    this.parseUrlParameters();
  }

  private detectTheme() {
    // Try to detect dark mode from multiple sources
    
    // 1. Check if we're in an iframe and can access parent HA theme
    try {
      if (window.parent && window.parent !== window) {
        const parentStyles = window.parent.getComputedStyle(window.parent.document.documentElement);
        const bgColor = parentStyles.getPropertyValue('--primary-background-color') || 
                       parentStyles.getPropertyValue('background-color');
        // If background is dark, we're in dark mode
        if (bgColor && this.isColorDark(bgColor)) {
          this.isDarkMode = true;
        }
      }
    } catch (e) {
      // Cross-origin restriction, fallback to other methods
    }

    // 2. Check URL parameter
    const params = new URLSearchParams(window.location.search);
    if (params.get('theme') === 'dark') {
      this.isDarkMode = true;
    } else if (params.get('theme') === 'light') {
      this.isDarkMode = false;
    }
    // 3. Check system preference if not overridden
    else if (!this.isDarkMode && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      this.isDarkMode = true;
    }

    // Apply theme class to document
    if (this.isDarkMode) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }

    // Listen for system theme changes
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        this.isDarkMode = e.matches;
        if (this.isDarkMode) {
          document.documentElement.classList.add('dark-mode');
        } else {
          document.documentElement.classList.remove('dark-mode');
        }
        this.requestUpdate();
      });
    }
  }

  private isColorDark(color: string): boolean {
    // Convert color to RGB and calculate luminance
    const rgb = color.match(/\d+/g);
    if (!rgb || rgb.length < 3) return false;
    const [r, g, b] = rgb.map(Number);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance < 0.5;
  }

  private parseUrlParameters() {
    const params = new URLSearchParams(window.location.search);
    
    // Check for automation parameter
    const automationParam = params.get('automation');
    if (automationParam) {
      this.selectedAutomation = automationParam;
      // Switch to dashboard view to show the graph
      this.currentView = 'dashboard';
      console.log('Auto-selected automation from URL:', automationParam);
    }
    
    // Check for view parameter
    const viewParam = params.get('view');
    if (viewParam === 'analytics' || viewParam === 'dashboard') {
      this.currentView = viewParam;
    }
  }

  static styles = css`
    :host {
      display: block;
      height: 100vh;
      overflow: hidden;
      background: var(--primary-background-color, #fafafa);
      color: var(--primary-text-color, #212121);
      font-family: var(--paper-font-body1_-_font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif);
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
      background: var(--card-background-color);
      color: var(--primary-text-color);
      padding: 12px 16px;
      box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0, 0, 0, 0.1));
      border-bottom: 1px solid var(--divider-color);
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
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      color: var(--primary-text-color);
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .nav-button:hover {
      background: var(--secondary-background-color);
      border-color: var(--primary-color);
    }

    .nav-button.active {
      background: var(--primary-color);
      color: var(--text-primary-color, white);
      border-color: var(--primary-color);
    }
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
            .preselectedAutomationId=${this.selectedAutomation}
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
          <span>Visual AutoView v1.0.1</span>
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
