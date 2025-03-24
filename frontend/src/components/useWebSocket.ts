import { useEffect, useState, useRef } from 'react';
import dispatcher from '../utils/WebSocketDispatcher';

const useWebSocket = (url: string | null, useLocalStateUpdate: boolean = false) => {
  const [state, setState] = useState<any>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const latestMessageRef = useRef<any>(null);
  const animationFrameId = useRef<number | null>(null);

  // Schedule a state update using requestAnimationFrame to throttle updates.
  const scheduleUpdate = () => {
    if (animationFrameId.current === null) {
      animationFrameId.current = requestAnimationFrame(() => {
        if (latestMessageRef.current) {
          if (useLocalStateUpdate) {
            // Update local state with the latest message.
            setState(latestMessageRef.current.state || latestMessageRef.current);
          } else {
            dispatcher.dispatch(latestMessageRef.current);
          }
        }
        animationFrameId.current = null;
      });
    }
  };

  useEffect(() => {
    if (url) {
      socketRef.current = new WebSocket(url);

      socketRef.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
      };

      socketRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('📥 Message received:', message);
        // If the message contains a sequence number, keep only the latest.
        if (message.seq) {
          if (!latestMessageRef.current || message.seq > latestMessageRef.current.seq) {
            latestMessageRef.current = message;
          }
        } else {
          latestMessageRef.current = message;
        }
        scheduleUpdate();
      };

      socketRef.current.onclose = () => {
        console.log('❌ WebSocket disconnected');
        setIsConnected(false);
      };

      socketRef.current.onerror = (error) => {
        console.error('🚨 WebSocket Error:', error);
      };

      return () => {
        socketRef.current?.close();
      };
    }
  }, [url, useLocalStateUpdate]);

  // Register dispatcher state handler if not using local state update.
  useEffect(() => {
    if (!useLocalStateUpdate) {
      dispatcher.registerStateHandler(setState);
    }
  }, [useLocalStateUpdate]);

  const sendMessage = (message: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  };

  const closeWebSocket = () => {
    socketRef.current?.close();
  };

  const pause = () => {
    setIsPaused(true);
    sendMessage({ type: 'config', value: { paused: true } });
  };

  const resume = () => {
    setIsPaused(false);
    sendMessage({ type: 'config', value: { paused: false } });
  };

  return {
    state,
    isConnected,
    isPaused,
    sendMessage,
    closeWebSocket,
    pause,
    resume,
  };
};

export default useWebSocket;
