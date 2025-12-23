/**
 * API Client for Visual AutoView
 * Communicates with Home Assistant backend services
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  timestamp?: string;
  // Allow direct property access for convenience
  [key: string]: any;
}

interface GraphData {
  automation_id: string;
  alias: string;
  nodes: any[];
  edges: any[];
  graph: any;
  statistics: {
    node_count: number;
    edge_count: number;
    trigger_count: number;
    condition_count: number;
    action_count: number;
  };
}

interface AutomationInfo {
  automation_id: string;
  alias: string;
  enabled: boolean;
  node_count: number;
  edge_count: number;
}

interface SearchResult {
  automation_id: string;
  alias: string;
  score: number;
  highlights: string[];
}

export class VisualAutoViewApi {
  private api: AxiosInstance;
  private baseUrl: string;
  private lastTokenValidation: number = 0;
  private tokenValidationInterval: number = 5 * 60 * 1000; // 5 minutes
  private isTokenValid: boolean = false;

  constructor(baseUrl: string = '/api/visualautoview') {
    this.baseUrl = baseUrl;
    this.api = axios.create({
      baseURL: baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token interceptor for Home Assistant
    this.api.interceptors.request.use((config) => {
      // Try multiple ways to get the token
      let token = this.getHassToken();
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.debug('[API] Using auth token from:', this.getTokenSource());
      } else {
        console.warn('[API] No authentication token found! Request will fail with 401.');
        console.warn('[API] Token detection sources checked:', this.getTokenDetectionAttempts());
      }
      return config;
    });

    // Add response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
          console.error('[API] Authentication failed. Token may have expired.');
          this.isTokenValid = false;
          // Try to get a fresh token on next request
          this.lastTokenValidation = 0;
        }
        return Promise.reject(error);
      }
    );

    // Initial token validation
    this.validateTokenOnceAsync();
  }

  /**
   * Validate token and refresh if needed (async, non-blocking)
   */
  private validateTokenOnceAsync() {
    setTimeout(() => {
      this.validateToken();
    }, 100);
  }

  /**
   * Validate the current token
   */
  private validateToken() {
    const now = Date.now();
    
    // Only validate if enough time has passed
    if (now - this.lastTokenValidation < this.tokenValidationInterval) {
      return;
    }

    this.lastTokenValidation = now;
    
    // Check if token exists and is accessible
    const token = this.getHassToken();
    if (!token) {
      console.warn('[API] No Home Assistant token available. Token validation failed.');
      this.isTokenValid = false;
      return;
    }

    console.debug('[API] Token validation passed');
    this.isTokenValid = true;
  }

  /**
   * Get the source of the token for debugging
   */
  private getTokenSource(): string {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('token') || urlParams.get('access_token')) {
      return 'URL parameters';
    }

    try {
      const hassTokens = localStorage.getItem('hassTokens');
      if (hassTokens) {
        const tokens = JSON.parse(hassTokens);
        if (tokens.access_token) {
          return 'localStorage (hassTokens)';
        }
      }
    } catch (_e) {
      // Continue to next method
    }

    const hassConnection = (window as any).hassConnection;
    if (hassConnection?.auth?.data?.access_token) {
      return 'window.hassConnection';
    }

    const hassioToken = (window as any).hassio?.token;
    if (hassioToken) {
      return 'legacy hassio token';
    }

    return 'unknown';
  }

  /**
   * Get Home Assistant access token from various sources
   */
  private getHassToken(): string | null {
    // Method 1: From URL parameters (for iframe panels)
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token') || urlParams.get('access_token');
    if (urlToken) {
      console.debug('[API] Found token in URL parameters');
      return urlToken;
    }

    // Method 2: From localStorage (where HA stores tokens)
    try {
      const hassTokens = localStorage.getItem('hassTokens');
      if (hassTokens) {
        const tokens = JSON.parse(hassTokens);
        if (tokens.access_token) {
          console.debug('[API] Found token in localStorage (hassTokens)');
          return tokens.access_token;
        }
      }
    } catch (e) {
      console.debug('[API] Could not read token from localStorage:', e);
    }

    // Method 3: From window.hassConnection (if available)
    try {
      const hassConnection = (window as any).hassConnection;
      if (hassConnection?.auth?.data?.access_token) {
        console.debug('[API] Found token in window.hassConnection');
        return hassConnection.auth.data.access_token;
      }
    } catch (e) {
      console.debug('[API] Could not access window.hassConnection:', e);
    }

    // Method 4: From window.hass.connection (HA frontend integration)
    try {
      const hass = (window as any).hass;
      if (hass?.connection?.auth?.data?.access_token) {
        console.debug('[API] Found token in window.hass.connection');
        return hass.connection.auth.data.access_token;
      }
    } catch (e) {
      console.debug('[API] Could not access window.hass.connection:', e);
    }

    // Method 5: Legacy hassio token (Docker/Hass.io environments)
    try {
      const hassioToken = (window as any).hassio?.token;
      if (hassioToken) {
        console.debug('[API] Found token in legacy hassio');
        return hassioToken;
      }
    } catch (e) {
      console.debug('[API] Could not access legacy hassio token:', e);
    }

    // Method 6: Try to get token from sessionStorage (fallback)
    try {
      const sessionToken = sessionStorage.getItem('ha_access_token');
      if (sessionToken) {
        console.debug('[API] Found token in sessionStorage');
        return sessionToken;
      }
    } catch (e) {
      console.debug('[API] Could not read from sessionStorage:', e);
    }

    console.error('[API] No Home Assistant token found in any source. The extension may not work properly on mobile apps. Please ensure you are accessing this from within Home Assistant.');
    return null;
  }

  /**
   * Get diagnostic info about token detection attempts
   */
  private getTokenDetectionAttempts(): Record<string, string> {
    const attempts: Record<string, string> = {};
    
    // Check each source
    const urlParams = new URLSearchParams(window.location.search);
    attempts['URL params'] = urlParams.get('token') || urlParams.get('access_token') ? 'Found' : 'Not found';
    
    try {
      const hassTokens = localStorage.getItem('hassTokens');
      attempts['localStorage.hassTokens'] = hassTokens ? 'Found' : 'Not found';
    } catch (e) {
      attempts['localStorage.hassTokens'] = 'Error: ' + String(e);
    }
    
    try {
      const hassConnection = (window as any).hassConnection;
      attempts['window.hassConnection'] = hassConnection?.auth?.data?.access_token ? 'Found' : 'Not found';
    } catch (e) {
      attempts['window.hassConnection'] = 'Error: ' + String(e);
    }
    
    try {
      const hass = (window as any).hass;
      attempts['window.hass.connection'] = hass?.connection?.auth?.data?.access_token ? 'Found' : 'Not found';
    } catch (e) {
      attempts['window.hass.connection'] = 'Error: ' + String(e);
    }
    
    try {
      const hassioToken = (window as any).hassio?.token;
      attempts['window.hassio.token'] = hassioToken ? 'Found' : 'Not found';
    } catch (e) {
      attempts['window.hassio.token'] = 'Error: ' + String(e);
    }
    
    try {
      const sessionToken = sessionStorage.getItem('ha_access_token');
      attempts['sessionStorage.ha_access_token'] = sessionToken ? 'Found' : 'Not found';
    } catch (e) {
      attempts['sessionStorage.ha_access_token'] = 'Error: ' + String(e);
    }
    
    return attempts;
  }

  // Phase 1: Graph Parsing
  async parseAutomation(
    automationId: string,
    automationData: any
  ): Promise<ApiResponse<GraphData>> {
    const response = await this.api.post('/phase1/parse', {
      automation_id: automationId,
      automation_data: automationData,
    });
    return response.data;
  }

  async getAutomationGraph(automationId: string): Promise<ApiResponse<GraphData>> {
    const response = await this.api.get(`/phase1/automations/${automationId}/graph`);
    return response.data;
  }

  async listAutomations(page: number = 1, perPage: number = 50): Promise<ApiResponse<{
    total_count: number;
    enabled_count: number;
    disabled_count: number;
    automations: AutomationInfo[];
    page: number;
    per_page: number;
    total_pages: number;
  }>> {
    const response = await this.api.get('/phase1/automations', {
      params: { page, per_page: perPage },
    });
    // Axios wraps response in .data, so response.data contains our ApiResponse
    return response.data;
  }

  async validateAutomation(automationData: any): Promise<ApiResponse<{
    valid: boolean;
    errors: string[];
    warnings: string[];
    statistics: {
      triggers: number;
      conditions: number;
      actions: number;
    };
  }>> {
    const response = await this.api.post('/phase1/validate', {
      automation_data: automationData,
    });
    return response.data;
  }

  // Phase 2: Search & Filter
  async searchAutomations(
    query: string,
    matchType: 'contains' | 'exact' | 'regex' = 'contains',
    limit: number = 10
  ): Promise<ApiResponse<SearchResult[]>> {
    const response = await this.api.post('/phase2/search', {
      query,
      match_type: matchType,
      limit,
    });
    return response.data;
  }

  async advancedSearch(filters: Record<string, any>): Promise<ApiResponse<SearchResult[]>> {
    const response = await this.api.post('/phase2/search/advanced', filters);
    return response.data;
  }

  // Phase 2: Export
  async exportAutomation(
    automationId: string,
    format: 'png' | 'svg' | 'pdf' | 'json' = 'png',
    quality: 'low' | 'medium' | 'high' = 'medium'
  ): Promise<ApiResponse<{ file_path: string; download_url: string }>> {
    const response = await this.api.post('/phase2/export', {
      automation_ids: [automationId],
      format,
      quality,
    });
    return response.data;
  }

  async batchExport(
    automationIds: string[],
    format: 'pdf' = 'pdf'
  ): Promise<ApiResponse<{ file_path: string; download_url: string }>> {
    const response = await this.api.post('/phase2/export/batch', {
      automation_ids: automationIds,
      format,
    });
    return response.data;
  }

  // Phase 2: Themes
  async listThemes(): Promise<ApiResponse<any[]>> {
    const response = await this.api.get('/phase2/themes');
    return response.data;
  }

  async getTheme(themeId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/phase2/themes/${themeId}`);
    return response.data;
  }

  async applyTheme(themeId: string, automationIds?: string[]): Promise<ApiResponse<void>> {
    const response = await this.api.post('/phase2/themes/apply', {
      theme_id: themeId,
      automation_ids: automationIds,
    });
    return response.data;
  }

  // Phase 2: Comparison
  async compareAutomations(automationIds: string[]): Promise<ApiResponse<any>> {
    const response = await this.api.post('/phase2/compare', {
      automation_ids: automationIds,
    });
    return response.data;
  }

  async findSimilar(
    automationId: string,
    threshold: number = 0.5,
    limit: number = 10
  ): Promise<ApiResponse<any[]>> {
    const response = await this.api.post('/phase2/compare/find-similar', {
      automation_id: automationId,
      threshold,
      limit,
    });
    return response.data;
  }

  // Phase 3: Entity Relationships
  async getEntityRelationships(
    automationId?: string,
    entityId?: string
  ): Promise<ApiResponse<any>> {
    const response = await this.api.get('/phase3/entity-relationships', {
      params: { automation_id: automationId, entity_id: entityId },
    });
    return response.data;
  }

  async analyzeEntityImpact(entityId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/phase3/entity-impact/${entityId}`);
    return response.data;
  }

  // Phase 3: Dependency Graph
  async getDependencyGraph(): Promise<ApiResponse<any>> {
    const response = await this.api.get('/phase3/dependency-graph');
    return response.data;
  }

  async findDependencyChains(): Promise<ApiResponse<any[]>> {
    const response = await this.api.get('/phase3/dependency-chains');
    return response.data;
  }

  async detectCircularDependencies(): Promise<ApiResponse<any[]>> {
    const response = await this.api.get('/phase3/circular-dependencies');
    return response.data;
  }

  // Phase 3: Execution Tracking
  async getExecutionHistory(automationId: string, limit: number = 20): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/phase3/execution-history/${automationId}`, {
      params: { limit },
    });
    return response.data;
  }

  async getLastExecution(automationId: string): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/phase3/execution-last/${automationId}`);
    return response.data;
  }

  // Phase 3: Performance Metrics
  async getPerformanceMetrics(
    automationId: string,
    period: string = '30days'
  ): Promise<ApiResponse<any>> {
    const response = await this.api.get(`/phase3/performance-metrics/${automationId}`, {
      params: { period },
    });
    return response.data;
  }

  async getSystemPerformance(): Promise<ApiResponse<any>> {
    const response = await this.api.get('/phase3/system-performance');
    return response.data;
  }

  // Phase 3: Templates
  async getTemplateVariables(automationId: string): Promise<ApiResponse<any[]>> {
    const response = await this.api.get(`/phase3/template-variables/${automationId}`);
    return response.data;
  }

  async previewTemplate(automationId: string): Promise<ApiResponse<any>> {
    const response = await this.api.post('/phase3/preview-template', {
      automation_id: automationId,
    });
    return response.data;
  }

  async validateTemplate(automationId: string): Promise<ApiResponse<any>> {
    const response = await this.api.post('/phase3/validate-template', {
      automation_id: automationId,
    });
    return response.data;
  }

  // Error handling
  private handleError(error: AxiosError): Promise<never> {
    const status = error.response?.status;
    const statusText = error.response?.statusText;
    const message = (error.response?.data as any)?.message || error.message;
    
    if (status === 401 || status === 403) {
      console.error('[API] Authentication error (401/403):', message);
      console.error('[API] Token may have expired. Please log in again.');
      throw new Error(`Authentication failed: ${message}`);
    } else if (status === 404) {
      console.error('[API] Endpoint not found (404):', error.config?.url);
      throw new Error(`API endpoint not found: ${error.config?.url}`);
    } else if (status === 500) {
      console.error('[API] Server error (500):', message);
      throw new Error(`Server error: ${message}`);
    } else if (error.response) {
      // Server responded with error status
      console.error('[API] HTTP Error:', status, statusText);
      throw new Error(`${status}: ${statusText}`);
    } else if (error.request) {
      // Request made but no response (network error)
      console.error('[API] Network error: No response from server');
      throw new Error('Network error: No response from server. Check your connection.');
    } else {
      // Error in request setup
      console.error('[API] Request setup error:', message);
      throw error;
    }
  }
}

// Export singleton instance
export const api = new VisualAutoViewApi();
