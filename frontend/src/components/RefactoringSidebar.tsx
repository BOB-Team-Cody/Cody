import React, { useState, useEffect, useRef } from 'react';
import { X, Play, Eye, CheckCircle, AlertCircle, Clock, Settings } from 'lucide-react';
import { useAppStore } from '@/hooks/useAppStore';
import { api } from '@/services/api';

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

interface SessionData {
  id: string;
  project_path: string;
  status: string;
  start_time: string;
  end_time?: string;
  current_step: string;
  progress_percentage: number;
  messages: string[];
}

interface RefactoringSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const RefactoringSidebar: React.FC<RefactoringSidebarProps> = ({ isOpen, onClose }) => {
  const { currentProjectPath, addToast, setComparisonData, setShowComparison } = useAppStore();
  
  // State management
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [session, setSession] = useState<SessionData | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<RefactorSuggestion[]>([]);
  const [selectedSuggestions, setSelectedSuggestions] = useState<Set<string>>(new Set());
  const [lastMessageCount, setLastMessageCount] = useState(0);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end'
      });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Polling for session updates
  const pollSessionData = async () => {
    if (!currentSessionId) return;

    try {
      // Get session info
      const sessionData = await api.getRefactorSession(currentSessionId);
      setSession(sessionData);

      // Get new messages
      const messagesData = await api.getSessionMessages(currentSessionId, lastMessageCount);
      if (messagesData.messages.length > 0) {
        setMessages(prev => [...prev, ...messagesData.messages]);
        setLastMessageCount(messagesData.total_count);
      }

      // Check if session is complete
      if (sessionData.status === 'completed' || sessionData.status === 'failed') {
        setIsAnalyzing(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    } catch (error) {
      console.error('Error polling session data:', error);
    }
  };

  useEffect(() => {
    if (currentSessionId && isAnalyzing) {
      // Start polling
      intervalRef.current = setInterval(pollSessionData, 500); // Poll every 500ms for smooth updates
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [currentSessionId, isAnalyzing]);

  // Toast helper
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

  // Start refactoring analysis
  const handleStartRefactoring = async () => {
    if (!currentProjectPath) {
      showToast('Please analyze a project first', 'error');
      return;
    }

    setIsAnalyzing(true);
    setMessages([]);
    setLastMessageCount(0);
    setSuggestions([]);
    setSelectedSuggestions(new Set());

    try {
      const response = await api.refactorProject({
        path: currentProjectPath,
        suggestions_only: true,
        apply_suggestions: false
      });

      if (response.success) {
        setSuggestions(response.suggestions);
        setCurrentSessionId(response.session_id);
        showToast(`Found ${response.suggestions_count} refactoring suggestions`, 'success');
      } else {
        showToast(response.message, 'error');
        setCurrentSessionId(response.session_id);
      }
    } catch (error) {
      console.error('Refactoring analysis failed:', error);
      showToast('Failed to analyze project for refactoring', 'error');
      setIsAnalyzing(false);
    }
  };

  // Show comparison
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

  // Toggle suggestion selection
  const toggleSuggestionSelection = (suggestionId: string) => {
    const newSelected = new Set(selectedSuggestions);
    if (newSelected.has(suggestionId)) {
      newSelected.delete(suggestionId);
    } else {
      newSelected.add(suggestionId);
    }
    setSelectedSuggestions(newSelected);
  };

  // Apply suggestions
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
      } else {
        showToast(result.message, 'error');
      }
    } catch (error) {
      console.error('Failed to apply suggestions:', error);
      showToast('Failed to apply suggestions', 'error');
    }
  };

  // Utility functions
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-400';
      case 'completed': return 'text-green-400';
      case 'failed': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Clock className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'dead_code': return '🗑️';
      case 'high_usage': return '⚡';
      case 'potential_extraction': return '📦';
      case 'unused_function': return '❓';
      case 'large_module': return '📁';
      default: return '🔧';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed top-0 right-0 h-full w-96 bg-space-900 border-l border-gray-700 shadow-2xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-space-800">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-cyber-blue" />
          <h2 className="text-lg font-bold text-white">Code Refactoring</h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-700 rounded transition-colors"
        >
          <X className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
      </div>

      {/* Control Panel */}
      <div className="p-4 border-b border-gray-700 bg-space-850">
        <div className="space-y-3">
          {/* Project Info */}
          <div className="text-sm">
            <span className="text-gray-400">Project:</span>
            <div className="text-white font-mono text-xs mt-1 truncate">
              {currentProjectPath || 'No project selected'}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-2">
            <button
              onClick={handleStartRefactoring}
              disabled={isAnalyzing || !currentProjectPath}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-cyber-blue text-white rounded hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" />
              <span>{isAnalyzing ? 'Analyzing...' : 'Start Refactoring'}</span>
            </button>

            {suggestions.length > 0 && (
              <button
                onClick={handleShowComparison}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
              >
                <Eye className="w-4 h-4" />
                <span>Show Comparison</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Progress Section */}
      {session && (
        <div className="p-4 border-b border-gray-700 bg-space-850">
          <div className="space-y-3">
            {/* Status */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Status:</span>
              <div className={`flex items-center space-x-1 text-sm ${getStatusColor(session.status)}`}>
                {getStatusIcon(session.status)}
                <span className="capitalize">{session.status}</span>
              </div>
            </div>

            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>{session.current_step}</span>
                <span>{session.progress_percentage}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-cyber-blue to-purple-500 h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${session.progress_percentage}%` }}
                />
              </div>
            </div>

            {/* Time Info */}
            <div className="text-xs text-gray-400">
              <div>Started: {new Date(session.start_time).toLocaleTimeString()}</div>
              {session.end_time && (
                <div>Completed: {new Date(session.end_time).toLocaleTimeString()}</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages Section */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="p-3 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-white">Live Progress</h3>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 bg-black bg-opacity-20">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 italic py-8">
              {isAnalyzing ? 'Starting analysis...' : 'Click "Start Refactoring" to begin'}
            </div>
          ) : (
            <div className="space-y-1">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className="text-xs font-mono text-gray-300 hover:text-white transition-colors p-1 rounded hover:bg-gray-800"
                >
                  {message}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Suggestions Section */}
      {suggestions.length > 0 && (
        <div className="border-t border-gray-700 bg-space-850">
          <div className="p-3 border-b border-gray-600">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Suggestions ({suggestions.length})
              </h3>
              {selectedSuggestions.size > 0 && (
                <button
                  onClick={handleApplySuggestions}
                  className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition-colors"
                >
                  Apply ({selectedSuggestions.size})
                </button>
              )}
            </div>
          </div>
          
          <div className="max-h-64 overflow-y-auto p-3 space-y-2">
            {suggestions.slice(0, 10).map((suggestion) => ( // Show top 10 suggestions
              <div
                key={suggestion.id}
                className="glassmorphism p-2 rounded cursor-pointer hover:bg-opacity-80 transition-all text-xs"
                onClick={() => toggleSuggestionSelection(suggestion.id)}
              >
                <div className="flex items-start justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">{getTypeIcon(suggestion.type)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-white font-medium truncate">
                        {suggestion.target_element}
                      </div>
                      <div className="text-gray-400 truncate">
                        {suggestion.target_file}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <span className={`text-xs font-medium ${getConfidenceColor(suggestion.confidence)}`}>
                      {Math.round(suggestion.confidence * 100)}%
                    </span>
                    <input
                      type="checkbox"
                      checked={selectedSuggestions.has(suggestion.id)}
                      onChange={() => toggleSuggestionSelection(suggestion.id)}
                      className="rounded border-gray-600 bg-space-700 text-cyber-blue focus:ring-cyber-blue focus:ring-offset-0"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                </div>

                <div className="text-gray-300 mb-1">
                  {suggestion.description}
                </div>

                <div className="text-gray-400">
                  {suggestion.reasoning}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RefactoringSidebar;