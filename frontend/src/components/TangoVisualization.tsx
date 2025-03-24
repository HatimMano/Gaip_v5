import React, { useEffect, useRef } from 'react';

interface TangoVisualizationProps {
  // L'état doit être une matrice 2D, chaque cellule pouvant être une chaîne ou null.
  state: (string | null)[][] | undefined;
  mode: "training" | "inference" | "idle";
}

/**
 * Renders a Tango puzzle state on a canvas.
 * The grid is drawn with light gray lines, and filled cells display their symbol.
 */
const TangoVisualization: React.FC<TangoVisualizationProps> = ({ state, mode }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const canvasSize = 400;
  
  // Détermine la taille de la grille à partir de state, sinon par défaut à 6
  const gridSize = state && Array.isArray(state) && state.length > 0 ? state.length : 6;
  const cellSize = canvasSize / gridSize;

  const drawTango = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Efface le canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Dessiner les lignes de la grille
    ctx.strokeStyle = '#CCCCCC';
    ctx.lineWidth = 1;
    for (let i = 0; i <= gridSize; i++) {
      // Lignes verticales
      ctx.beginPath();
      ctx.moveTo(i * cellSize, 0);
      ctx.lineTo(i * cellSize, canvas.height);
      ctx.stroke();

      // Lignes horizontales
      ctx.beginPath();
      ctx.moveTo(0, i * cellSize);
      ctx.lineTo(canvas.width, i * cellSize);
      ctx.stroke();
    }

    // Dessiner les symboles dans les cellules si state est défini et conforme
    if (state && Array.isArray(state) && state.length === gridSize) {
      ctx.font = `${cellSize * 0.6}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      for (let row = 0; row < gridSize; row++) {
        // Vérifier que state[row] est un tableau et a la bonne longueur
        if (!Array.isArray(state[row]) || state[row].length !== gridSize) {
          console.error(`Row ${row} of state is not valid.`);
          continue;
        }
        for (let col = 0; col < gridSize; col++) {
          const symbol = state[row][col];
          if (symbol) {
            // Choix de la couleur : 'O' en vert, 'C' en rouge
            ctx.fillStyle = symbol === 'O' ? '#00ff00' : '#ff3366';
            ctx.fillText(symbol, col * cellSize + cellSize / 2, row * cellSize + cellSize / 2);
          }
        }
      }
    } else {
      // Optionnel : afficher un message si state est undefined
      ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
      ctx.font = "16px Arial";
      ctx.fillText("No state provided", canvasSize / 2, canvasSize / 2);
    }

    // Affiche le mode actuel en superposition
    ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
    ctx.font = "16px Arial";
    ctx.fillText(`Mode: ${mode}`, 10, 20);
  };

  // Redessiner à chaque changement de state ou de mode
  useEffect(() => {
    drawTango();
  }, [state, mode, gridSize, cellSize]);

  return <canvas ref={canvasRef} width={canvasSize} height={canvasSize} className="canvas" />;
};

export default TangoVisualization;
