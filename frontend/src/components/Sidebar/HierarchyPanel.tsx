import React from 'react';
import { GitBranch, Activity, Settings, BarChart3 } from 'lucide-react';
import { AnalyzeResponse, NodeData } from '@/types';
import { useAppStore } from '@/hooks/useAppStore';

interface HierarchyPanelProps {
  analysisResult: AnalyzeResponse | null;
  selectedNode: NodeData | null;
  isAnalyzing: boolean;
}

const HierarchyPanel: React.FC<HierarchyPanelProps> = ({
  analysisResult,
  selectedNode,
  isAnalyzing,
}) => {
  const { layoutMode, setLayoutMode } = useAppStore();

  const handleLayoutChange = (mode: 'force-directed' | 'hierarchical') => {
    setLayoutMode(mode);
  };

  if (isAnalyzing) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="text-center">
          <div className="inline-block w-8 h-8 mb-4 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" />
          <div className="text-lg font-semibold text-white mb-2">분석 중...</div>
          <div className="text-sm text-gray-400">계층 구조를 생성하고 있습니다</div>
        </div>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="text-center">
          <GitBranch className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <div className="text-lg font-semibold text-gray-400 mb-2">계층 뷰</div>
          <div className="text-sm text-gray-500">
            프로젝트를 분석하면 함수 호출 계층이 표시됩니다
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-white border-opacity-10">
        <div className="flex items-center space-x-3 mb-4">
          <GitBranch className="w-5 h-5 text-cyber-blue" />
          <h2 className="text-lg font-semibold text-white">계층 뷰</h2>
        </div>
        
        {/* Layout Mode Selector */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-300">
            <Settings className="w-4 h-4 inline mr-2" />
            레이아웃 모드
          </label>
          <div className="grid grid-cols-1 gap-2">
            <button
              onClick={() => handleLayoutChange('force-directed')}
              className={`
                p-3 rounded-lg border text-left transition-all duration-200
                ${layoutMode === 'force-directed'
                  ? 'border-cyber-blue bg-cyber-blue bg-opacity-20 text-white'
                  : 'border-gray-600 text-gray-300 hover:border-gray-500'
                }
              `}
            >
              <div className="font-medium text-sm">Force-Directed</div>
              <div className="text-xs opacity-75">자유로운 네트워크 구조</div>
            </button>
            
            <button
              onClick={() => handleLayoutChange('hierarchical')}
              className={`
                p-3 rounded-lg border text-left transition-all duration-200
                ${layoutMode === 'hierarchical'
                  ? 'border-cyber-blue bg-cyber-blue bg-opacity-20 text-white'
                  : 'border-gray-600 text-gray-300 hover:border-gray-500'
                }
              `}
            >
              <div className="font-medium text-sm">계층형 (Hierarchical)</div>
              <div className="text-xs opacity-75">호출 깊이별 세로 배치</div>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 custom-scrollbar">
        {/* Layout Info */}
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <Activity className="w-4 h-4 text-cyber-green" />
            <span className="text-sm font-medium text-gray-300">현재 레이아웃</span>
          </div>
          <div className="bg-space-700 p-4 rounded-lg">
            <div className="text-sm text-white font-medium mb-2">
              {layoutMode === 'force-directed' ? 'Force-Directed Layout' : 'Hierarchical Layout'}
            </div>
            <div className="text-xs text-gray-400">
              {layoutMode === 'force-directed' 
                ? '노드들이 자연스럽게 연결 관계에 따라 배치됩니다. 전체적인 네트워크 구조를 파악하는데 유용합니다.'
                : '함수 호출 깊이에 따라 계층적으로 배치됩니다. 엔트리포인트부터 깊은 호출까지의 흐름을 추적할 수 있습니다.'
              }
            </div>
          </div>
        </div>

        {/* Selected Node Info */}
        {selectedNode && (
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-4 h-4 bg-cyber-blue rounded-full" />
              <span className="text-sm font-medium text-gray-300">선택된 노드</span>
            </div>
            <div className="bg-space-700 p-4 rounded-lg">
              <div className="text-sm text-white font-medium mb-2">{selectedNode.name}</div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>타입: {selectedNode.type}</div>
                <div>파일: {selectedNode.file}</div>
                <div>호출 횟수: {selectedNode.callCount}</div>
                {selectedNode.dead && (
                  <div className="text-red-400 font-medium">⚠️ Dead Code</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-cyber-purple" />
            <span className="text-sm font-medium text-gray-300">구조 정보</span>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-space-700 p-3 rounded-lg">
              <div className="text-lg font-bold text-white">{analysisResult.nodes_count}</div>
              <div className="text-xs text-gray-400">노드</div>
            </div>
            <div className="bg-space-700 p-3 rounded-lg">
              <div className="text-lg font-bold text-white">{analysisResult.edges_count}</div>
              <div className="text-xs text-gray-400">연결</div>
            </div>
          </div>
        </div>

        {/* Usage Tips */}
        <div className="mt-8 p-4 bg-space-800 rounded-lg border border-gray-700">
          <div className="text-sm font-medium text-gray-300 mb-2">💡 사용 팁</div>
          <ul className="text-xs text-gray-400 space-y-1">
            <li>• 계층형 뷰는 코드 호출 흐름을 추적하는데 최적화되어 있습니다</li>
            <li>• 노드 클릭으로 해당 함수의 코드를 확인할 수 있습니다</li>
            <li>• 엣지의 두께는 호출 빈도를 나타냅니다</li>
            <li>• 색상은 모듈별로 구분되어 표시됩니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HierarchyPanel;