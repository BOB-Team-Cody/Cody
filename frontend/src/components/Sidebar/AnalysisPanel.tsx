import React from 'react';
import { FileCode, Package, Zap, Skull, Clock } from 'lucide-react';
import { AnalyzeResponse, NodeData } from '@/types';

interface AnalysisPanelProps {
  analysisResult: AnalyzeResponse | null;
  selectedNode: NodeData | null;
  isAnalyzing: boolean;
}

const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  analysisResult,
  selectedNode,
  isAnalyzing,
}) => {
  // Render analysis overview
  const renderAnalysisOverview = () => {
    if (isAnalyzing) {
      return (
        <div className="text-center py-8">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-cyber-blue border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-300">프로젝트를 분석하고 있습니다<span className="loading-dots"></span></p>
          <p className="text-sm text-gray-500 mt-2">3D 우주가 곧 생성됩니다</p>
        </div>
      );
    }
    
    if (!analysisResult) {
      return (
        <div className="text-center py-8">
          <div className="text-6xl mb-4">🌌</div>
          <p className="text-gray-300 mb-2">코드 우주 분석 준비</p>
          <p className="text-sm text-gray-500">
            Python 프로젝트 경로를 입력하고 분석을 시작하세요
          </p>
          <div className="mt-6 p-4 bg-space-700 bg-opacity-50 rounded-lg text-left text-sm">
            <h4 className="font-semibold text-white mb-2">분석 결과:</h4>
            <ul className="space-y-1 text-gray-400">
              <li>🌟 <strong>밝은 노드</strong>: 많이 호출되는 함수</li>
              <li>💀 <strong>빨간 노드</strong>: 사용되지 않는 코드</li>
              <li>🔗 <strong>연결선</strong>: 함수 호출 관계</li>
              <li>🎯 <strong>클릭</strong>: 노드 상세 정보</li>
            </ul>
          </div>
        </div>
      );
    }
    
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Package className="w-5 h-5 text-cyber-blue" />
              <span className="text-sm font-medium text-gray-300">노드</span>
            </div>
            <div className="text-2xl font-bold text-white">
              {analysisResult.nodes_count}
            </div>
          </div>
          
          <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="w-5 h-5 text-cyber-gold" />
              <span className="text-sm font-medium text-gray-300">연결</span>
            </div>
            <div className="text-2xl font-bold text-white">
              {analysisResult.edges_count}
            </div>
          </div>
        </div>
        
        {analysisResult.statistics.dead_code_count > 0 && (
          <div className="bg-red-900 bg-opacity-30 border border-red-500 border-opacity-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Skull className="w-5 h-5 text-red-400" />
              <span className="text-sm font-medium text-red-300">Dead Code 발견</span>
            </div>
            <div className="text-lg font-bold text-red-200">
              {analysisResult.statistics.dead_code_count}개 항목
            </div>
            <p className="text-sm text-red-300 mt-1">
              사용되지 않는 코드가 발견되었습니다. 정리를 고려해보세요.
            </p>
          </div>
        )}
        
        <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
          <h4 className="font-semibold text-white mb-3">✨ 분석 완료!</h4>
          <p className="text-sm text-gray-300 mb-2">
            {analysisResult.message}
          </p>
          <p className="text-xs text-gray-500">
            3D 우주에서 노드를 클릭하여 자세한 정보를 확인하세요.
          </p>
        </div>
      </div>
    );
  };
  
  // Render selected node details
  const renderNodeDetails = () => {
    if (!selectedNode) {
      return null;
    }
    
    const callCount = selectedNode.callCount || 0;
    const isDead = selectedNode.dead;
    const isUnused = callCount === 0 && !isDead;
    const isHighUsage = callCount > 3;
    
    let statusInfo = {
      text: '',
      icon: <FileCode className="w-5 h-5" />,
      bgColor: 'bg-blue-900',
      borderColor: 'border-blue-500',
      textColor: 'text-blue-200',
    };
    
    if (isDead) {
      statusInfo = {
        text: '⚠️ 데드 코드 (vulture 분석)',
        icon: <Skull className="w-5 h-5" />,
        bgColor: 'bg-red-900',
        borderColor: 'border-red-500',
        textColor: 'text-red-200',
      };
    } else if (isHighUsage) {
      statusInfo = {
        text: '🔥 자주 사용되는 핵심 함수',
        icon: <Zap className="w-5 h-5" />,
        bgColor: 'bg-yellow-900',
        borderColor: 'border-yellow-500',
        textColor: 'text-yellow-200',
      };
    } else if (isUnused) {
      statusInfo = {
        text: '💤 호출 안됨 (필요한 코드)',
        icon: <Clock className="w-5 h-5" />,
        bgColor: 'bg-gray-700',
        borderColor: 'border-gray-500',
        textColor: 'text-gray-300',
      };
    } else if (selectedNode.type === 'class') {
      statusInfo = {
        text: '🏗️ 클래스 정의',
        icon: <Package className="w-5 h-5" />,
        bgColor: 'bg-purple-900',
        borderColor: 'border-purple-500',
        textColor: 'text-purple-200',
      };
    }
    
    return (
      <div className="mt-6 space-y-4">
        <div className="border-t border-white border-opacity-10 pt-4">
          <h4 className="font-semibold text-white mb-3 flex items-center space-x-2">
            <span>🎯 선택된 노드</span>
          </h4>
        </div>
        
        <div className="space-y-3">
          <div className="bg-space-700 bg-opacity-50 p-4 rounded-lg">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">이름:</span>
                <span className="text-sm font-medium text-white">{selectedNode.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">타입:</span>
                <span className="text-sm text-white capitalize">{selectedNode.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">파일:</span>
                <span className="text-sm text-white truncate max-w-48" title={selectedNode.file}>
                  {selectedNode.file}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-400">호출 횟수:</span>
                <span className="text-sm font-bold text-white">{callCount}회</span>
              </div>
            </div>
          </div>
          
          <div className={`${statusInfo.bgColor} bg-opacity-30 border ${statusInfo.borderColor} border-opacity-50 p-4 rounded-lg`}>
            <div className={`flex items-center space-x-2 mb-2 ${statusInfo.textColor}`}>
              {statusInfo.icon}
              <span className="text-sm font-medium">상태</span>
            </div>
            <p className={`text-sm ${statusInfo.textColor}`}>
              {statusInfo.text}
            </p>
            
            {isDead && (
              <div className="mt-3 p-2 bg-red-800 bg-opacity-50 rounded text-xs text-red-200">
                ⚠️ 이 코드는 실제로 사용되지 않습니다. 제거를 고려해보세요.
              </div>
            )}
            
            {isUnused && (
              <div className="mt-3 p-2 bg-gray-600 bg-opacity-50 rounded text-xs text-gray-300">
                💡 AST에서 호출이 감지되지 않았지만, vulture는 필요한 코드라고 판단했습니다.
              </div>
            )}
            
            {isHighUsage && (
              <div className="mt-3 p-2 bg-yellow-800 bg-opacity-50 rounded text-xs text-yellow-200">
                🚀 이 함수는 프로젝트의 핵심 로직입니다.
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="p-4 h-full overflow-y-auto custom-scrollbar">
      {renderAnalysisOverview()}
      {renderNodeDetails()}
    </div>
  );
};

export default AnalysisPanel;