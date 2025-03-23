// InferencePanel.tsx
import React from 'react';

interface InferencePanelProps {
  selectedGame: string;
  isInferencing: boolean;
  handleInferenceAction: (action: string) => void;
}

const InferencePanel: React.FC<InferencePanelProps> = ({
  selectedGame,
  isInferencing,
  handleInferenceAction,
}) => {
  return (
    <div className="left-section">
      <h2>Inference</h2>
      <div className="button-group">
        <button
          className="button"
          onClick={() => handleInferenceAction('start')}
          disabled={isInferencing}
        >
          Start
        </button>
        <button
          className="button"
          onClick={() => handleInferenceAction('pause')}
          disabled={!isInferencing}
        >
          Pause
        </button>
        <button
          className="button"
          onClick={() => handleInferenceAction('stop')}
          disabled={!isInferencing}
        >
          Stop
        </button>
      </div>
    </div>
  );
};

export default InferencePanel;
