import React, { useState, useRef, useEffect } from 'react';
import { Wrench, Play, AlertCircle, CheckCircle, Copy, GitCompare } from 'lucide-react';

interface RefactoringPanelProps {
  selectedNode: any;
}

interface RefactoringMessage {
  step: string;
  content?: string;
  type?: string;
  result?: any;
  error?: string;
  node?: string;
}

const RefactoringPanel: React.FC<RefactoringPanelProps> = ({ selectedNode }) => {
  const [isRefactoring, setIsRefactoring] = useState(false);
  const [messages, setMessages] = useState<RefactoringMessage[]>([]);
  const [refactoringResult, setRefactoringResult] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'before' | 'after' | 'side-by-side'>('before');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startRefactoring = async () => {
    if (!selectedNode || selectedNode.type !== 'function') {
      return;
    }

    setIsRefactoring(true);
    setMessages([]);
    setRefactoringResult(null);

    try {
      // Close any existing EventSource
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Create new EventSource for streaming
      const eventSource = new EventSource(`http://localhost:8000/refactor?function_id=${encodeURIComponent(selectedNode.id)}`);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'end') {
            setIsRefactoring(false);
            eventSource.close();
            return;
          }

          if (data.type === 'error') {
            setMessages(prev => [...prev, data]);
            setIsRefactoring(false);
            eventSource.close();
            return;
          }

          if (data.type === 'llm_response') {
            setMessages(prev => [...prev, data]);
          } else if (data.type === 'final_result') {
            setRefactoringResult(data.result);
            setMessages(prev => [...prev, {
              step: 'final_result',
              type: 'success',
              content: 'Refactoring completed successfully!'
            }]);
          }

        } catch (error) {
          console.error('Error parsing refactoring message:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        setMessages(prev => [...prev, {
          step: 'stream_error',
          type: 'error',
          error: 'Connection error occurred'
        }]);
        setIsRefactoring(false);
        eventSource.close();
      };

    } catch (error) {
      console.error('Failed to start refactoring:', error);
      setMessages(prev => [...prev, {
        step: 'error',
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }]);
      setIsRefactoring(false);
    }
  };

  const stopRefactoring = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsRefactoring(false);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const renderMessage = (message: RefactoringMessage, index: number) => {
    if (message.type === 'llm_response' && message.content) {
      return (
        <div key={index} className="mb-4 p-4 bg-gray-800 bg-opacity-50 rounded-lg">
          <div className="flex items-center mb-2">
            <div className="w-2 h-2 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
            <span className="text-sm font-medium text-cyan-400">
              {message.step === 'analyze_code' && 'Code Analysis'}
              {message.step === 'generate_suggestions' && 'Generating Suggestions'}
              {message.step === 'refactor_code' && 'Refactoring Code'}
              {message.step === 'validate_refactoring' && 'Validating Results'}
            </span>
          </div>
          <div className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
            {message.content}
          </div>
        </div>
      );
    }

    if (message.type === 'error') {
      return (
        <div key={index} className="mb-4 p-4 bg-red-900 bg-opacity-50 rounded-lg border border-red-500">
          <div className="flex items-center mb-2">
            <AlertCircle className="w-4 h-4 text-red-400 mr-2" />
            <span className="text-sm font-medium text-red-400">Error</span>
          </div>
          <div className="text-sm text-red-300">
            {message.error || message.content}
          </div>
        </div>
      );
    }

    if (message.type === 'success') {
      return (
        <div key={index} className="mb-4 p-4 bg-green-900 bg-opacity-50 rounded-lg border border-green-500">
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
            <span className="text-sm font-medium text-green-400">{message.content}</span>
          </div>
        </div>
      );
    }

    return null;
  };

  const renderCodeComparison = () => {
    if (!refactoringResult) return null;

    const { original_code, refactored_code } = refactoringResult;

    if (viewMode === 'side-by-side') {
      return (
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-300">Original Code</h4>
              <button
                onClick={() => copyToClipboard(original_code)}
                className="p-1 text-gray-400 hover:text-white"
                title="Copy original code"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <pre className="bg-gray-900 p-3 rounded text-xs text-gray-300 overflow-auto max-h-96 border border-gray-700">
              <code>{original_code}</code>
            </pre>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-green-400">Refactored Code</h4>
              <button
                onClick={() => copyToClipboard(refactored_code)}
                className="p-1 text-gray-400 hover:text-white"
                title="Copy refactored code"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <pre className="bg-gray-900 p-3 rounded text-xs text-green-300 overflow-auto max-h-96 border border-green-500">
              <code>{refactored_code}</code>
            </pre>
          </div>
        </div>
      );
    }

    const currentCode = viewMode === 'before' ? original_code : refactored_code;
    const codeTitle = viewMode === 'before' ? 'Original Code' : 'Refactored Code';
    const codeColor = viewMode === 'before' ? 'text-gray-300' : 'text-green-400';
    const borderColor = viewMode === 'before' ? 'border-gray-700' : 'border-green-500';

    return (
      <div className="mt-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className={`text-sm font-medium ${codeColor}`}>{codeTitle}</h4>
          <button
            onClick={() => copyToClipboard(currentCode)}
            className="p-1 text-gray-400 hover:text-white"
            title={`Copy ${codeTitle.toLowerCase()}`}
          >
            <Copy className="w-4 h-4" />
          </button>
        </div>
        <pre className={`bg-gray-900 p-3 rounded text-xs ${codeColor} overflow-auto max-h-96 border ${borderColor}`}>
          <code>{currentCode}</code>
        </pre>
      </div>
    );
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex items-center space-x-3 mb-6">
        <Wrench className="w-5 h-5 text-orange-400" />
        <h2 className="text-lg font-semibold text-white">Code Refactoring</h2>
      </div>

      {!selectedNode || selectedNode.type !== 'function' ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <Wrench className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">Select a function node to start refactoring</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Function Info */}
          <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 mb-4">
            <h3 className="text-sm font-medium text-white mb-1">{selectedNode.name}</h3>
            <p className="text-xs text-gray-400">{selectedNode.file}</p>
            <div className="flex items-center mt-2 space-x-4">
              <span className="text-xs text-gray-500">
                Calls: {selectedNode.callCount || 0}
              </span>
              {selectedNode.dead && (
                <span className="text-xs text-red-400">Dead Code</span>
              )}
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex space-x-2 mb-4">
            <button
              onClick={startRefactoring}
              disabled={isRefactoring}
              className="flex-1 btn-primary text-sm py-2 flex items-center justify-center"
            >
              {isRefactoring ? (
                <>
                  <div className="inline-block w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Refactoring...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start Refactoring
                </>
              )}
            </button>
            
            {isRefactoring && (
              <button
                onClick={stopRefactoring}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg"
              >
                Stop
              </button>
            )}
          </div>

          {/* Code Comparison View Toggle */}
          {refactoringResult && (
            <div className="flex space-x-1 mb-4 p-1 bg-gray-800 rounded-lg">
              <button
                onClick={() => setViewMode('before')}
                className={`flex-1 px-3 py-1 text-xs rounded ${
                  viewMode === 'before' 
                    ? 'bg-gray-600 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Before
              </button>
              <button
                onClick={() => setViewMode('after')}
                className={`flex-1 px-3 py-1 text-xs rounded ${
                  viewMode === 'after' 
                    ? 'bg-green-600 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                After
              </button>
              <button
                onClick={() => setViewMode('side-by-side')}
                className={`flex-1 px-3 py-1 text-xs rounded ${
                  viewMode === 'side-by-side' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <GitCompare className="w-3 h-3 inline mr-1" />
                Compare
              </button>
            </div>
          )}

          {/* Messages and Results */}
          <div className="flex-1 overflow-auto">
            {messages.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-300 mb-3">Refactoring Progress</h4>
                <div className="space-y-2">
                  {messages.map((message, index) => renderMessage(message, index))}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            )}

            {renderCodeComparison()}
          </div>
        </div>
      )}
    </div>
  );
};

export default RefactoringPanel;