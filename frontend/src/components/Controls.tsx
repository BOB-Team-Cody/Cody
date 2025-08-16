import React from 'react';
import { RefreshCw, RotateCcw, Trash2, MoreHorizontal } from 'lucide-react';
import { useClearData, useGraphData, useStatistics } from '@/hooks/useApi';
import { useAppStore } from '@/hooks/useAppStore';

const Controls: React.FC = () => {
  const graphData = useGraphData();
  const statistics = useStatistics();
  const clearData = useClearData();
  const { autoRotate, toggleAutoRotate } = useAppStore();

  const handleRefresh = async () => {
    try {
      await Promise.all([
        graphData.refetch(),
        statistics.refetch()
      ]);
    } catch (error) {
      console.error('Refresh failed:', error);
    }
  };

  const handleClear = async () => {
    if (window.confirm('모든 분석 데이터를 삭제하시겠습니까?')) {
      try {
        await clearData.mutateAsync();
      } catch (error) {
        console.error('Clear failed:', error);
      }
    }
  };

  return (
    <div className="glassmorphism p-3 rounded-xl shadow-2xl">
      <div className="flex items-center space-x-3">
        {/* Refresh Button */}
        <button
          onClick={handleRefresh}
          disabled={graphData.isLoading || statistics.isLoading}
          className="btn-ghost p-2 rounded-lg transition-all duration-200 hover:bg-cyber-blue hover:bg-opacity-20 disabled:opacity-50"
          title="그래프 새로고침"
        >
          <RefreshCw className={`w-5 h-5 ${(graphData.isLoading || statistics.isLoading) ? 'animate-spin' : ''}`} />
        </button>

        {/* Auto-rotate Toggle */}
        <button
          onClick={toggleAutoRotate}
          className={`p-2 rounded-lg transition-all duration-200 ${
            autoRotate 
              ? 'bg-cyber-blue bg-opacity-30 text-cyber-blue' 
              : 'btn-ghost hover:bg-cyber-blue hover:bg-opacity-20'
          }`}
          title={autoRotate ? '자동 회전 끄기' : '자동 회전 켜기'}
        >
          <RotateCcw className="w-5 h-5" />
        </button>

        {/* Clear Data Button */}
        <button
          onClick={handleClear}
          disabled={clearData.isPending}
          className="btn-ghost p-2 rounded-lg transition-all duration-200 hover:bg-red-500 hover:bg-opacity-20 disabled:opacity-50"
          title="데이터 삭제"
        >
          {clearData.isPending ? (
            <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
          ) : (
            <Trash2 className="w-5 h-5" />
          )}
        </button>

        <div className="w-px h-6 bg-gray-600" />

        {/* More Options */}
        <button
          className="btn-ghost p-2 rounded-lg transition-all duration-200"
          title="더 많은 옵션"
        >
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default Controls;