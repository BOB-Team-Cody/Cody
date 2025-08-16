import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  AnalyzeRequest,
  AnalyzeResponse,
  GraphDataResponse,
  Statistics,
  HealthResponse,
  ApiError,
} from '@/types';

class CodeWeaverAPI {
  private api: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        const apiError = this.handleApiError(error);
        console.error('API Response Error:', apiError);
        return Promise.reject(apiError);
      }
    );
  }

  private handleApiError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      const data = error.response.data as any;
      return {
        message: data?.detail || error.message,
        status: error.response.status,
        detail: data?.detail,
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'No response from server. Please check if the API server is running.',
        status: 0,
      };
    } else {
      // Something happened in setting up the request
      return {
        message: error.message,
      };
    }
  }

  /**
   * Check API health and connection status
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await this.api.get<HealthResponse>('/health');
    return response.data;
  }

  /**
   * Analyze a Python project
   */
  async analyzeProject(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    const response = await this.api.post<AnalyzeResponse>('/analyze', request);
    return response.data;
  }

  /**
   * Get graph data for 3D visualization
   */
  async getGraphData(): Promise<GraphDataResponse> {
    const response = await this.api.get<GraphDataResponse>('/graph-data');
    return response.data;
  }

  /**
   * Get analysis statistics
   */
  async getStatistics(): Promise<Statistics> {
    const response = await this.api.get<Statistics>('/statistics');
    return response.data;
  }

  /**
   * Clear all analysis data
   */
  async clearData(): Promise<{ success: boolean; message: string }> {
    const response = await this.api.delete<{ success: boolean; message: string }>('/clear');
    return response.data;
  }

  /**
   * Refactor a project using AI-powered suggestions
   */
  async refactorProject(request: {
    path: string;
    suggestions_only?: boolean;
    apply_suggestions?: boolean;
  }): Promise<{
    success: boolean;
    message: string;
    suggestions_count: number;
    suggestions: any[];
    original_stats: any;
    refactored_stats: any;
  }> {
    const response = await this.api.post('/refactor', request);
    return response.data;
  }

  /**
   * Get comparison visualization data
   */
  async getComparisonVisualization(projectPath: string): Promise<{
    original: any;
    refactored: any;
    differences: any;
  }> {
    const response = await this.api.get(`/compare-visualization?path=${encodeURIComponent(projectPath)}`);
    return response.data;
  }

  /**
   * Apply selected refactoring suggestions
   */
  async applySuggestions(projectPath: string, suggestionIds: string[]): Promise<{
    success: boolean;
    message: string;
    applied_suggestions: string[];
    modified_files: string[];
  }> {
    const response = await this.api.post('/apply-suggestions', {
      project_path: projectPath,
      suggestion_ids: suggestionIds
    });
    return response.data;
  }

  /**
   * Get refactoring session information
   */
  async getRefactorSession(sessionId: string): Promise<{
    id: string;
    project_path: string;
    status: string;
    start_time: string;
    end_time?: string;
    current_step: string;
    progress_percentage: number;
    messages: string[];
  }> {
    const response = await this.api.get(`/refactor/session/${sessionId}`);
    return response.data;
  }

  /**
   * Get session messages
   */
  async getSessionMessages(sessionId: string, since: number = 0): Promise<{
    session_id: string;
    messages: string[];
    total_count: number;
  }> {
    const response = await this.api.get(`/refactor/session/${sessionId}/messages?since=${since}`);
    return response.data;
  }

  /**
   * Get API information
   */
  async getApiInfo(): Promise<any> {
    const response = await this.api.get('/');
    return response.data;
  }

  /**
   * Test connection to API
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.checkHealth();
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  /**
   * Get base URL for API
   */
  getBaseURL(): string {
    return this.baseURL;
  }

  /**
   * Update base URL
   */
  setBaseURL(url: string): void {
    this.baseURL = url;
    this.api.defaults.baseURL = url;
  }
}

// Create singleton instance
export const apiClient = new CodeWeaverAPI();

// Export default instance as 'api' for convenience
export const api = apiClient;

// Export class for testing or custom instances
export { CodeWeaverAPI };

// Utility functions for common API operations
export const apiUtils = {
  /**
   * Validate project path format
   */
  validateProjectPath(path: string): { valid: boolean; error?: string } {
    if (!path || path.trim().length === 0) {
      return { valid: false, error: 'Project path is required' };
    }

    // Basic path validation
    const invalidChars = /[<>:"|?*]/;
    if (invalidChars.test(path)) {
      return { valid: false, error: 'Project path contains invalid characters' };
    }

    return { valid: true };
  },

  /**
   * Format API error for display
   */
  formatApiError(error: ApiError): string {
    if (error.status === 0) {
      return 'Unable to connect to the API server. Please ensure the server is running.';
    }

    if (error.status === 404) {
      return 'API endpoint not found. Please check the server configuration.';
    }

    if (error.status === 500) {
      return 'Internal server error. Please check the server logs.';
    }

    return error.message || 'An unknown error occurred';
  },

  /**
   * Retry API call with exponential backoff
   */
  async retryApiCall<T>(
    apiCall: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> {
    let lastError: any;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall();
      } catch (error) {
        lastError = error;

        if (attempt === maxRetries) {
          break;
        }

        // Exponential backoff
        const delay = baseDelay * Math.pow(2, attempt);
        console.log(`API call failed, retrying in ${delay}ms... (attempt ${attempt + 1}/${maxRetries})`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  },
};