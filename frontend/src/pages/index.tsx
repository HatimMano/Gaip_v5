import { useState, useEffect } from 'react';
import GameVisualization from '@/components/GameVisualization';
import InferencePanel from '@/components/InferencePanel';
import TrainingPanel from '@/components/TrainingPanel';
import useWebSocket from '@/components/useWebSocket';

export default function Home() {
  const [selectedGame, setSelectedGame] = useState("tango");
  const [isTraining, setIsTraining] = useState(false);
  const [isInferencing, setIsInferencing] = useState(false);
  const currentMode = isTraining ? "training" : isInferencing ? "inference" : "idle";

  const [inferenceState, setInferenceState] = useState<any>([]);
  const inferenceWsUrl = isInferencing ? `ws://localhost:8000/ws?game=${selectedGame}` : null;
  const { state: wsInferenceState, sendMessage, closeWebSocket } = useWebSocket(inferenceWsUrl);

  useEffect(() => {
    if (wsInferenceState && wsInferenceState.length > 0) {
      setInferenceState(wsInferenceState);
    }
  }, [wsInferenceState]);

  const [trainingState, setTrainingState] = useState<any>([]);
  const trainingWsUrl = isTraining ? `ws://localhost:8000/ws/training?game=${selectedGame}` : null;
  const trainingWS = useWebSocket(trainingWsUrl, true);

  useEffect(() => {
    if (trainingWS.state) {
      setTrainingState(trainingWS.state);
    }
  }, [trainingWS.state]);

  useEffect(() => {
    if (isInferencing) {
      console.log(`Game changed to ${selectedGame}. Closing inference WebSocket...`);
      closeWebSocket();
      setIsInferencing(false);
    }
  }, [selectedGame]);

  const [currentEpisode, setCurrentEpisode] = useState(0);
  const [currentReward, setCurrentReward] = useState(0);
  const [averageReward, setAverageReward] = useState(0);
  const maxEpisodes = 100;
  
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    const fetchTrainingStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/training/status?game=${selectedGame}`);
        const data = await response.json();
        setCurrentEpisode(data.current_episode);
        setCurrentReward(data.current_reward);
        setAverageReward(data.average_reward);
      } catch (error) {
        console.error('Error fetching training status:', error);
      }
    };
    if (isTraining) {
      fetchTrainingStatus();
      interval = setInterval(fetchTrainingStatus, 500);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isTraining, selectedGame]);

  const handleTrainingAction = async (action: string) => {
    if (isInferencing) {
      console.warn('Cannot train while inference is running');
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/training/${action}?game=${selectedGame}`, {
        method: 'POST',
      });
      const data = await response.json();
      console.log(`Status: ${data.status}`);
      if (action === 'start') {
        setIsTraining(true);
      } else if (action === 'stop') {
        setIsTraining(false);
      } else if (action === 'pause') {
        if (data.status === "Training resumed") {
          setIsTraining(true);
        }
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleInferenceAction = async (action: string) => {
    if (isTraining) {
      console.warn('Cannot infer while training is running');
      return;
    }
    if (action === 'start') {
      setIsInferencing(true);
    }
    if (action === 'stop') {
      setIsInferencing(false);
      closeWebSocket();
    }
    if (action === 'pause') {
      try {
        const response = await fetch(`http://localhost:8000/inference/pause?game=${selectedGame}`, {
          method: 'POST',
        });
        const data = await response.json();
        console.log(`Status: ${data.status}`);
      } catch (error) {
        console.error('Error pausing inference:', error);
      }
    }
    sendMessage({ action: `${action}_inference`, game: selectedGame });
  };

  const saveModel = async () => {
    try {
      const response = await fetch(`http://localhost:8000/training/save?game=${selectedGame}`, {
        method: 'POST',
      });
      const data = await response.json();
      console.log(`Status: ${data.status}`);
    } catch (error) {
      console.error('Error saving model:', error);
    }
  };

  const displayedState = isTraining ? trainingState : inferenceState;

  return (
    <div className="container">
      <InferencePanel 
        selectedGame={selectedGame}
        isInferencing={isInferencing}
        handleInferenceAction={handleInferenceAction}
      />

      <div className="center-section">
        <GameVisualization state={displayedState} game={selectedGame} mode={currentMode} />
        <div className="game-selector">
          <label htmlFor="game-select">Select Game:</label>
          <select
            id="game-select"
            value={selectedGame}
            onChange={(e) => setSelectedGame(e.target.value)}
          >
            <option value="snake">Snake</option>
            <option value="pong">Pong</option>
            <option value="tango">Tango</option>
          </select>
        </div>
      </div>

      <TrainingPanel 
        selectedGame={selectedGame}
        isTraining={isTraining}
        currentEpisode={currentEpisode}
        currentReward={currentReward}
        averageReward={averageReward}
        maxEpisodes={maxEpisodes}
        handleTrainingAction={handleTrainingAction}
        saveModel={saveModel}
      />
    </div>
  );
}
