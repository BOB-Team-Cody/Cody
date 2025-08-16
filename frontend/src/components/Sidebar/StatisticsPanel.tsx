import React from 'react';
import { BarChart3, TrendingUp, AlertCircle, Users } from 'lucide-react';
import { Statistics, AnalyzeResponse } from '@/types';

interface StatisticsPanelProps {
  statistics: Statistics | null;
  analysisResult: AnalyzeResponse | null;
}

const StatisticsPanel: React.FC<StatisticsPanelProps> = ({
  statistics,
  analysisResult,
}) => {
  if (!statistics || !analysisResult) {
    return (
      <div className="p-4 text-center py-8">
        <BarChart3 className="w-12 h-12 mx-auto text-gray-500 mb-4" />
        <p className="text-gray-400">통계 데이터가 없습니다</p>
        <p className="text-sm text-gray-500 mt-2">
          프로젝트를 분석하면 상세한 통계가 표시됩니다
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 h-full overflow-y-auto custom-scrollbar space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-5 h-5 text-cyber-blue" />
            <span className="text-sm font-medium text-gray-300">전체 노드</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {statistics.total_nodes}
          </div>
        </div>
        
        <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-cyber-green" />
            <span className="text-sm font-medium text-gray-300">관계</span>
          </div>
          <div className="text-2xl font-bold text-white">
            {statistics.total_relationships}
          </div>
        </div>
      </div>

      {/* Dead Code Alert */}
      {statistics.dead_code_count > 0 && (
        <div className="bg-red-900 bg-opacity-30 border border-red-500 border-opacity-50 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-sm font-medium text-red-300">Dead Code 현황</span>
          </div>
          <div className="text-lg font-bold text-red-200 mb-2">
            {statistics.dead_code_count}개 발견
          </div>
          <div className="text-sm text-red-300">
            전체의 {((statistics.dead_code_count / statistics.total_nodes) * 100).toFixed(1)}%
          </div>
        </div>
      )}

      {/* Type Distribution */}
      {statistics.by_type && (
        <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
          <h4 className="font-semibold text-white mb-3 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>타입별 분포</span>
          </h4>
          <div className="space-y-2">
            {Object.entries(statistics.by_type).map(([type, count]) => {
              const percentage = (count / statistics.total_nodes) * 100;
              return (
                <div key={type} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300 capitalize">{type}</span>
                    <span className="text-white font-medium">{count}개</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-cyber-blue h-2 rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-400">
                    {percentage.toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Most Called Functions */}
      {statistics.most_called && statistics.most_called.length > 0 && (
        <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
          <h4 className="font-semibold text-white mb-3 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>최다 호출 함수</span>
          </h4>
          <div className="space-y-2">
            {statistics.most_called.slice(0, 5).map((item, index) => (
              <div key={`${item.name}-${index}`} className="flex justify-between items-center p-2 bg-space-800 bg-opacity-50 rounded">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-white truncate">
                    {item.name}
                  </div>
                  <div className="text-xs text-gray-400 truncate">
                    {item.file}
                  </div>
                </div>
                <div className="ml-2 text-right">
                  <div className="text-sm font-bold text-cyber-gold">
                    {item.callCount}회
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Network Metrics */}
      <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
        <h4 className="font-semibold text-white mb-3">네트워크 메트릭</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">평균 연결도:</span>
            <span className="text-white font-medium">
              {(statistics.total_relationships / statistics.total_nodes).toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">네트워크 밀도:</span>
            <span className="text-white font-medium">
              {((2 * statistics.total_relationships) / (statistics.total_nodes * (statistics.total_nodes - 1)) * 100).toFixed(2)}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">분석 완료:</span>
            <span className="text-cyber-green font-medium">✓</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatisticsPanel;