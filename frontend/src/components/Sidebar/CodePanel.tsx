import React from 'react';
import { FileText, Code } from 'lucide-react';
import { NodeData } from '@/types';

interface CodePanelProps {
  selectedNode: NodeData | null;
}

const CodePanel: React.FC<CodePanelProps> = ({ selectedNode }) => {
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

  // Mock code content - in a real implementation, this would fetch from the backend
  const getCodePreview = () => {
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
        <pre className="whitespace-pre-wrap">
          {getCodePreview()}
        </pre>
      </div>
      
      <div className="mt-3 text-xs text-gray-500 text-center">
        💡 실제 구현에서는 백엔드에서 실제 코드를 가져와 표시합니다
      </div>
    </div>
  );
};

export default CodePanel;