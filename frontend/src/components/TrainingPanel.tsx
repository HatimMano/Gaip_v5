// TrainingPanel.tsx
import React from 'react';

interface TrainingPanelProps {
  selectedGame: string;
  isTraining: boolean;
  currentEpisode: number;
  currentReward: number;
  averageReward: number;
  maxEpisodes: number;
  handleTrainingAction: (action: string) => void;
  saveModel: () => void;
}

const TrainingPanel: React.FC<TrainingPanelProps> = ({
  selectedGame,
  isTraining,
  currentEpisode,
  currentReward,
  averageReward,
  maxEpisodes,
  handleTrainingAction,
  saveModel,
}) => {
  return (
    <div className="right-section">
      <h2>Training</h2>
      <progress
        value={currentEpisode}
        max={maxEpisodes}
        className="progress-bar"
      />
      <p>Episodes: {currentEpisode}/{maxEpisodes}</p>
      <p>Current Reward: {currentReward.toFixed(2)}</p>
      <p>Average Reward: {averageReward.toFixed(2)}</p>
      <div className="button-group">
        <button
          className="button"
          onClick={() => handleTrainingAction('start')}
          disabled={isTraining}
        >
          Start
        </button>
        <button
          className="button"
          onClick={() => handleTrainingAction('pause')}
          disabled={!isTraining}
        >
          Pause
        </button>
        <button
          className="button"
          onClick={() => handleTrainingAction('stop')}
          disabled={!isTraining}
        >
          Stop
        </button>
        <button
          className="button"
          onClick={saveModel}
          disabled={!isTraining}
        >
          Save Model
        </button>
      </div>
    </div>
  );
};

export default TrainingPanel;
