import { useEffect, useRef, useState } from 'react';

const useWebSocket = (url: string | null) => {
  const [state, setState] = useState<number[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!url || socketRef.current) return; // Avoid reconnecting if already connected

    socketRef.current = new WebSocket(url);

    socketRef.current.onopen = () => {
      console.log('✅ Connected to WebSocket');
      setIsConnected(true);
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setState(data.state);
    };

    socketRef.current.onclose = () => {
      console.log('🔴 Disconnected from WebSocket');
      setIsConnected(false);
    };

    socketRef.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    return () => {
      // No automatic cleanup — manual closure only
    };
  }, [url]);

  const sendMessage = (message: object) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  };

  const closeWebSocket = () => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
  };

  return { state, isConnected, sendMessage, closeWebSocket };
};

export default useWebSocket;