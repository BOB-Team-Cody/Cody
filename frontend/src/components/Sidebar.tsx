import React, { useState } from 'react';
import { Search, BarChart3, FileText, GitBranch, Wrench } from 'lucide-react';
import { useAppStore } from '@/hooks/useAppStore';
import { useAnalysisWorkflow } from '@/hooks/useApi';
import AnalysisPanel from './Sidebar/AnalysisPanel';
import StatisticsPanel from './Sidebar/StatisticsPanel';
import CodePanel from './Sidebar/CodePanel';
import HierarchyPanel from './Sidebar/HierarchyPanel';
import RefactoringPanel from './Sidebar/RefactoringPanel';

const Sidebar: React.FC = () => {
  const {
    sidebarOpen,
    activeTab,
    setActiveTab,
    selectedNode,
    isAnalyzing,
    analysisResult,
    statistics,
  } = useAppStore();
  
  const { runAnalysis } = useAnalysisWorkflow();
  const [projectPath, setProjectPath] = useState('sample_project');
  
  const handleAnalyze = async () => {
    if (!projectPath.trim()) {
      return;
    }
    
    try {
      await runAnalysis(projectPath.trim());
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };
  
  const tabs = [
    { id: 'analysis' as const, label: '분석 결과', icon: Search },
    { id: 'hierarchy' as const, label: '계층 뷰', icon: GitBranch },
    { id: 'stats' as const, label: '통계', icon: BarChart3 },
    { id: 'code' as const, label: '코드', icon: FileText },
    { id: 'refactoring' as const, label: '리팩토링', icon: Wrench },
  ];
  
  return (
    <aside
      className={`
        fixed top-0 left-0 h-full w-96 z-20
        glassmorphism shadow-2xl sidebar-transition
        flex flex-col
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}
    >
      {/* Header */}
      <div className="p-6 border-b border-white border-opacity-10">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-8 h-8 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">CW</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Code Weaver</h1>
            <p className="text-xs text-gray-400">3D Code Visualization</p>
          </div>
        </div>
        
        {/* Project Path Input */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-300">
            프로젝트 경로
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={projectPath}
              onChange={(e) => setProjectPath(e.target.value)}
              placeholder="예: /path/to/your/project"
              className="flex-1 input-primary text-sm"
              disabled={isAnalyzing}
            />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !projectPath.trim()}
            className="w-full btn-primary text-sm py-2 flex items-center justify-center"
          >
            {isAnalyzing ? (
              <>
                <div className="inline-block w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                분석 중<span className="loading-dots"></span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4 mr-2" />
                분석 시작
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Tab Navigation */}
      <div className="flex border-b border-white border-opacity-10">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex-1 flex items-center justify-center space-x-2 py-3 px-4
                text-sm font-medium transition-all duration-200
                ${
                  activeTab === tab.id
                    ? 'text-cyber-blue border-b-2 border-cyber-blue bg-white bg-opacity-5'
                    : 'text-gray-400 hover:text-white hover:bg-white hover:bg-opacity-5'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          );
        })}
      </div>
      
      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'analysis' && (
          <AnalysisPanel
            analysisResult={analysisResult}
            selectedNode={selectedNode}
            isAnalyzing={isAnalyzing}
          />
        )}
        
        {activeTab === 'hierarchy' && (
          <HierarchyPanel
            analysisResult={analysisResult}
            selectedNode={selectedNode}
            isAnalyzing={isAnalyzing}
          />
        )}
        
        {activeTab === 'stats' && (
          <StatisticsPanel
            statistics={statistics}
            analysisResult={analysisResult}
          />
        )}
        
        {activeTab === 'code' && (
          <CodePanel
            selectedNode={selectedNode}
          />
        )}
        
        {activeTab === 'refactoring' && (
          <RefactoringPanel
            selectedNode={selectedNode}
          />
        )}
      </div>
    </aside>
  );
};

export default Sidebar;