import React, { useState } from 'react';
import { useAppStore } from '@/hooks/useAppStore';
import { api } from '@/services/api';
import RefactorProgress from './RefactorProgress';

interface RefactorSuggestion {
  id: string;
  type: string;
  target_file: string;
  target_element: string;
  description: string;
  original_code: string;
  suggested_code: string;
  confidence: number;
  reasoning: string;
}

interface RefactorResult {
  success: boolean;
  message: string;
  suggestions_count: number;
  suggestions: RefactorSuggestion[];
  original_stats: any;
  refactored_stats: any;
}

const RefactorPanel: React.FC = () => {
  const store = useAppStore();
  const { 
    currentProjectPath, 
    addToast, 
    setComparisonData, 
    setShowComparison 
  } = store;
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [suggestions, setSuggestions] = useState<RefactorSuggestion[]>([]);
  const [selectedSuggestions, setSelectedSuggestions] = useState<Set<string>>(new Set());
  const [refactorResult, setRefactorResult] = useState<RefactorResult | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    try {
      if (addToast) {
        addToast(message, type);
      } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
      }
    } catch (error) {
      console.error('Toast error:', error);
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  };

  const handleRefactorAnalysis = async () => {
    console.log('handleRefactorAnalysis called');
    console.log('currentProjectPath:', currentProjectPath);
    
    if (!currentProjectPath) {
      showToast('Please analyze a project first', 'error');
      return;
    }

    setIsAnalyzing(true);
    try {
      console.log('Calling api.refactorProject with path:', currentProjectPath);
      const response = await api.refactorProject({
        path: currentProjectPath,
        suggestions_only: true,
        apply_suggestions: false
      });

      console.log('Refactor response:', response);

      if (response.success) {
        setSuggestions(response.suggestions);
        setRefactorResult(response);
        setCurrentSessionId(response.session_id);
        showToast(`Found ${response.suggestions_count} refactoring suggestions`, 'success');
      } else {
        showToast(response.message, 'error');
        setCurrentSessionId(response.session_id); // Still set session ID for error tracking
      }
    } catch (error) {
      console.error('Refactoring analysis failed:', error);
      showToast('Failed to analyze project for refactoring', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleProgressComplete = () => {
    console.log('Refactoring progress completed');
    setIsAnalyzing(false);
    // Optionally refresh suggestions or perform other actions
  };

  const handleShowComparison = async () => {
    if (!currentProjectPath) {
      showToast('Please analyze a project first', 'error');
      return;
    }

    try {
      const comparisonData = await api.getComparisonVisualization(currentProjectPath);
      setComparisonData(comparisonData);
      setShowComparison(true);
      showToast('Comparison visualization loaded', 'success');
    } catch (error) {
      console.error('Failed to load comparison:', error);
      showToast('Failed to load comparison visualization', 'error');
    }
  };

  const toggleSuggestionSelection = (suggestionId: string) => {
    const newSelected = new Set(selectedSuggestions);
    if (newSelected.has(suggestionId)) {
      newSelected.delete(suggestionId);
    } else {
      newSelected.add(suggestionId);
    }
    setSelectedSuggestions(newSelected);
  };

  const handleApplySuggestions = async () => {
    if (selectedSuggestions.size === 0) {
      showToast('Please select suggestions to apply', 'warning');
      return;
    }

    try {
      const result = await api.applySuggestions(
        currentProjectPath,
        Array.from(selectedSuggestions)
      );

      if (result.success) {
        showToast(`Applied ${selectedSuggestions.size} suggestions`, 'success');
        setSelectedSuggestions(new Set());
        // Refresh the analysis
        handleRefactorAnalysis();
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      console.error('Failed to apply suggestions:', error);
      showToast('Failed to apply suggestions', 'error');
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'dead_code':
        return '🗑️';
      case 'high_usage':
        return '⚡';
      case 'potential_extraction':
        return '📦';
      default:
        return '🔧';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Refactoring</h2>
        <button
          onClick={handleRefactorAnalysis}
          disabled={isAnalyzing || !currentProjectPath}
          className="px-3 py-1 bg-cyber-blue text-white rounded hover:bg-cyber-blue-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {/* Progress Tracking */}
      {currentSessionId && (
        <RefactorProgress 
          sessionId={currentSessionId} 
          onComplete={handleProgressComplete}
        />
      )}

      {/* Statistics */}
      {refactorResult && (
        <div className="glassmorphism p-3 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">Analysis Results</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span>Suggestions Found:</span>
              <span className="text-cyber-blue">{refactorResult.suggestions_count}</span>
            </div>
            <div className="flex justify-between">
              <span>Selected:</span>
              <span className="text-green-400">{selectedSuggestions.size}</span>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {suggestions.length > 0 && (
        <div className="space-y-2">
          <button
            onClick={handleShowComparison}
            className="w-full px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors text-sm"
          >
            Show Visual Comparison
          </button>
          
          {selectedSuggestions.size > 0 && (
            <button
              onClick={handleApplySuggestions}
              className="w-full px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-sm"
            >
              Apply Selected ({selectedSuggestions.size})
            </button>
          )}
        </div>
      )}

      {/* Suggestions List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {suggestions.map((suggestion) => (
          <div
            key={suggestion.id}
            className="glassmorphism p-3 rounded-lg cursor-pointer hover:bg-opacity-80 transition-all"
            onClick={() => toggleSuggestionSelection(suggestion.id)}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getTypeIcon(suggestion.type)}</span>
                <div className="flex-1">
                  <div className="text-sm font-medium text-white">
                    {suggestion.target_element}
                  </div>
                  <div className="text-xs text-gray-400">
                    {suggestion.target_file}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-medium ${getConfidenceColor(suggestion.confidence)}`}>
                  {Math.round(suggestion.confidence * 100)}%
                </span>
                <input
                  type="checkbox"
                  checked={selectedSuggestions.has(suggestion.id)}
                  onChange={() => toggleSuggestionSelection(suggestion.id)}
                  className="rounded border-gray-600 bg-space-700 text-cyber-blue focus:ring-cyber-blue focus:ring-offset-0"
                />
              </div>
            </div>

            <div className="text-xs text-gray-300 mb-2">
              {suggestion.description}
            </div>

            <div className="text-xs text-gray-400">
              {suggestion.reasoning}
            </div>

            {/* Code Preview */}
            <details className="mt-2">
              <summary className="text-xs text-cyber-blue cursor-pointer hover:text-cyber-blue-light">
                View Code Changes
              </summary>
              <div className="mt-2 space-y-2">
                <div>
                  <div className="text-xs text-gray-400 mb-1">Original:</div>
                  <pre className="text-xs bg-red-900 bg-opacity-20 p-2 rounded border-l-2 border-red-500 overflow-x-auto">
                    {suggestion.original_code.substring(0, 200)}
                    {suggestion.original_code.length > 200 && '...'}
                  </pre>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Suggested:</div>
                  <pre className="text-xs bg-green-900 bg-opacity-20 p-2 rounded border-l-2 border-green-500 overflow-x-auto">
                    {suggestion.suggested_code.substring(0, 200)}
                    {suggestion.suggested_code.length > 200 && '...'}
                  </pre>
                </div>
              </div>
            </details>
          </div>
        ))}
      </div>

      {suggestions.length === 0 && !isAnalyzing && (
        <div className="text-center text-gray-400 py-8">
          <div className="text-lg mb-2">🔧</div>
          <div className="text-sm">No refactoring suggestions</div>
          <div className="text-xs">Run analysis to find opportunities</div>
        </div>
      )}
    </div>
  );
};

export default RefactorPanel;