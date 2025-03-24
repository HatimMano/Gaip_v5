import React from 'react';
import SnakeVisualization from './SnakeVisualization';
import PongVisualization from './PongVisualization';
import TangoVisualization from './TangoVisualization';

interface GameVisualizationProps {
  // Pour Tango, l'état est une matrice 2D, pour les autres, l'état peut être un array de nombres.
  state: any;
  game: "snake" | "pong" | "tango" | string;
  mode: "training" | "inference" | "idle";
}

const GameVisualization: React.FC<GameVisualizationProps> = ({ state, game, mode }) => {
  if (game === "snake") {
    return <SnakeVisualization state={state} mode={mode} />;
  } else if (game === "pong") {
    return <PongVisualization state={state} mode={mode} />;
  } else if (game === "tango") {
    return <TangoVisualization state={state} mode={mode} />;
  } else {
    return <div>No visualization available for this game.</div>;
  }
};

export default GameVisualization;
