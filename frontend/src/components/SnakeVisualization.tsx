import React, { useEffect, useRef } from 'react';
import gameConfig from '../config/gameConfig';

interface SnakeVisualizationProps {
  state: number[];
  mode: "training" | "inference" | "idle";
}

/**
 * Renders a Snake game state on a canvas.
 * Assumes state is structured as a sequence of snake segments (x,y) followed by food coordinates.
 */
const SnakeVisualization: React.FC<SnakeVisualizationProps> = ({ state, mode }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { cellSize, gridSize } = gameConfig.snake;

  const drawSnake = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw snake segments (all except the last two values)
    ctx.fillStyle = '#00ff00';
    ctx.shadowColor = 'rgba(0, 255, 0, 0.6)';
    ctx.shadowBlur = 10;
    for (let i = 0; i < state.length - 2; i += 2) {
      const x = state[i];
      const y = state[i + 1];
      if (x === -1 || y === -1) continue;
      ctx.fillRect(x * cellSize, y * cellSize, cellSize - 2, cellSize - 2);
    }

    // Draw food (last two values)
    ctx.fillStyle = '#ff3366';
    ctx.shadowColor = 'rgba(255, 51, 102, 0.6)';
    ctx.shadowBlur = 15;
    const foodX = state[state.length - 2];
    const foodY = state[state.length - 1];
    ctx.fillRect(foodX * cellSize, foodY * cellSize, cellSize - 2, cellSize - 2);

    // Display current mode
    ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
    ctx.font = "16px Arial";
    ctx.fillText(`Mode: ${mode}`, 10, 20);
  };

  useEffect(() => {
    let animationFrameId: number;
    const render = () => {
      drawSnake();
      animationFrameId = requestAnimationFrame(render);
    };
    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [state, mode]);

  const width = gridSize * cellSize;
  const height = gridSize * cellSize;
  return <canvas ref={canvasRef} width={width} height={height} className="canvas" />;
};

export default SnakeVisualization;
