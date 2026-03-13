import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook to connect to the Nexus WebSocket stream and listen for agent events.
 * Returns the current live status of agents and the streaming activity log.
 */
export const useNexusStream = (url = 'ws://localhost:8000/ws/stream') => {
  const [isConnected, setIsConnected] = useState(false);
  const [agents, setAgents] = useState({
    chronos: { status: 'idle', message: '' },
    hermes: { status: 'idle', message: '' },
    apollo: { status: 'idle', message: '' },
    athena: { status: 'idle', message: '' },
    fortuna: { status: 'idle', message: '' },
  });
  const [logs, setLogs] = useState([]);
  const ws = useRef(null);

  const connect = useCallback(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('[WebSocket] Connected securely to Nexus Core');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // 1. Live Agent Working Status
        if (data.type === 'agent_status') {
          setAgents((prev) => ({
            ...prev,
            [data.agent]: { status: data.status, message: data.message },
          }));
        } 
        
        // 2. Global AI Thinking/Activity Log
        else if (data.type === 'activity_log') {
          // Prepend new logs so the newest is at the top of the feed
          setLogs((prev) => [data.activity, ...prev].slice(0, 100)); // Keep last 100 logs
        }
        
        // 3. Human Approval Required Alert
        else if (data.type === 'approval_request') {
          // In a real app, you might trigger a toast notification or global context alert here
          console.warn(`[Approval Required] ${data.agent} is asking for permission!`);
        }

      } catch (err) {
        console.error('[WebSocket] Failed to parse stream message:', err);
      }
    };

    ws.current.onclose = () => {
      console.log('[WebSocket] Disconnected from Nexus Core');
      setIsConnected(false);
      // Auto-reconnect after 3 seconds
      setTimeout(connect, 3000);
    };

    ws.current.onerror = (err) => {
      console.error('[WebSocket] Connection Error:', err);
      ws.current.close();
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        // Prevent auto-reconnect on unmount
        ws.current.onclose = null; 
        ws.current.close();
      }
    };
  }, [connect]);

  return { isConnected, agents, logs };
};
