import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BellRing, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const BroadcastListener = () => {
  const [broadcasts, setBroadcasts] = useState([]);
  const { token } = useAuth(); // Only connect if logged in

  useEffect(() => {
    if (!token) return;

    // Use absolute URL to the main FastAPI server
    // Protocol is ws:// or wss:// based on current protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use the exact route we mapped in main.py
    const wsUrl = `${protocol}//${window.location.hostname}:8000/api/v1/hotel/ws/broadcast`;
    
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        console.log("Broadcast received:", event.data);
        const data = JSON.parse(event.data);
        // Add new broadcast to list
        setBroadcasts((prev) => [data, ...prev]);
      } catch (err) {
        console.error("Failed to parse broadcast message", err);
      }
    };

    ws.onclose = () => {
      console.log("Broadcast WebSocket disconnected");
    };

    return () => {
      ws.close();
    };
  }, [token]);

  const removeBroadcast = (id) => {
    setBroadcasts((prev) => prev.filter((b) => b.id !== id));
  };

  return (
    <div style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      maxWidth: '400px',
      pointerEvents: 'none' // Let clicks pass through empty areas
    }}>
      <AnimatePresence>
        {broadcasts.map((b) => (
          <motion.div
            key={b.id}
            initial={{ opacity: 0, x: 50, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            style={{
              pointerEvents: 'auto',
              background: b.priority === 'high' ? 'rgba(239, 68, 68, 0.95)' : 'rgba(59, 130, 246, 0.95)',
              color: 'white',
              padding: '16px',
              borderRadius: '8px',
              boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
              backdropFilter: 'blur(10px)',
              border: `1px solid ${b.priority === 'high' ? '#f87171' : '#60a5fa'}`,
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px'
            }}
          >
            <BellRing size={24} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 'bold', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.9, marginBottom: '4px' }}>
                ANNOUNCEMENT
              </div>
              <div style={{ fontSize: '1rem', lineHeight: 1.4 }}>
                {b.message}
              </div>
              <div style={{ fontSize: '0.7rem', opacity: 0.7, marginTop: '8px' }}>
                {b.created_at ? new Date(b.created_at.endsWith('Z') ? b.created_at : b.created_at + 'Z').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
              </div>
            </div>
            <button 
              onClick={() => removeBroadcast(b.id)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'white',
                opacity: 0.7,
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              <X size={16} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default BroadcastListener;
