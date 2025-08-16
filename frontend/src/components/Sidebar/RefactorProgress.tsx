import React, { useState, useEffect, useRef } from 'react';
import { api } from '@/services/api';

interface RefactorProgressProps {
  sessionId: string | null;
  onComplete?: () => void;
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

const RefactorProgress: React.FC<RefactorProgressProps> = ({ sessionId, onComplete }) => {
  const [session, setSession] = useState<SessionData | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [lastMessageCount, setLastMessageCount] = useState(0);
  const [isPolling, setIsPolling] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const pollSessionData = async () => {
    if (!sessionId) return;

    try {
      // Get session info
      const sessionData = await api.getRefactorSession(sessionId);
      setSession(sessionData);

      // Get new messages
      const messagesData = await api.getSessionMessages(sessionId, lastMessageCount);
      if (messagesData.messages.length > 0) {
        setMessages(prev => [...prev, ...messagesData.messages]);
        setLastMessageCount(messagesData.total_count);
      }

      // Check if session is complete
      if (sessionData.status === 'completed' || sessionData.status === 'failed') {
        setIsPolling(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        if (onComplete) {
          onComplete();
        }
      }
    } catch (error) {
      console.error('Error polling session data:', error);
    }
  };

  useEffect(() => {
    if (sessionId && !isPolling) {
      setIsPolling(true);
      setMessages([]);
      setLastMessageCount(0);
      
      // Start polling
      pollSessionData(); // Initial call
      intervalRef.current = setInterval(pollSessionData, 1000); // Poll every second
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setIsPolling(false);
    };
  }, [sessionId]);

  if (!sessionId || !session) {
    return null;
  }

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
      case 'running': return '⚙️';
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  return (
    <div className="glassmorphism p-4 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Refactoring Progress</h3>
        <span className={`text-xs ${getStatusColor(session.status)}`}>
          {getStatusIcon(session.status)} {session.status.toUpperCase()}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
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

      {/* Messages */}
      <div className="space-y-2">
        <div className="text-xs text-gray-400 mb-2">Live Updates:</div>
        <div className="bg-black bg-opacity-30 rounded p-3 max-h-60 overflow-y-auto text-xs font-mono">
          {messages.length === 0 ? (
            <div className="text-gray-500 italic">Waiting for updates...</div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className="mb-1 text-gray-300 hover:text-white transition-colors"
                >
                  {message}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Session Info */}
      <div className="mt-4 pt-3 border-t border-gray-600">
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
          <div>
            <span className="text-gray-500">Started:</span>
            <div className="text-white">
              {new Date(session.start_time).toLocaleTimeString()}
            </div>
          </div>
          {session.end_time && (
            <div>
              <span className="text-gray-500">Completed:</span>
              <div className="text-white">
                {new Date(session.end_time).toLocaleTimeString()}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Auto-refresh indicator */}
      {isPolling && (
        <div className="mt-2 flex items-center justify-center">
          <div className="animate-pulse text-xs text-gray-500">
            <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-2"></span>
            Live updates active
          </div>
        </div>
      )}
    </div>
  );
};

export default RefactorProgress;