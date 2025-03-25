import React, { useEffect, useRef } from 'react';
import gameConfig from '../config/gameConfig';

interface PongVisualizationProps {
  state: number[];
  mode: "training" | "inference" | "idle";
}

/**
 * Renders a Pong game state on a canvas.
 * Assumes state is an array:
 * [playerPaddleY, opponentPaddleY, ballX, ballY, ballVx, ballVy] (normalized)
 */
const PongVisualization: React.FC<PongVisualizationProps> = ({ state, mode }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { paddleHeight, paddleWidth, ballRadius } = gameConfig.pong;

  const drawPong = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const playerPaddleY = state[0] * canvasHeight;
    const opponentPaddleY = state[1] * canvasHeight;
    const ballX = state[2] * canvasWidth;
    const ballY = state[3] * canvasHeight;

    ctx.fillStyle = '#00ff00';
    ctx.fillRect(10, playerPaddleY, paddleWidth, paddleHeight);

    ctx.fillStyle = '#ff3366';
    ctx.fillRect(canvasWidth - 10 - paddleWidth, opponentPaddleY, paddleWidth, paddleHeight);

    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(ballX, ballY, ballRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
    ctx.font = "16px Arial";
    ctx.fillText(`Mode: ${mode}`, 10, 20);
  };

  useEffect(() => {
    let animationFrameId: number;
    const render = () => {
      drawPong();
      animationFrameId = requestAnimationFrame(render);
    };
    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [state, mode]);

  return <canvas ref={canvasRef} width={400} height={400} className="canvas" />;
};

export default PongVisualization;
