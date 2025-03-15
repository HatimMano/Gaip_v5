import React, { useEffect, useRef } from 'react';

interface Props {
  state: number[];
}

const cellSize = 35; // Adjusted size for better rendering
const gridSize = 10;

const EnvironmentVisualization: React.FC<Props> = ({ state }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const drawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Smooth animation for transitions
    ctx.fillStyle = '#00ff00';
    ctx.shadowColor = 'rgba(0, 255, 0, 0.6)';
    ctx.shadowBlur = 10;

    // Draw the snake
    for (let i = 0; i < state.length - 2; i += 2) {
      const x = state[i] * cellSize;
      const y = state[i + 1] * cellSize;
      ctx.fillRect(x, y, cellSize - 2, cellSize - 2);
    }

    // Draw the food (with a softer color)
    ctx.fillStyle = '#ff3366';
    ctx.shadowColor = 'rgba(255, 51, 102, 0.6)';
    ctx.shadowBlur = 15;
    const foodX = state[state.length - 2] * cellSize;
    const foodY = state[state.length - 1] * cellSize;
    ctx.fillRect(foodX, foodY, cellSize - 2, cellSize - 2);
  };

  // Redraw when the state changes
  useEffect(() => {
    drawCanvas();
  }, [state]);

  return (
    <canvas
      ref={canvasRef}
      className="canvas" // CSS class defined in global.css
      width={gridSize * cellSize}
      height={gridSize * cellSize}
    />
  );
};

export default EnvironmentVisualization;