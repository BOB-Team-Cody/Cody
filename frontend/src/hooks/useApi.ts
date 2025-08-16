import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { apiClient, apiUtils } from '@/services/api';
import { useAppStore } from './useAppStore';
import {
  AnalyzeRequest,
  AnalyzeResponse,
  ApiError,
} from '@/types';

// Query keys
export const queryKeys = {
  health: ['health'] as const,
  graphData: ['graphData'] as const,
  statistics: ['statistics'] as const,
} as const;

/**
 * Hook for API health check
 */
export const useHealthCheck = () => {
  const setApiConnected = useAppStore((state) => state.setApiConnected);
  
  const query = useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.checkHealth(),
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  });

  useEffect(() => {
    if (query.data) {
      setApiConnected(query.data.status === 'healthy' || query.data.status === 'degraded');
    } else if (query.error) {
      setApiConnected(false);
    }
  }, [query.data, query.error, setApiConnected]);

  return query;
};

/**
 * Hook for analyzing a project
 */
export const useAnalyzeProject = () => {
  const queryClient = useQueryClient();
  const { setIsAnalyzing, setLastError, setAnalysisResult } = useAppStore();
  
  return useMutation({
    mutationFn: (request: AnalyzeRequest) => {
      // Validate request before sending
      const validation = apiUtils.validateProjectPath(request.path);
      if (!validation.valid) {
        throw new Error(validation.error || 'Invalid project path');
      }
      
      setIsAnalyzing(true);
      setLastError(null);
      
      return apiClient.analyzeProject(request);
    },
    onMutate: () => {
      setIsAnalyzing(true);
      setLastError(null);
    },
    onSuccess: (data: AnalyzeResponse) => {
      setAnalysisResult(data);
      setIsAnalyzing(false);
      
      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({ queryKey: queryKeys.graphData });
      queryClient.invalidateQueries({ queryKey: queryKeys.statistics });
    },
    onError: (error: ApiError) => {
      setIsAnalyzing(false);
      setLastError(error.message || 'Analysis failed');
      console.error('Analysis error:', error);
    },
  });
};

/**
 * Hook for getting graph data
 */
export const useGraphData = () => {
  const setGraphData = useAppStore((state) => state.setGraphData);
  
  const query = useQuery({
    queryKey: queryKeys.graphData,
    queryFn: () => apiClient.getGraphData(),
    enabled: false, // Only fetch when explicitly triggered
    retry: 2,
  });

  useEffect(() => {
    if (query.data) {
      setGraphData(query.data);
    }
  }, [query.data, setGraphData]);

  return query;
};

/**
 * Hook for getting statistics
 */
export const useStatistics = () => {
  const setStatistics = useAppStore((state) => state.setStatistics);
  
  const query = useQuery({
    queryKey: queryKeys.statistics,
    queryFn: () => apiClient.getStatistics(),
    enabled: false, // Only fetch when explicitly triggered
    retry: 2,
  });

  useEffect(() => {
    if (query.data) {
      setStatistics(query.data);
    }
  }, [query.data, setStatistics]);

  return query;
};

/**
 * Hook for clearing analysis data
 */
export const useClearData = () => {
  const queryClient = useQueryClient();
  const { setAnalysisResult, setGraphData, setStatistics, setSelectedNode } = useAppStore();
  
  return useMutation({
    mutationFn: () => apiClient.clearData(),
    onSuccess: () => {
      // Clear store state
      setAnalysisResult(null);
      setGraphData(null);
      setStatistics(null);
      setSelectedNode(null);
      
      // Clear query cache
      queryClient.invalidateQueries({ queryKey: queryKeys.graphData });
      queryClient.invalidateQueries({ queryKey: queryKeys.statistics });
    },
  });
};

/**
 * Combined hook for analysis workflow
 */
export const useAnalysisWorkflow = () => {
  const analyzeProject = useAnalyzeProject();
  const graphData = useGraphData();
  const statistics = useStatistics();
  
  const runAnalysis = async (projectPath: string) => {
    try {
      // Start analysis
      const result = await analyzeProject.mutateAsync({ path: projectPath });
      
      // If analysis was successful, fetch related data
      if (result.success) {
        // Fetch graph data and statistics
        await Promise.all([
          graphData.refetch(),
          statistics.refetch(),
        ]);
      }
      
      return result;
    } catch (error) {
      console.error('Analysis workflow error:', error);
      throw error;
    }
  };
  
  return {
    runAnalysis,
    isAnalyzing: analyzeProject.isPending,
    error: analyzeProject.error,
  };
};

/**
 * Hook for API connection status
 */
export const useApiStatus = () => {
  const healthCheck = useHealthCheck();
  const apiConnected = useAppStore((state) => state.apiConnected);
  
  return {
    connected: apiConnected,
    loading: healthCheck.isLoading,
    error: healthCheck.error,
    lastChecked: healthCheck.dataUpdatedAt,
  };
};