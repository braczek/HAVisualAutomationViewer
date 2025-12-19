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
      }
      return config;
    });
  }

  /**
   * Get Home Assistant access token from various sources
   */
  private getHassToken(): string | null {
    // Method 1: From URL parameters (for iframe panels)
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token') || urlParams.get('access_token');
    if (urlToken) {
      return urlToken;
    }

    // Method 2: From localStorage (where HA stores tokens)
    try {
      const hassTokens = localStorage.getItem('hassTokens');
      if (hassTokens) {
        const tokens = JSON.parse(hassTokens);
        if (tokens.access_token) {
          return tokens.access_token;
        }
      }
    } catch (e) {
      console.warn('Could not read token from localStorage:', e);
    }

    // Method 3: From window.hassConnection (if available)
    const hassConnection = (window as any).hassConnection;
    if (hassConnection?.auth?.data?.access_token) {
      return hassConnection.auth.data.access_token;
    }

    // Method 4: Legacy hassio token
    const hassioToken = (window as any).hassio?.token;
    if (hassioToken) {
      return hassioToken;
    }

    console.error('No Home Assistant token found. Please access this page from within Home Assistant.');
    return null;
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
    console.error('API Error:', error);
    if (error.response) {
      // Server responded with error status
      throw new Error(`${error.response.status}: ${error.response.statusText}`);
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server');
    } else {
      // Error in request setup
      throw error;
    }
  }
}

// Export singleton instance
export const api = new VisualAutoViewApi();
