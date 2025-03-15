import React, { useEffect, useRef } from 'react';

interface Props {
  state: number[];
}

const cellSize = 35; // ✅ Taille ajustée pour un meilleur rendu
const gridSize = 10;

const EnvironmentVisualization: React.FC<Props> = ({ state }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const drawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // ✅ Nettoyage de la zone de dessin
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // ✅ Animation douce → Transition fluide
    ctx.fillStyle = '#00ff00';
    ctx.shadowColor = 'rgba(0, 255, 0, 0.6)';
    ctx.shadowBlur = 10;

    // ✅ Dessin du serpent
    for (let i = 0; i < state.length - 2; i += 2) {
      const x = state[i] * cellSize;
      const y = state[i + 1] * cellSize;
      ctx.fillRect(x, y, cellSize - 2, cellSize - 2);
    }

    // ✅ Dessin de la nourriture (avec une couleur plus douce)
    ctx.fillStyle = '#ff3366';
    ctx.shadowColor = 'rgba(255, 51, 102, 0.6)';
    ctx.shadowBlur = 15;
    const foodX = state[state.length - 2] * cellSize;
    const foodY = state[state.length - 1] * cellSize;
    ctx.fillRect(foodX, foodY, cellSize - 2, cellSize - 2);
  };

  // ✅ Redessiner quand l'état change
  useEffect(() => {
    drawCanvas();
  }, [state]);

  return (
    <canvas
      ref={canvasRef}
      className="canvas" // ✅ Classe CSS déjà définie dans global.css
      width={gridSize * cellSize}
      height={gridSize * cellSize}
    />
  );
};

export default EnvironmentVisualization;
