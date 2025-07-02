// Purpose: Manages the WebSocket connection and message handling for real-time updates.
// Data_Contract (Interface):
//   Args: {
//     url: string;
//     onMessage: (event: MessageEvent) => void;
//     onOpen?: () => void;
//     onClose?: () => void;
//     onError?: (error: Event) => void;
//   }
//   Returns: {
//     sendMessage: (data: string | object) => void;
//     isConnected: boolean;
//   }
// State_Management: Manages WebSocket connection status (isConnected), and potentially the socket instance.
// Dependencies & Dependents: Uses 'socket.io-client' or native WebSocket. Used by various components needing real-time data.
// V2_Compliance_Check: Confirmed.

import { useEffect, useState, useCallback, useRef } from 'react';
import io, { Socket } from 'socket.io-client';

interface UseWebSocketOptions {
  url: string;
  onMessage: (type: string, data: any) => void; // Generalized message handler
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Error) => void;
}

interface UseWebSocketReturn {
  sendMessage: (type: string, data: any) => void;
  isConnected: boolean;
  subscribe: (event: string, callback: (data: any) => void) => void;
  unsubscribe: (event: string, callback: (data: any) => void) => void;
}

const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
}: UseWebSocketOptions): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!url) return;

    const socket = io(url, {
      transports: ['websocket'], // Force WebSocket transport
      // autoConnect: false, // Could be true if you want to connect immediately
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      onOpen?.();
      console.log('WebSocket connected:', socket.id);
    });

    socket.on('disconnect', (reason: string) => {
      setIsConnected(false);
      onClose?.();
      console.log('WebSocket disconnected:', reason);
    });

    socket.on('connect_error', (error: Error) => {
      console.error('WebSocket connection error:', error);
      onError?.(error);
    });

    // Generic message listener - specific events should be subscribed to
    // This can be a fallback or for general 'message' type events.
    // It's often better to use specific event subscriptions.
    socket.onAny((event, ...args) => {
        onMessage(event, args.length > 0 ? args[0] : null);
    });

    // socket.connect(); // Connect if autoConnect is false

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [url, onOpen, onClose, onError, onMessage]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit(type, data);
    } else {
      console.warn('WebSocket is not connected. Message not sent:', type, data);
    }
  }, []);

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    socketRef.current?.on(event, callback);
  }, []);

  const unsubscribe = useCallback((event: string, callback: (data: any) => void) => {
    socketRef.current?.off(event, callback);
  }, []);


  return { sendMessage, isConnected, subscribe, unsubscribe };
};

export default useWebSocket;
