import { useState, useEffect, useRef } from 'react';

export interface InventoryEvent {
  product_name: string;
  store_code: string;
  quantity: number;
  reorder_point: number;
  updated_at: string | null;
}

export function useInventoryFeed(url: string) {
  const [events, setEvents]       = useState<InventoryEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const wsRef          = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive          = useRef(true);

  useEffect(() => {
    alive.current = true;

    function connect() {
      if (!alive.current) return;
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!alive.current) { ws.close(); return; }
          setConnected(true);
          setError(null);
        };

        ws.onmessage = (e) => {
          try {
            const msg = JSON.parse(e.data);
            if (msg.type === 'inventory_snapshot' && Array.isArray(msg.events)) {
              setEvents(msg.events);
            }
          } catch { /* ignore malformed */ }
        };

        ws.onclose = () => {
          setConnected(false);
          if (alive.current) {
            reconnectTimer.current = setTimeout(connect, 3000);
          }
        };

        ws.onerror = () => {
          setError('WebSocket connection failed');
          ws.close();
        };
      } catch {
        setError('Could not connect to live feed');
        reconnectTimer.current = setTimeout(connect, 5000);
      }
    }

    connect();
    return () => {
      alive.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [url]);

  return { events, connected, error };
}
