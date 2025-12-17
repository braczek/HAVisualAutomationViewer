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
      const token = (window as any).hassio?.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Phase 1: Graph Parsing
  async parseAutomation(
    automationId: string,
    automationData: any
  ): Promise<ApiResponse<GraphData>> {
    return this.api.post('/phase1/parse', {
      automation_id: automationId,
      automation_data: automationData,
    });
  }

  async getAutomationGraph(automationId: string): Promise<ApiResponse<GraphData>> {
    return this.api.get(`/phase1/automations/${automationId}/graph`);
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
    return this.api.get('/phase1/automations', {
      params: { page, per_page: perPage },
    });
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
    return this.api.post('/phase1/validate', {
      automation_data: automationData,
    });
  }

  // Phase 2: Search & Filter
  async searchAutomations(
    query: string,
    matchType: 'contains' | 'exact' | 'regex' = 'contains',
    limit: number = 10
  ): Promise<ApiResponse<SearchResult[]>> {
    return this.api.post('/phase2/search', {
      query,
      match_type: matchType,
      limit,
    });
  }

  async advancedSearch(filters: Record<string, any>): Promise<ApiResponse<SearchResult[]>> {
    return this.api.post('/phase2/search/advanced', filters);
  }

  // Phase 2: Export
  async exportAutomation(
    automationId: string,
    format: 'png' | 'svg' | 'pdf' | 'json' = 'png',
    quality: 'low' | 'medium' | 'high' = 'medium'
  ): Promise<ApiResponse<{ file_path: string; download_url: string }>> {
    return this.api.post('/phase2/export', {
      automation_ids: [automationId],
      format,
      quality,
    });
  }

  async batchExport(
    automationIds: string[],
    format: 'pdf' = 'pdf'
  ): Promise<ApiResponse<{ file_path: string; download_url: string }>> {
    return this.api.post('/phase2/export/batch', {
      automation_ids: automationIds,
      format,
    });
  }

  // Phase 2: Themes
  async listThemes(): Promise<ApiResponse<any[]>> {
    return this.api.get('/phase2/themes');
  }

  async getTheme(themeId: string): Promise<ApiResponse<any>> {
    return this.api.get(`/phase2/themes/${themeId}`);
  }

  async applyTheme(themeId: string, automationIds?: string[]): Promise<ApiResponse<void>> {
    return this.api.post('/phase2/themes/apply', {
      theme_id: themeId,
      automation_ids: automationIds,
    });
  }

  // Phase 2: Comparison
  async compareAutomations(automationIds: string[]): Promise<ApiResponse<any>> {
    return this.api.post('/phase2/compare', {
      automation_ids: automationIds,
    });
  }

  async findSimilar(
    automationId: string,
    threshold: number = 0.5,
    limit: number = 10
  ): Promise<ApiResponse<any[]>> {
    return this.api.post('/phase2/compare/find-similar', {
      automation_id: automationId,
      threshold,
      limit,
    });
  }

  // Phase 3: Entity Relationships
  async getEntityRelationships(
    automationId?: string,
    entityId?: string
  ): Promise<ApiResponse<any>> {
    return this.api.get('/phase3/entity-relationships', {
      params: { automation_id: automationId, entity_id: entityId },
    });
  }

  async analyzeEntityImpact(entityId: string): Promise<ApiResponse<any>> {
    return this.api.get(`/phase3/entity-impact/${entityId}`);
  }

  // Phase 3: Dependency Graph
  async getDependencyGraph(): Promise<ApiResponse<any>> {
    return this.api.get('/phase3/dependency-graph');
  }

  async findDependencyChains(): Promise<ApiResponse<any[]>> {
    return this.api.get('/phase3/dependency-chains');
  }

  async detectCircularDependencies(): Promise<ApiResponse<any[]>> {
    return this.api.get('/phase3/circular-dependencies');
  }

  // Phase 3: Execution Tracking
  async getExecutionHistory(automationId: string, limit: number = 20): Promise<ApiResponse<any>> {
    return this.api.get(`/phase3/execution-history/${automationId}`, {
      params: { limit },
    });
  }

  async getLastExecution(automationId: string): Promise<ApiResponse<any>> {
    return this.api.get(`/phase3/execution-last/${automationId}`);
  }

  // Phase 3: Performance Metrics
  async getPerformanceMetrics(
    automationId: string,
    period: string = '30days'
  ): Promise<ApiResponse<any>> {
    return this.api.get(`/phase3/performance-metrics/${automationId}`, {
      params: { period },
    });
  }

  async getSystemPerformance(): Promise<ApiResponse<any>> {
    return this.api.get('/phase3/system-performance');
  }

  // Phase 3: Templates
  async getTemplateVariables(automationId: string): Promise<ApiResponse<any[]>> {
    return this.api.get(`/phase3/template-variables/${automationId}`);
  }

  async previewTemplate(automationId: string): Promise<ApiResponse<any>> {
    return this.api.post('/phase3/preview-template', {
      automation_id: automationId,
    });
  }

  async validateTemplate(automationId: string): Promise<ApiResponse<any>> {
    return this.api.post('/phase3/validate-template', {
      automation_id: automationId,
    });
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
