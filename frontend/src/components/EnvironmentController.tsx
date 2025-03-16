interface Props {
    // ✅ Training Handlers
    onStartTraining: () => void;
    onStopTraining: () => void;
    onPauseTraining: () => void;
    onSaveModel: () => void;
  
    // ✅ Inference Handlers
    onStartInference: () => void;
    onStopInference: () => void;
    onPauseInference: () => void;
  
    // ✅ States
    isTraining: boolean;
    isInferencing: boolean;
  
    // ✅ Feedback Values
    currentEpisode: number;
    maxEpisodes: number;
    currentReward: number;
    averageReward: number;
  }
  
  const EnvironmentController: React.FC<Props> = ({
    onStartTraining,
    onStopTraining,
    onPauseTraining,
    onSaveModel,
    onStartInference,
    onStopInference,
    onPauseInference,
    isTraining,
    isInferencing,
    currentEpisode,
    maxEpisodes,
    currentReward,
    averageReward,
  }) => {
    return (
      <div className="controller-wrapper">
        {/* ✅ Inference Block */}
        <div className="panel">
          <h3>Inference</h3>
          <div className="button-group">
            <button
              className="button"
              onClick={onStartInference}
              disabled={isTraining || isInferencing}
            >
              Start
            </button>
            <button
              className="button"
              onClick={onPauseInference}
              disabled={!isInferencing}
            >
              Pause
            </button>
            <button
              className="button"
              onClick={onStopInference}
              disabled={!isInferencing}
            >
              Stop
            </button>
          </div>
        </div>
  
        {/* ✅ Training Block */}
        <div className="panel">
          <h3>Training</h3>
  
          {/* ✅ Barre de progression */}
          <progress
            value={currentEpisode}
            max={maxEpisodes}
            className="progress-bar"
          />
  
          {/* ✅ Statut */}
          <p>
            Episodes: <strong>{currentEpisode}</strong> / {maxEpisodes}
          </p>
  
          {/* ✅ Current Reward */}
          <p>
            Current Reward: <strong>{currentReward.toFixed(2)}</strong>
          </p>
  
  
          <div className="button-group">
            <button
              className="button"
              onClick={onStartTraining}
              disabled={isTraining || isInferencing}
            >
              Start
            </button>
            <button
              className="button"
              onClick={onPauseTraining}
              disabled={!isTraining}
            >
              Pause
            </button>
            <button
              className="button"
              onClick={onStopTraining}
              disabled={!isTraining}
            >
              Stop
            </button>
            <button
              className="button"
              onClick={onSaveModel}
              disabled={!isTraining}
            >
              Save Model
            </button>
          </div>
        </div>
      </div>
    );
  };
  
  export default EnvironmentController;
  