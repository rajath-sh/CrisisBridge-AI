import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldAlert, LayoutDashboard, MessageSquare, ShieldCheck, LogOut, Bell, Info, Users, HeadphonesIcon, Activity, Map, X, AlertOctagon, Radio } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [notifications, setNotifications] = React.useState([]);
  const [showNotifs, setShowNotifs] = React.useState(false);
  const [showProfileModal, setShowProfileModal] = React.useState(false);
  
  const [profileData, setProfileData] = React.useState({ full_name: '', email: '' });

  const activeSessionsRef = React.useRef(new Set());
  const seenSensorAlertsRef = React.useRef(new Set());
  const seenBroadcastsRef = React.useRef(new Set());
  const isFirstFetchRef = React.useRef(true);
  const isFirstSensorFetchRef = React.useRef(true);
  const isFirstBroadcastFetchRef = React.useRef(true);

  const fetchNotifs = async () => {
    try {
      const response = await axios.get('/api/v1/notifications');
      setNotifications(prev => {
        // Keep local chat/sensor/broadcast notifications alive during server polls
        const localNotifs = prev.filter(n => typeof n.id === 'string' && (n.id.startsWith('chat-') || n.id.startsWith('sensor-') || n.id.startsWith('broadcast-')));
        return [...localNotifs, ...response.data.notifications];
      });
    } catch (err) {
      console.error('Failed to fetch notifications');
    }
  };

  const fetchSupportRequests = async () => {
    if (user?.role === 'admin' || user?.role === 'staff') {
      try {
        const res = await axios.get('http://localhost:8002/chat/active');
        const sessions = res.data.sessions || [];
        
        let newChatDetected = false;
        const currentSessionIds = new Set(sessions.map(s => s.session_id));

        if (isFirstFetchRef.current) {
          activeSessionsRef.current = currentSessionIds;
          isFirstFetchRef.current = false;
          return;
        }

        sessions.forEach(s => {
          if (!activeSessionsRef.current.has(s.session_id)) {
            newChatDetected = true;
          }
        });

        if (newChatDetected && location.pathname !== '/live-support') {
          // New request detected AND user is in a different tab
          setNotifications(prev => [
            {
              id: 'chat-' + Date.now(),
              title: '💬 New Support Request',
              message: 'A guest is waiting for assistance in Live Support.',
              is_read: false,
              created_at: new Date().toISOString()
            },
            ...prev
          ]);
        }
        
        // Update the ref to track currently active sessions
        activeSessionsRef.current = currentSessionIds;
      } catch (err) {
        // Chat module might not be running, ignore
      }
    }
  };

  const fetchSensorAlerts = async () => {
    if (user?.role === 'admin' || user?.role === 'staff') {
      try {
        const res = await axios.get('http://localhost:8001/sensor/alerts');
        const alerts = res.data || [];
        
        const currentAlertKeys = new Set(alerts.map(a => `${a.sensor_id}-${a.timestamp}`));

        if (isFirstSensorFetchRef.current) {
          seenSensorAlertsRef.current = currentAlertKeys;
          isFirstSensorFetchRef.current = false;
          return;
        }

        alerts.forEach(a => {
          const key = `${a.sensor_id}-${a.timestamp}`;
          if (!seenSensorAlertsRef.current.has(key) && location.pathname !== '/sensors') {
            // New high-risk alert detected AND user is in a different tab
            setNotifications(prev => [
              {
                id: 'sensor-' + key,
                title: `⚠️ SENSOR ALERT: ${a.type.toUpperCase()}`,
                message: `${a.message} in ${a.zone}. Value: ${a.value}`,
                is_read: false,
                created_at: a.timestamp
              },
              ...prev
            ]);
          }
        });
        
        seenSensorAlertsRef.current = currentAlertKeys;
      } catch (err) {
        // Sensor module might not be running, ignore
      }
    }
  };

  const fetchBroadcastAlerts = async () => {
    try {
      const res = await axios.get('/api/v1/hotel/broadcast');
      const broadcasts = res.data || [];
      
      const currentBroadcastIds = new Set(broadcasts.map(b => b.id));

      if (isFirstBroadcastFetchRef.current) {
        seenBroadcastsRef.current = currentBroadcastIds;
        isFirstBroadcastFetchRef.current = false;
        return;
      }

      broadcasts.forEach(b => {
        if (!seenBroadcastsRef.current.has(b.id)) {
          // New broadcast detected!
          const newNotif = {
            id: 'broadcast-' + b.id,
            title: `📢 ANNOUNCEMENT: ${b.priority.toUpperCase()}`,
            message: b.message,
            is_read: false,
            created_at: b.created_at
          };
          
          setNotifications(prev => [newNotif, ...prev]);
        }
      });
      
      seenBroadcastsRef.current = currentBroadcastIds;
    } catch (err) {
      // Broadcast module might not be running, ignore
    }
  };

  React.useEffect(() => {
    if (user) {
      fetchNotifs();
      fetchSupportRequests();
      fetchSensorAlerts();
      fetchBroadcastAlerts();
      const interval = setInterval(() => {
        fetchNotifs();
        fetchSupportRequests();
        fetchSensorAlerts();
        fetchBroadcastAlerts();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [user, location.pathname]);

  const markAsRead = async (id) => {
    try {
      if (typeof id === 'string' && (id.startsWith('chat-') || id.startsWith('sensor-') || id.startsWith('broadcast-'))) {
        setNotifications(prev => prev.filter(n => n.id !== id));
        return;
      }
      await axios.patch(`/api/v1/notifications/${id}/read`);
      fetchNotifs();
    } catch (err) {
      console.error('Failed to mark read');
    }
  };

  const clearAll = async () => {
    try {
      // Identify DB notifications that need to be marked as read
      const unreadDbNotifications = notifications.filter(
        n => !n.is_read && !(typeof n.id === 'string' && (n.id.startsWith('chat-') || n.id.startsWith('sensor-') || n.id.startsWith('broadcast-')))
      );

      // Instantly clear all notifications from the UI (including chat and sensor ones)
      setNotifications([]);

      if (unreadDbNotifications.length === 0) {
        return;
      }

      // Mark each unread DB notification as read
      const promises = unreadDbNotifications.map(n =>
        axios.patch(`/api/v1/notifications/${n.id}/read`)
      );

      await Promise.allSettled(promises);

      // Refresh DB notifications
      fetchNotifs();
    } catch (err) {
      console.error('Failed to clear all notifications:', err);
    }
  };

  React.useEffect(() => {
    if (user) {
      setProfileData({ full_name: user.full_name || '', email: user.email || '' });
    }
  }, [user]);

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <nav className="navbar">
        <div className="logo">
          <ShieldAlert size={28} color="#3b82f6" />
          <span>CrisisBridge AI</span>
        </div>
        
        <div className="nav-links">
          <Link 
            to="/dashboard" 
            className={`btn btn-ghost ${isActive('/dashboard') ? 'active' : ''}`}
          >
            <LayoutDashboard size={18} />
            Dashboard
          </Link>
          
          <Link 
            to="/safety" 
            className={`btn btn-ghost ${isActive('/safety') ? 'active' : ''}`}
          >
            <ShieldCheck size={18} />
            Safety Check
          </Link>

          <Link 
            to="/chat" 
            className={`btn btn-ghost ${isActive('/chat') ? 'active' : ''}`}
          >
            <MessageSquare size={18} />
            AI Assistant
          </Link>

          <Link 
            to="/live-support" 
            className={`btn btn-ghost ${isActive('/live-support') ? 'active' : ''}`}
          >
            <HeadphonesIcon size={18} />
            Live Support
          </Link>

          <Link 
            to="/maps" 
            className={`btn btn-ghost ${isActive('/maps') ? 'active' : ''}`}
          >
            <Map size={18} />
            Hotel Maps
          </Link>

          {(user?.role === 'admin' || user?.role === 'staff') && (
            <Link 
              to="/sensors" 
              className={`btn btn-ghost ${isActive('/sensors') ? 'active' : ''}`}
            >
              <Activity size={18} />
              Sensors
            </Link>
          )}

          {user?.role === 'admin' && (
            <>
              <Link 
                to="/users" 
                className={`btn btn-ghost ${isActive('/users') ? 'active' : ''}`}
              >
                <Users size={18} />
                Manage Users
              </Link>
              <Link 
                to="/logs" 
                className={`btn btn-ghost ${isActive('/logs') ? 'active' : ''}`}
              >
                <Info size={18} />
                System Logs
              </Link>
            </>
          )}
        </div>

        <div className="user-profile">
          <div style={{ position: 'relative' }}>
            <button 
              className="btn btn-ghost" 
              onClick={() => setShowNotifs(!showNotifs)}
              style={{ padding: '0.5rem', border: 'none', position: 'relative' }}
            >
              <Bell size={20} color={notifications.some(n => !n.is_read) ? 'var(--primary)' : 'white'} />
              {notifications.some(n => !n.is_read) && (
                <span style={{ 
                  position: 'absolute', top: '4px', right: '4px', 
                  width: '8px', height: '8px', background: 'var(--danger)', 
                  borderRadius: '50%', border: '2px solid var(--bg-dark)' 
                }}></span>
              )}
            </button>

            <AnimatePresence>
              {showNotifs && (
                <motion.div 
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="glass-card"
                  style={{
                    position: 'absolute', top: '100%', right: 0, width: '320px',
                    marginTop: '0.5rem', maxHeight: '400px', overflowY: 'auto',
                    padding: '1rem', zIndex: 1000,
                    background: 'var(--bg-dark)',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.8)',
                    border: '1px solid var(--border)'
                  }}
                >
                  <div className="flex justify-between items-center mb-4">
                    <h4 style={{ fontSize: '0.875rem' }}>Notifications</h4>
                    <button 
                      className="text-xs"
                      onClick={(e) => { e.stopPropagation(); clearAll(); }}
                      style={{ 
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--primary)', fontWeight: 600
                      }}
                    >
                      Clear All
                    </button>
                  </div>
                  <div className="flex flex-col gap-2">
                    {notifications.filter(n => !n.is_read).length === 0 ? (
                      <p className="text-xs text-muted text-center py-4">No notifications</p>
                    ) : (
                      notifications.filter(n => !n.is_read).map(n => (
                        <div 
                          key={n.id} 
                          className="p-3 rounded-lg"
                          style={{ 
                            background: 'rgba(59, 130, 246, 0.1)',
                            border: '1px solid rgba(59,130,246,0.2)',
                            cursor: 'pointer'
                          }}
                          onClick={() => markAsRead(n.id)}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)' }} />
                            <p className="text-xs font-bold" style={{ color: 'white' }}>{n.title}</p>
                          </div>
                          <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.8)', lineHeight: '1.4' }}>{n.message}</p>
                          <p className="text-[10px] mt-2 opacity-60">
                            {n.created_at ? new Date(n.created_at.endsWith('Z') ? n.created_at : n.created_at + 'Z').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          <div 
            title="Click to view profile"
            onClick={() => setShowProfileModal(true)}
            style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', cursor: 'pointer', transition: 'transform 0.2s', marginLeft: '1rem' }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            {user?.username?.[0]?.toUpperCase() || 'A'}
          </div>

          <button 
            className="btn btn-ghost" 
            onClick={logout} 
            style={{ 
              padding: '0.5rem 0.75rem', 
              border: '1px solid rgba(239, 68, 68, 0.2)', 
              fontSize: '0.75rem', 
              fontWeight: 'bold', 
              color: '#ef4444',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginLeft: '1rem'
            }}
          >
            <LogOut size={16} />
            LOGOUT
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {showProfileModal && (
          <div 
            className="modal-overlay" 
            onClick={() => setShowProfileModal(false)}
            style={{
              position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', 
              display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999,
              backdropFilter: 'blur(12px)',
              padding: '40px',
              overflowY: 'auto'
            }}
          >
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card" 
              style={{ 
                width: '100%', 
                maxWidth: '480px', 
                padding: '2.5rem', 
                border: '1px solid var(--primary-glow)',
                margin: 'auto'
              }}
            >
              <div className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-3">
                  <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', fontWeight: 'bold' }}>
                    {user?.username?.[0]?.toUpperCase()}
                  </div>
                  <div>
                    <h2 style={{ fontSize: '1.5rem', marginBottom: '2px' }}>Account Overview</h2>
                    <p className="text-xs text-muted">Your profile details</p>
                  </div>
                </div>
                <button onClick={() => setShowProfileModal(false)} className="btn btn-ghost" style={{ padding: '0.5rem', color: 'var(--text-muted)' }}>
                  <X size={24} />
                </button>
              </div>

              <div className="flex flex-col gap-6">
                <div className="flex flex-col gap-4 p-5 rounded-2xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                  <div className="grid grid-cols-2 gap-y-6 gap-x-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] text-muted uppercase tracking-widest font-bold">FULL NAME</span>
                      <span className="text-sm font-semibold">{user?.full_name || 'Not Set'}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] text-muted uppercase tracking-widest font-bold">USERNAME</span>
                      <span className="text-sm font-semibold">{user?.username}</span>
                    </div>
                    <div className="flex flex-col gap-1 col-span-2">
                      <span className="text-[10px] text-muted uppercase tracking-widest font-bold">EMAIL ADDRESS</span>
                      <span className="text-sm font-semibold" style={{ color: 'var(--primary)' }}>{user?.email}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] text-muted uppercase tracking-widest font-bold">SYSTEM ROLE</span>
                      <span className="text-sm font-bold" style={{ color: user?.role === 'admin' ? '#ef4444' : 'var(--primary)' }}>
                        {user?.role?.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] text-muted uppercase tracking-widest font-bold">ACCOUNT STATUS</span>
                      <span className="text-sm font-semibold flex items-center gap-2">
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }} />
                        Active
                      </span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] text-muted uppercase tracking-widest font-bold">MEMBER SINCE</span>
                      <span className="text-sm font-semibold">{new Date(user?.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <button type="button" onClick={() => setShowProfileModal(false)} className="btn btn-primary w-full" style={{ padding: '0.8rem', fontWeight: 'bold', fontSize: '0.9rem' }}>
                  CLOSE OVERVIEW
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Navbar;
