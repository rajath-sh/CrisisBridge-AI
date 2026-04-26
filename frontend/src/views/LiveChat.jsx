import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Send, HeadphonesIcon, User as UserIcon, Loader2, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CHAT_API_BASE = 'http://localhost:8002';
const WS_BASE = 'ws://localhost:8002/ws/chat';

const LiveChat = () => {
  const { user } = useAuth();
  const [activeSessions, setActiveSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [ws, setWs] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const isGuest = user?.role?.toLowerCase() === 'guest';
  const lastReadCountsRef = useRef({}); // Tracks { session_id: number_of_read_messages }

  // Fetch active sessions for staff/admin
  useEffect(() => {
    if (!isGuest && !currentSessionId) {
      const fetchSessions = async () => {
        try {
          const res = await axios.get(`${CHAT_API_BASE}/chat/active`);
          const sessions = res.data.sessions || [];
          
          // If we were just in a session, mark its messages as read
          if (currentSessionId) {
            const currentSess = sessions.find(s => s.session_id === currentSessionId);
            if (currentSess) {
              lastReadCountsRef.current[currentSessionId] = currentSess.message_count;
            }
          }
          
          setActiveSessions(sessions);
        } catch (err) {
          console.error("Failed to fetch active sessions", err);
        }
      };
      fetchSessions();
      const interval = setInterval(fetchSessions, 5000);
      return () => clearInterval(interval);
    }
  }, [isGuest, currentSessionId]);

  // Scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket connection logic
  const connectWebSocket = (sessionId) => {
    if (ws) ws.close();

    const senderId = user?.username || user?.email?.split('@')[0] || 'Unknown';
    const senderRole = user?.role || 'staff';
    const websocket = new WebSocket(`${WS_BASE}/${sessionId}?sender_id=${senderId}&sender_role=${senderRole}`);

    websocket.onopen = () => {
      console.log('Connected to chat session:', sessionId);
      setCurrentSessionId(sessionId);
      setLoading(false);
      
      // Clear unread count when joining
      const sessionData = activeSessions.find(s => s.session_id === sessionId);
      if (sessionData) {
        lastReadCountsRef.current[sessionId] = sessionData.message_count;
      }
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'history') {
        setMessages(data.messages);
      } else if (['message', 'user_joined', 'user_left'].includes(data.event)) {
        setMessages(prev => [...prev, data]);
      } else if (data.event === 'error') {
        alert(`Notice: ${data.message}`);
        if (data.message.includes('deleted')) {
          leaveSession();
        }
      }
    };

    websocket.onclose = () => {
      console.log('Disconnected from chat');
      setCurrentSessionId(null);
      setWs(null);
    };

    setWs(websocket);
  };

  const startNewSession = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${CHAT_API_BASE}/chat/start`, { user_id: user?.username || user?.email?.split('@')[0] || 'Guest' });
      connectWebSocket(res.data.session_id);
    } catch (err) {
      console.error("Failed to start session", err);
      alert("Failed to start chat session.");
      setLoading(false);
    }
  };

  const leaveSession = () => {
    if (ws) {
      ws.close();
    }
    setCurrentSessionId(null);
    setMessages([]);
  };

  const closeSessionAsAdmin = async (sessionId) => {
    try {
      await axios.patch(`${CHAT_API_BASE}/chat/session/${sessionId}/close`);
      leaveSession();
      alert("Session closed.");
    } catch (err) {
      console.error(err);
      alert("Failed to close session.");
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm("Are you sure you want to permanently delete this session and all its data?")) return;
    try {
      // Use the correct API path /chat/session/{id}
      await axios.delete(`${CHAT_API_BASE}/chat/session/${sessionId}`);
      setActiveSessions(prev => prev.filter(s => s.session_id !== sessionId));
    } catch (err) {
      console.error("Deletion failed:", err.response?.data || err.message);
      alert("Failed to delete session. Check if the chat module is running on port 8002.");
    }
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (!input.trim() || !ws) return;

    ws.send(JSON.stringify({
      sender_id: user?.username || user?.email?.split('@')[0] || 'Unknown',
      sender_role: user?.role || 'user',
      message: input
    }));
    setInput('');
  };

  return (
    <div className="dashboard-container" style={{ maxWidth: '1000px', margin: '0 auto', height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem', flexShrink: 0 }}>
        <div style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '1rem' }}>
          <HeadphonesIcon size={32} color="#3b82f6" />
        </div>
        <div>
          <h1>Live Support</h1>
          <p className="text-muted">Real-time connection to {isGuest ? 'hotel staff' : 'guests in need'}</p>
        </div>
      </div>

      <div className="glass-card" style={{ flex: 1, display: 'flex', overflow: 'hidden', padding: 0, flexDirection: 'column', background: 'rgba(15, 23, 42, 0.6)' }}>
        
        {/* Active Chat Interface (Full Height Container) */}
        {currentSessionId ? (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
            {/* Header: Sticky at top */}
            <div className="p-4 flex justify-between items-center" style={{ borderBottom: '1px solid var(--border)', background: 'rgba(0,0,0,0.4)', flexShrink: 0 }}>
              <div>
                <h3 className="text-sm font-bold flex items-center gap-2">
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }}></span>
                  Session Active
                </h3>
                <p className="text-[10px] text-muted text-mono mt-1 opacity-60">{currentSessionId}</p>
              </div>
              <div className="flex gap-2">
                <button className="btn btn-ghost btn-sm" style={{ padding: '0.4rem 1rem' }} onClick={leaveSession}>
                  Leave
                </button>
                {user?.role === 'admin' && (
                  <button className="btn btn-danger btn-sm" style={{ padding: '0.4rem 1rem' }} onClick={() => closeSessionAsAdmin(currentSessionId)}>
                    End Chat
                  </button>
                )}
              </div>
            </div>

            {/* Chat Messages: Scrollable Middle */}
            <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-4 custom-scrollbar" style={{ background: 'rgba(0,0,0,0.1)' }}>
              {messages.map((msg, i) => {
                if (['user_joined', 'user_left'].includes(msg.event)) {
                  return (
                    <div key={i} className="text-center w-full my-2">
                      <span className="text-[10px] text-muted px-4 py-1 rounded-full uppercase tracking-widest font-bold" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                        {msg.message}
                      </span>
                    </div>
                  );
                }

                const isMe = msg.sender_id === (user?.username || user?.email?.split('@')[0] || 'Unknown');
                return (
                  <div 
                    key={i} 
                    className="flex gap-3 max-w-[85%]" 
                    style={{ 
                      alignSelf: isMe ? 'flex-end' : 'flex-start',
                      flexDirection: isMe ? 'row-reverse' : 'row' 
                    }}
                  >
                    <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-lg" style={{ background: isMe ? 'var(--primary)' : 'rgba(255,255,255,0.1)', border: '2px solid rgba(255,255,255,0.05)' }}>
                      <UserIcon size={14} color="white" />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: isMe ? 'flex-end' : 'flex-start' }}>
                      <div className={`text-[10px] mb-1 uppercase tracking-wider font-bold opacity-60 ${isMe ? 'text-right' : 'text-left'}`}>
                        {msg.sender_id} • {msg.sender_role}
                      </div>
                      <div className="shadow-xl" style={{ 
                        padding: '0.8rem 1.2rem',
                        borderRadius: isMe ? '1.25rem 0.25rem 1.25rem 1.25rem' : '0.25rem 1.25rem 1.25rem 1.25rem',
                        background: isMe ? 'linear-gradient(135deg, var(--primary) 0%, #1d4ed8 100%)' : 'rgba(255,255,255,0.07)',
                        color: 'white',
                        fontSize: '0.9rem',
                        lineHeight: '1.5',
                        border: isMe ? 'none' : '1px solid rgba(255,255,255,0.08)'
                      }}>
                        {msg.message}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Footer: Fixed at bottom */}
            <div className="p-4" style={{ borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.3)', flexShrink: 0 }}>
              <form onSubmit={sendMessage} className="flex gap-2">
                <input 
                  type="text" 
                  className="input-field flex-1" 
                  placeholder="Describe your issue or ask for help..." 
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
                <button type="submit" className="btn btn-primary" style={{ padding: '0 1.5rem', borderRadius: '12px' }}>
                  <Send size={18} />
                </button>
              </form>
            </div>
          </div>
        ) : (
          /* Selection Screen (Staff or Guest) */
          <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
            {/* Sidebar for Staff */}
            {!isGuest ? (
              <div style={{ width: '100%', padding: '2rem', overflowY: 'auto' }}>
                <div className="flex justify-between items-center mb-6">
                  <h3>Active Guest Requests</h3>
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20">
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#3b82f6' }} className="animate-pulse"></span>
                    <span className="text-[10px] font-bold text-blue-400">MONITORING LIVE</span>
                  </div>
                </div>
                {activeSessions.length === 0 ? (
                  <div className="text-center py-20 opacity-40">
                    <HeadphonesIcon size={48} className="mx-auto mb-4" />
                    <p>No active guest sessions at the moment.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {activeSessions.map((session, i) => {
                      const unread = Math.max(0, session.message_count - (lastReadCountsRef.current[session.session_id] || 0));
                      
                      return (
                      <div key={i} className="flex flex-col p-5 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)', transition: 'transform 0.2s', boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>
                        <div className="flex justify-between items-start mb-4">
                          <div style={{ flex: 1 }}>
                            <div className="text-[10px] text-muted uppercase tracking-wider font-bold mb-1 opacity-50">New Support Request</div>
                            <h4 className="text-lg font-bold" style={{ color: 'var(--primary)', marginBottom: '0.2rem' }}>
                              {session.user_id || 'Anonymous Guest'}
                            </h4>
                            <p className="text-[10px] text-muted font-mono opacity-40">Session Ref: {session.session_id.split('-')[0]}</p>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold" style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#3b82f6' }}>
                              {session.active_users} ONLINE
                            </span>
                            {unread > 0 && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', animation: 'pulse 2s infinite' }}>
                                {unread} NEW {unread === 1 ? 'MESSAGE' : 'MESSAGES'}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2 mt-2">
                          <button className="btn btn-primary btn-sm flex-1" onClick={() => connectWebSocket(session.session_id)}>
                            Respond Now
                          </button>
                          {user?.role === 'admin' && (
                            <button className="btn btn-ghost btn-sm text-danger" style={{ border: '1px solid rgba(239, 68, 68, 0.1)' }} onClick={() => deleteSession(session.session_id)}>
                              Delete
                            </button>
                          )}
                        </div>
                      </div>
                    )})}
                  </div>
                )}
              </div>
            ) : (
              /* Guest Start Screen */
              <div className="flex flex-col items-center justify-center w-full" style={{ padding: '4rem' }}>
                <div style={{ padding: '2rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '2rem', marginBottom: '2rem' }}>
                  <HeadphonesIcon size={64} className="text-primary" />
                </div>
                <h2 className="mb-3 text-center">Emergency Support Chat</h2>
                <p className="text-muted text-center mb-10 max-w-md leading-relaxed">
                  Our 24/7 staff is ready to assist you with safety concerns, medical needs, or general inquiries. Once started, a team member will be with you immediately.
                </p>
                <button 
                  className="btn btn-primary flex items-center gap-3" 
                  style={{ padding: '1rem 2.5rem', borderRadius: '16px', fontWeight: 'bold', fontSize: '1rem' }}
                  onClick={startNewSession}
                  disabled={loading}
                >
                  {loading ? <Loader2 className="animate-spin" /> : <MessageSquare size={20} />}
                  Start Support Chat
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveChat;
