import React, { useState, useEffect } from 'react';
import { FileText, Code, Loader2 } from 'lucide-react';
import { NodeData } from '@/types';
import { apiClient } from '@/services/api';

interface CodePanelProps {
  selectedNode: NodeData | null;
}

const CodePanel: React.FC<CodePanelProps> = ({ selectedNode }) => {
  const [sourceCode, setSourceCode] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Fetch source code when selectedNode changes
  useEffect(() => {
    if (!selectedNode) {
      setSourceCode('');
      setError('');
      return;
    }

    const fetchSourceCode = async () => {
      if (selectedNode.type !== 'function') {
        // For non-function nodes, show basic info
        setSourceCode(getMockCodePreview());
        return;
      }

      setLoading(true);
      setError('');
      
      try {
        const response = await apiClient.getFunctionById(selectedNode.id);
        setSourceCode(response.sourceCode || 'Source code not available');
      } catch (err: any) {
        console.error('Failed to fetch function source:', err);
        setError('Failed to load source code');
        setSourceCode(getMockCodePreview());
      } finally {
        setLoading(false);
      }
    };

    fetchSourceCode();
  }, [selectedNode]);

  const getMockCodePreview = () => {
    if (!selectedNode) return '';
    
    const { type, name } = selectedNode;
    
    switch (type) {
      case 'function':
        return `def ${name}():\n    """Function implementation"""\n    pass`;
      case 'class':
        return `class ${name}:\n    """Class implementation"""\n    \n    def __init__(self):\n        pass`;
      case 'module':
        return `# ${name}\n"""Module docstring"""\n\nimport statements...`;
      default:
        return `# ${name}\n# Code content...`;
    }
  };

  if (!selectedNode) {
    return (
      <div className="p-4 text-center py-8">
        <Code className="w-12 h-12 mx-auto text-gray-500 mb-4" />
        <p className="text-gray-400">코드 미리보기</p>
        <p className="text-sm text-gray-500 mt-2">
          3D 뷰에서 노드를 선택하면 코드 정보가 표시됩니다
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 h-full flex flex-col">
      <div className="flex items-center space-x-2 mb-4">
        <FileText className="w-5 h-5 text-cyber-blue" />
        <span className="font-semibold text-white">코드 미리보기</span>
      </div>
      
      <div className="mb-3 p-3 bg-space-700 bg-opacity-50 rounded-lg">
        <div className="text-sm space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-400">파일:</span>
            <span className="text-white font-mono text-xs">{selectedNode.file}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">이름:</span>
            <span className="text-white font-mono">{selectedNode.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">타입:</span>
            <span className="text-white capitalize">{selectedNode.type}</span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 bg-space-800 rounded-lg p-4 font-mono text-sm text-gray-300 overflow-auto custom-scrollbar">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-6 h-6 animate-spin text-cyber-blue" />
            <span className="ml-2 text-gray-400">Loading source code...</span>
          </div>
        ) : error ? (
          <div className="text-red-400 p-4 text-center">
            <div className="text-lg mb-2">⚠️</div>
            <div>{error}</div>
            <div className="text-xs text-gray-500 mt-2">Showing fallback preview</div>
          </div>
        ) : null}
        
        <pre className="whitespace-pre-wrap">
          {sourceCode}
        </pre>
      </div>
      
      {selectedNode.type === 'function' && !loading && !error && (
        <div className="mt-3 text-xs text-green-400 text-center flex items-center justify-center">
          <span className="mr-1">✓</span>
          실제 Neo4j 데이터베이스에서 코드를 가져왔습니다
        </div>
      )}
      
      {selectedNode.type !== 'function' && (
        <div className="mt-3 text-xs text-gray-500 text-center">
          💡 함수 노드가 아닌 경우 기본 미리보기를 표시합니다
        </div>
      )}
    </div>
  );
};

export default CodePanel;