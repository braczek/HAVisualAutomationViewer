/**
 * Home Assistant Panel Integration
 * This creates a custom panel that integrates properly with HA's frontend
 */

import { LitElement, html, css, PropertyValues } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import './views/dashboard';
import './views/analytics';
import './components/graph';

// Home Assistant type definitions
interface HomeAssistant {
  states: any;
  callService: (domain: string, service: string, data?: any) => Promise<any>;
  callWS: (message: any) => Promise<any>;
  language: string;
  themes: any;
  selectedTheme: any;
  connection: any;
  user: any;
}

interface PanelInfo {
  component_name: string;
  config: any;
  icon: string;
  title: string;
  url_path: string;
}

@customElement('visualautoview-panel')
export class VisualAutoViewPanel extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ attribute: false }) public panel!: PanelInfo;
  @property({ type: Boolean }) public narrow = false;

  @state() private currentView = 'dashboard';
  @state() private selectedAutomation = '';

  protected updated(changedProps: PropertyValues): void {
    super.updated(changedProps);
    
    // When hass object changes, update theme
    if (changedProps.has('hass') && this.hass) {
      this.updateThemeFromHass();
    }
  }

  private updateThemeFromHass() {
    if (!this.hass) return;

    // Access HA's theme directly
    const isDark = this.hass.themes?.darkMode || false;
    
    // Apply HA's CSS variables to our component
    const haStyles = getComputedStyle(document.documentElement);
    
    // Set CSS variables that match HA's theme
    this.style.setProperty('--primary-color', haStyles.getPropertyValue('--primary-color'));
    this.style.setProperty('--accent-color', haStyles.getPropertyValue('--accent-color'));
    this.style.setProperty('--primary-text-color', haStyles.getPropertyValue('--primary-text-color'));
    this.style.setProperty('--primary-background-color', haStyles.getPropertyValue('--primary-background-color'));
    this.style.setProperty('--card-background-color', haStyles.getPropertyValue('--card-background-color'));
    this.style.setProperty('--divider-color', haStyles.getPropertyValue('--divider-color'));
    
    // Toggle dark mode class
    this.classList.toggle('dark-mode', isDark);
  }

  private handleViewChange(view: string) {
    console.log('View change requested:', view);
    this.currentView = view;
    console.log('Current view set to:', this.currentView);
    this.requestUpdate(); // Force re-render
  }

  private handleAutomationSelect(automationId: string) {
    this.selectedAutomation = automationId;
    this.currentView = 'dashboard';
  }

  static get styles() {
    return css`
      :host {
        display: block;
        height: 100%;
        background-color: var(--primary-background-color, #fafafa);
        color: var(--primary-text-color, #212121);
        font-family: var(--paper-font-body1_-_font-family);
        -webkit-font-smoothing: var(--paper-font-body1_-_-webkit-font-smoothing);
        font-size: var(--paper-font-body1_-_font-size);
        font-weight: var(--paper-font-body1_-_font-weight);
        line-height: var(--paper-font-body1_-_line-height);
      }

      :host(.dark-mode) {
        background-color: var(--primary-background-color, #111111);
        color: var(--primary-text-color, #e1e1e1);
      }

      .panel-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
      }

      .toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 24px;
        background-color: var(--card-background-color, white);
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .toolbar h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .nav-buttons {
        display: flex;
        gap: 8px;
      }

      .nav-button {
        padding: 8px 16px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
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

      .content {
        flex: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;
      }

      vav-dashboard,
      vav-analytics {
        display: block;
        flex: 1;
        height: 100%;
      }
    `;
  }

  render() {
    return html`
      <div class="panel-container">
        <div class="toolbar">
          <h1>🔍 Visual AutoView</h1>
          <div class="nav-buttons">
            <button
              class="nav-button ${this.currentView === 'dashboard' ? 'active' : ''}"
              @click=${() => this.handleViewChange('dashboard')}
            >
              Dashboard
            </button>
            <button
              class="nav-button ${this.currentView === 'analytics' ? 'active' : ''}"
              @click=${() => this.handleViewChange('analytics')}
            >
              Analytics
            </button>
          </div>
        </div>

        <div class="content">
          ${this.currentView === 'dashboard'
            ? html`<vav-dashboard
                .hass=${this.hass}
                .selectedAutomation=${this.selectedAutomation}
              ></vav-dashboard>`
            : html`<vav-analytics
                .hass=${this.hass}
              ></vav-analytics>`}
        </div>
      </div>
    `;
  }
}

// This is required for HA to load the panel
declare global {
  interface Window {
    customCards?: any[];
  }
}
