import { useState, useRef, useEffect } from 'react';
import EnvironmentVisualization from '@/components/EnvironmentVisualization';
import EnvironmentController from '@/components/EnvironmentController';
import useWebSocket from '@/hooks/useWebSocket';

export default function Home() {
  const isInferencingRef = useRef(false);

  const [isTraining, setIsTraining] = useState(false);
  const [isInferencing, setIsInferencing] = useState(false);

  // ✅ Mise à jour immédiate de la ref → Évite le délai de synchronisation
  useEffect(() => {
    isInferencingRef.current = isInferencing;
  }, [isInferencing]);

  // ✅ Lancement immédiat de la connexion WebSocket dès que isInferencing change
  const { state, sendMessage, closeWebSocket } = useWebSocket(
    isInferencing ? 'ws://localhost:8000/ws' : null
  );

  // ✅ Gestion du training (pas de WebSocket)
  const handleTrainingAction = async (action: string) => {
    if (isInferencing) {
      console.warn('🚫 Cannot train while inference is running');
      return;
    }
  
    try {
      const response = await fetch(`http://localhost:8000/training/${action}`, {
        method: 'POST',
      });
  
      const data = await response.json();
      console.log(`✅ Status: ${data.status}`);
  
      if (action === 'start') setIsTraining(true);
      if (action === 'stop') setIsTraining(false);
      if (action === 'pause') console.log('⏸️ Training paused');
    } catch (error) {
      console.error('❌ Error:', error);
    }
  };
  

  // ✅ Gestion de l'inférence (avec WebSocket)
  const handleInferenceAction = async (action: string) => {
    if (isTraining) {
      console.warn('🚫 Cannot infer while training is running');
      return;
    }
  
    if (action === 'start') {
      console.log('🚀 Starting inference...');
      setIsInferencing(true);
    }
  
    if (action === 'stop') {
      console.log('🛑 Stopping inference...');
      setIsInferencing(false);
      closeWebSocket(); // ✅ Fermeture propre du WebSocket
    }
  
    if (action === 'pause') {
      console.log('⏸️ Pausing inference...');
  
      // ✅ Appel de l'API REST pour mettre en pause
      try {
        const response = await fetch('http://localhost:8000/inference/pause', {
          method: 'POST'
        });
        const data = await response.json();
        console.log(`✅ Status: ${data.status}`);
      } catch (error) {
        console.error('❌ Error pausing inference:', error);
      }
    }
  
    console.log(`🔎 Inference action: ${action}`);
    sendMessage({ action: `${action}_inference` });
  };
  

  return (
    <div className="wrapper">
      {/* ✅ Partie Canvas + Inference */}
      <div className="left-section">
        <EnvironmentVisualization state={state} />
  
        {/* ✅ Boutons d'inférence */}
        <div className="button-group">
          <button
            className="button"
            onClick={() => handleInferenceAction('start')}
            disabled={isTraining || isInferencing}
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
  
      {/* ✅ Training panel à droite */}
      <div className="right-section">
        <h3 className="title">Training</h3>
        <div className="button-group">
          <button
            className="button"
            onClick={() => handleTrainingAction('start')}
            disabled={isTraining || isInferencing}
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
            onClick={() => console.log('Saving model...')}
            disabled={!isTraining}
          >
            Save Model
          </button>
        </div>
      </div>
    </div>
  );
  
}  