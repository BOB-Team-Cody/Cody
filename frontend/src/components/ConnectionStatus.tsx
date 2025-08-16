import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

interface ConnectionStatusProps {
  connected: boolean;
  loading: boolean;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  connected, 
  loading 
}) => {
  if (loading) {
    return (
      <div className="glassmorphism p-2 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-gray-400">연결 중...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`glassmorphism p-2 rounded-lg ${connected ? 'border-green-500' : 'border-red-500'} border-opacity-50`}>
      <div className="flex items-center space-x-2">
        {connected ? (
          <>
            <Wifi className="w-4 h-4 text-green-400" />
            <span className="text-xs text-green-400">API 연결됨</span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4 text-red-400" />
            <span className="text-xs text-red-400">API 연결 끊김</span>
          </>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatus;