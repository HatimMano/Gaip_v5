import React, { useEffect, useRef } from 'react';
import gameConfig from '../config/gameConfig';

interface Constraint {
  equal_pairs: [[number, number], [number, number]][];
  diff_pairs: [[number, number], [number, number]][];
}

interface TangoVisualizationProps {
  state: (string | null)[][] | undefined;
  mode: "training" | "inference" | "idle";
  constraints?: Constraint;
}

/**
 * Renders a Tango puzzle state on a canvas.
 * The grid is drawn with light gray lines, filled cells display their symbol,
 * and constraints are visualized with a marker ("=" or "x") placed between the two cells concerned.
 */
const TangoVisualization: React.FC<TangoVisualizationProps> = ({ state, mode, constraints }) => {
const { gridSize, canvasSize, cellSize } = gameConfig.tango;


  const defaultConstraints: Constraint = {
    equal_pairs: [
      [[0, 0], [1, 0]],
      [[2, 2], [3, 2]],
      [[4, 4], [5, 4]]
    ],
    diff_pairs: [
      [[0, 2], [1, 2]],
      [[3, 3], [4, 3]],
      [[2, 5], [3, 5]]
    ]
  };

  const effectiveConstraints = constraints ? constraints : defaultConstraints;

  const canvasRef = useRef<HTMLCanvasElement>(null);

  const drawTango = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#CCCCCC';
    ctx.lineWidth = 1;
    for (let i = 0; i <= gridSize; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cellSize, 0);
      ctx.lineTo(i * cellSize, canvasSize);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, i * cellSize);
      ctx.lineTo(canvasSize, i * cellSize);
      ctx.stroke();
    }

    if (state && Array.isArray(state) && state.length === gridSize) {
      ctx.font = `${cellSize * 0.6}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      for (let row = 0; row < gridSize; row++) {
        if (!Array.isArray(state[row]) || state[row].length !== gridSize) {
          console.error(`Row ${row} of state is not valid.`);
          continue;
        }
        for (let col = 0; col < gridSize; col++) {
          const symbol = state[row][col];
          if (symbol) {
            ctx.fillStyle = symbol === 'O' ? '#00ff00' : '#ff3366';
            ctx.fillText(symbol, col * cellSize + cellSize / 2, row * cellSize + cellSize / 2);
          }
        }
      }
    } else {
      ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
      ctx.font = "16px Arial";
      ctx.fillText("No state provided", canvasSize / 2, canvasSize / 2);
    }

    if (effectiveConstraints) {
      ctx.font = `${cellSize * 0.4}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      const getMidPoint = (cellA: [number, number], cellB: [number, number]) => {
        const [rowA, colA] = cellA;
        const [rowB, colB] = cellB;
        const midX = (((colA + 0.5) + (colB + 0.5)) / 2) * cellSize;
        const midY = (((rowA + 0.5) + (rowB + 0.5)) / 2) * cellSize;
        return { midX, midY };
      };

      effectiveConstraints.equal_pairs.forEach(pair => {
        const { midX, midY } = getMidPoint(pair[0], pair[1]);
        ctx.fillStyle = '#0000FF'; // bleu
        ctx.fillText("=", midX, midY);
      });

      effectiveConstraints.diff_pairs.forEach(pair => {
        const { midX, midY } = getMidPoint(pair[0], pair[1]);
        ctx.fillStyle = '#FFA500'; // orange
        ctx.fillText("x", midX, midY);
      });
    }

    ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
    ctx.font = "16px Arial";
    ctx.fillText(`Mode: ${mode}`, 10, 20);
  };

  useEffect(() => {
    drawTango();
  }, [state, mode, effectiveConstraints]);

  return <canvas ref={canvasRef} width={canvasSize} height={canvasSize} className="canvas" />;
};

export default TangoVisualization;
