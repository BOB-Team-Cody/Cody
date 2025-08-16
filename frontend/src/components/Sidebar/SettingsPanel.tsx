import React from 'react';
import { useAppStore } from '@/hooks/useAppStore';

const SettingsPanel: React.FC = () => {
  const { autoRotate, setAutoRotate } = useAppStore();

  return (
    <div className="p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">시각화 설정</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-300">자동 회전</span>
            <button
              onClick={() => setAutoRotate(!autoRotate)}
              className={`
                relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                ${autoRotate ? 'bg-cyber-blue' : 'bg-gray-600'}
              `}
            >
              <span
                className={`
                  inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                  ${autoRotate ? 'translate-x-6' : 'translate-x-1'}
                `}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;