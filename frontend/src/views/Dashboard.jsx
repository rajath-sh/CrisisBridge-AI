import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertOctagon, MapPin, Clock, Users, Activity, Loader2, Radio, Map, Trash2, Bell } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState({ active: 0, broadcastsCount: 0 });
  const [loading, setLoading] = useState(true);
  const [broadcasts, setBroadcasts] = useState([]);
  const [onlineStaff, setOnlineStaff] = useState([]);
  const [locations, setLocations] = useState([]);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showBroadcastModal, setShowBroadcastModal] = useState(false);
  const [showPanicModal, setShowPanicModal] = useState(false);
  
  const [reportData, setReportData] = useState({
    incident_type: '',
    severity: 'medium',
    description: '',
    floor: 1,
    zone: '',
    phone_number: '',
    image_file: null
  });
  const [broadcastData, setBroadcastData] = useState({ message: '', priority: 'normal' });
  const [panicData, setPanicData] = useState({ zone: '' });
  
  const { user } = useAuth();

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const incRes = await axios.get('/api/v1/incidents/?t=' + Date.now(), {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const bcRes = await axios.get('/api/v1/hotel/broadcast?t=' + Date.now(), {
        headers: { Authorization: `Bearer ${token}` }
      });

      const staffRes = await axios.get('/api/v1/users/staff/online?t=' + Date.now(), {
        headers: { Authorization: `Bearer ${token}` }
      });

      setIncidents(incRes.data.incidents || []);
      setBroadcasts(bcRes.data || []);
      setOnlineStaff(staffRes.data || []);
      setStats({
        active: incRes.data.active_count || 0,
        broadcastsCount: (bcRes.data || []).length
      });
    } catch (err) {
      console.error('Failed to fetch dashboard data', err?.response?.status, err?.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const refreshLocations = async () => {
    try {
      const locRes = await axios.get('/api/v1/hotel/locations?t=' + Date.now());
      setLocations(locRes.data || []);
    } catch (err) {
      console.error('Failed to fetch locations', err);
    }
  };

  useEffect(() => {
    if (showReportModal) {
      refreshLocations();
    }
  }, [showReportModal]);

  useEffect(() => {
    fetchDashboardData();
    refreshLocations(); // also load locations on mount
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handlePanic = () => {
    refreshLocations();
    setShowPanicModal(true);
  };

  const submitPanic = async (e) => {
    e.preventDefault();
    if (!panicData.zone) {
      alert("Please select a location.");
      return;
    }
    
    const selectedLoc = locations.find(l => l.name === panicData.zone);

    try {
      await axios.post('/api/v1/incidents/report', {
        incident_type: 'security',
        severity: 'critical',
        title: '🚨 PANIC ALERT: EMERGENCY AT ' + panicData.zone.toUpperCase(),
        description: `CRITICAL: Panic button triggered at ${panicData.zone}. Immediate assistance required.`,
        floor: selectedLoc?.floor || 1,
        zone: panicData.zone,
        reporter_id: user.id,
        phone_number: ''
      });
      setShowPanicModal(false);
      setPanicData({ zone: '' });
      fetchDashboardData();
      alert("🚨 Emergency reported! Help is on the way to " + panicData.zone);
    } catch (err) {
      alert("Failed to report emergency.");
    }
  };

  const submitReport = async (e) => {
    e.preventDefault();
    try {
      let image_url = null;
      if (reportData.image_file) {
        const formData = new FormData();
        formData.append('file', reportData.image_file);
        const uploadRes = await axios.post('/api/v1/incidents/upload-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        image_url = uploadRes.data.image_url;
      }

      await axios.post('/api/v1/incidents/report', {
        title: reportData.incident_type, // Use type as title
        incident_type: reportData.incident_type,
        severity: reportData.severity,
        description: reportData.description,
        floor: reportData.floor,
        zone: reportData.zone,
        phone_number: reportData.phone_number,
        image_url: image_url,
        reporter_id: user.id
      });
      setShowReportModal(false);
      setReportData({
        incident_type: '',
        severity: 'medium',
        description: '',
        floor: user.current_floor || 1,
        zone: '',
        phone_number: '',
        image_file: null
      });
      // Immediately refresh the incident list so it shows up
      await fetchDashboardData();
    } catch (err) {
      console.error('Submit error:', err?.response?.data || err);
      alert(`Failed to submit report: ${err?.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const submitBroadcast = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/v1/hotel/broadcast', broadcastData);
      setShowBroadcastModal(false);
      setBroadcastData({ message: '', priority: 'normal' });
    } catch (err) {
      alert("Failed to send broadcast. Check your permissions.");
    } finally {
      fetchDashboardData();
    }
  };

  const deleteBroadcast = async (id) => {
    if (!window.confirm("Delete this broadcast message?")) return;
    try {
      await axios.delete(`/api/v1/hotel/broadcast/${id}`);
      fetchDashboardData();
    } catch (err) {
      alert("Failed to delete broadcast.");
    }
  };

  const resolveIncident = async (id) => {
    if (!window.confirm("Mark this incident as resolved? It will be removed from the active feed.")) return;
    try {
      await axios.post('/api/v1/incidents/update-status', {
        incident_id: id,
        status: 'resolved'
      });
      await fetchDashboardData();
    } catch (err) {
      alert("Failed to resolve incident.");
    }
  };

  const getSeverityColor = (sev) => {
    switch (sev) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#94a3b8';
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="dashboard-container"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
        <div>
          <h1>Live Incident Dashboard</h1>
          <p className="text-muted mt-2">Real-time emergency monitoring and coordination</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          {user?.role === 'admin' && (
            <button className="btn btn-ghost" onClick={() => setShowBroadcastModal(true)} style={{ padding: '0.75rem 1rem', color: '#60a5fa', borderColor: 'rgba(96,165,250,0.3)' }}>
              <Radio size={18} />
              BROADCAST
            </button>
          )}
          <button className="btn btn-ghost" onClick={() => setShowReportModal(true)} style={{ padding: '0.75rem 1.5rem' }}>
            <Activity size={18} />
            REPORT INCIDENT
          </button>
          <button className="btn btn-danger pulse-red" onClick={handlePanic} style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}>
            <AlertOctagon size={22} />
            PANIC BUTTON
          </button>
        </div>
      </div>

      <AnimatePresence>
        {showReportModal && (
          <div className="modal-overlay" style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
            backdropFilter: 'blur(8px)'
          }}>
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="glass-card" 
              style={{ width: '100%', maxWidth: '500px', padding: '2rem' }}
            >
              <h2 style={{ marginBottom: '1.5rem' }}>Report Incident</h2>
              <form onSubmit={submitReport} className="flex flex-col gap-4">
                <div className="flex gap-4">
                  <div className="input-group flex-[2]">
                    <label>Incident Type</label>
                    <input 
                      className="input-field" 
                      placeholder="e.g. Fire, Medical Leak, Security..." 
                      value={reportData.incident_type}
                      onChange={e => setReportData({...reportData, incident_type: e.target.value})}
                      required
                    />
                  </div>
                  <div className="input-group flex-1">
                    <label>Severity</label>
                    <select 
                      className="input-field"
                      value={reportData.severity}
                      onChange={e => setReportData({...reportData, severity: e.target.value})}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
                <div className="input-group">
                  <label>Description (Optional)</label>
                  <textarea 
                    className="input-field" 
                    rows="2" 
                    placeholder="Details about the incident..."
                    value={reportData.description}
                    onChange={e => setReportData({...reportData, description: e.target.value})}
                  />
                </div>
                <div className="flex gap-4">
                  <div className="input-group flex-1">
                    <label>Location / Zone</label>
                    <select 
                      className="input-field"
                      value={reportData.zone}
                      onChange={e => setReportData({...reportData, zone: e.target.value})}
                    >
                      <option value="">Select Location...</option>
                      {locations && locations.length > 0 ? (
                        locations.map(loc => (
                          <option key={loc.id} value={loc.name}>{loc.name} (Floor {loc.floor})</option>
                        ))
                      ) : (
                        <option disabled>Loading locations...</option>
                      )}
                    </select>
                  </div>
                  <div className="input-group flex-1">
                    <label>Phone Number (for staff contact only)</label>
                    <input 
                      className="input-field"
                      type="tel"
                      placeholder="+91..."
                      value={reportData.phone_number}
                      onChange={e => setReportData({...reportData, phone_number: e.target.value})}
                      required
                    />
                  </div>
                </div>
                <div className="input-group">
                  <label>Upload Image (Optional)</label>
                  <input 
                    type="file"
                    className="input-field"
                    accept="image/*"
                    onChange={e => setReportData({...reportData, image_file: e.target.files[0]})}
                  />
                </div>
                <div className="flex gap-4 mt-4">
                  <button type="button" className="btn btn-ghost flex-1" onClick={() => setShowReportModal(false)}>CANCEL</button>
                  <button type="submit" className="btn btn-primary flex-1">SUBMIT REPORT</button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* Broadcast Modal */}
        {showBroadcastModal && (
          <div className="modal-overlay" style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
            backdropFilter: 'blur(8px)'
          }}>
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
              className="glass-card" style={{ width: '100%', maxWidth: '500px', padding: '2rem', border: '1px solid var(--primary)' }}
            >
              <h2 className="flex items-center gap-2 mb-6 text-primary">
                <Radio size={24} /> System Broadcast
              </h2>
              <form onSubmit={submitBroadcast} className="flex flex-col gap-4">
                <div className="input-group">
                  <label>Message</label>
                  <textarea 
                    className="input-field" rows="3" placeholder="Enter alert message to broadcast to all users..."
                    value={broadcastData.message} onChange={e => setBroadcastData({...broadcastData, message: e.target.value})} required
                  />
                </div>
                <div className="input-group">
                  <label>Priority</label>
                  <select className="input-field" value={broadcastData.priority} onChange={e => setBroadcastData({...broadcastData, priority: e.target.value})}>
                    <option value="normal">Normal / Info</option>
                    <option value="high">High / Emergency</option>
                  </select>
                </div>
                <div className="flex gap-4 mt-4">
                  <button type="button" className="btn btn-ghost flex-1" onClick={() => setShowBroadcastModal(false)}>CANCEL</button>
                  <button type="submit" className="btn btn-primary flex-1">SEND NOW</button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
        {showPanicModal && (
          <div className="modal-overlay" style={{
            position: 'fixed', inset: 0, background: 'rgba(220, 38, 38, 0.4)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
            backdropFilter: 'blur(12px)'
          }}>
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="glass-card" 
              style={{ width: '100%', maxWidth: '400px', padding: '2.5rem', border: '2px solid #ef4444', textAlign: 'center' }}
            >
              <div style={{ color: '#ef4444', marginBottom: '1.5rem' }}>
                <AlertOctagon size={64} className="animate-pulse mx-auto" />
              </div>
              <h2 style={{ color: '#ef4444', marginBottom: '0.5rem' }}>EMERGENCY PANIC</h2>
              <p className="text-muted mb-2">Select your current location to trigger the alert.</p>
              <p style={{ color: '#ef4444', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '1.5rem', textTransform: 'uppercase' }}>
                ⚠️ Heavy fines if pressed for no reason!
              </p>
              
              <form onSubmit={submitPanic} className="flex flex-col gap-6">
                <div className="input-group">
                  <select 
                    className="input-field"
                    style={{ borderColor: '#ef4444', fontSize: '1.1rem', padding: '1rem' }}
                    value={panicData.zone}
                    onChange={e => setPanicData({ zone: e.target.value })}
                    required
                  >
                    <option value="">-- SELECT LOCATION --</option>
                    {locations.map((loc, i) => (
                      <option key={i} value={loc.name}>{loc.name} (Floor {loc.floor})</option>
                    ))}
                  </select>
                </div>
                
                <div className="flex flex-col gap-3">
                  <button type="submit" className="btn btn-danger" style={{ padding: '1rem', fontSize: '1.1rem', fontWeight: 'bold' }}>
                    CONFIRM & SEND ALERT
                  </button>
                  <button type="button" className="btn btn-ghost" onClick={() => setShowPanicModal(false)}>
                    CANCEL
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '2rem' }}>
        {/* Main Feed */}
        <div className="flex flex-col gap-6">
          {/* Broadcasts Section */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 mb-1">
              <Bell size={20} className="text-primary" />
              <h3 style={{ fontSize: '1.25rem' }}>Live Announcements</h3>
            </div>
            
            {broadcasts.length > 0 ? (
              <div className="flex flex-col gap-2">
                {broadcasts.slice(0, 3).map((bc) => (
                  <motion.div 
                    key={bc.id}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card"
                    style={{ 
                      padding: '1rem 1.5rem', 
                      background: bc.priority === 'high' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255,255,255,0.03)',
                      border: bc.priority === 'high' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid var(--border)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div className="flex items-center gap-4">
                      <div style={{ color: bc.priority === 'high' ? '#ef4444' : '#60a5fa' }}>
                        <Radio size={20} className={bc.priority === 'high' ? 'animate-pulse' : ''} />
                      </div>
                      <div>
                        <p style={{ fontSize: '0.95rem', fontWeight: 500 }}>{bc.message}</p>
                        <p className="text-xs text-muted mt-1 flex items-center gap-2">
                          <Clock size={12} /> {bc.created_at ? new Date(bc.created_at.endsWith('Z') ? bc.created_at : bc.created_at + 'Z').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'} • {bc.created_by}
                        </p>
                      </div>
                    </div>
                    {user?.role === 'admin' && (
                      <button 
                        onClick={() => deleteBroadcast(bc.id)}
                        className="text-muted hover:text-danger transition-colors"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0.5rem' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="glass-card py-4" style={{ textAlign: 'center', opacity: 0.5 }}>
                <p className="text-xs">No active announcements</p>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={20} className="text-primary" />
            <h3 style={{ fontSize: '1.25rem' }}>Active Incidents</h3>
          </div>
          
          <AnimatePresence mode="popLayout">
            {loading ? (
              <div className="glass-card flex items-center justify-center" style={{ height: '200px' }}>
                <Loader2 className="animate-spin text-primary" size={32} />
              </div>
            ) : incidents.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass-card"
              >
                <p className="text-muted" style={{ textAlign: 'center' }}>No active incidents reported. All systems clear.</p>
              </motion.div>
            ) : (
              incidents
                .filter(inc => !['resolved', 'closed'].includes(inc.status?.toLowerCase()))
                .sort((a, b) => new Date(b.reported_at || 0) - new Date(a.reported_at || 0))
                .map((inc) => (
                <motion.div 
                  key={inc.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="glass-card"
                  style={{ borderLeft: `6px solid ${getSeverityColor(inc.severity)}` }}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold uppercase tracking-wider" style={{ color: getSeverityColor(inc.severity) }}>
                          {inc.incident_type}
                        </span>
                        <div className="badge">{inc.severity}</div>
                      </div>
                      <h4 className="mt-2" style={{ fontSize: '1.125rem' }}>{inc.title}</h4>
                      <p className="text-sm text-muted mt-2">{inc.description}</p>
                      
                      {inc.image_url && (
                        <div style={{ marginTop: '1rem', borderRadius: '8px', overflow: 'hidden', maxHeight: '150px', background: '#000' }}>
                          <img 
                            src={inc.image_url} 
                            alt="Incident" 
                            style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
                          />
                        </div>
                      )}
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
                        <div className="flex gap-4">
                          <p className="text-xs text-muted flex items-center gap-1">
                            <MapPin size={12} /> {inc.zone || 'Unknown Zone'} (F{inc.floor})
                          </p>
                          <p className="text-xs text-muted flex items-center gap-1">
                            <Clock size={12} /> {inc.reported_at ? new Date(inc.reported_at.endsWith('Z') ? inc.reported_at : inc.reported_at + 'Z').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                          </p>
                          <p className="text-xs font-medium flex items-center gap-1" style={{ color: 'var(--primary)' }}>
                            <Users size={12} /> {inc.reporter_name || 'Anonymous'}
                          </p>
                          {inc.phone_number && (
                            <p className="text-xs font-bold flex items-center gap-1" style={{ color: 'var(--primary)', background: 'rgba(59, 130, 246, 0.1)', padding: '4px 8px', borderRadius: '4px', display: 'inline-flex' }}>
                              <Radio size={12} /> {inc.phone_number}
                            </p>
                          )}
                        </div>
                        <span className={`badge badge-${inc.status.toLowerCase()}`}>{inc.status}</span>
                      </div>

                      {user?.role === 'admin' && (
                        <div className="mt-4 pt-4" style={{ borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'flex-end' }}>
                          <button 
                            className="btn btn-ghost" 
                            onClick={() => resolveIncident(inc.id)}
                            style={{ 
                              fontSize: '0.75rem', 
                              padding: '0.5rem 1rem', 
                              color: '#10b981', 
                              borderColor: 'rgba(16,185,129,0.3)' 
                            }}
                          >
                            MARK AS RESOLVED
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
          </div>
        </div>

        {/* Sidebar */}
        <div className="flex flex-col gap-6">
          <div className="glass-card">
            <h3>Quick Stats</h3>
            <div className="mt-6 flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted">Active Alerts</span>
                <span className="font-bold text-xl" style={{ color: incidents.length > 0 ? 'var(--danger)' : 'var(--success)' }}>
                  {stats.active}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted">Total Broadcasts</span>
                <span className="font-bold text-xl text-primary">{stats.broadcastsCount}</span>
              </div>
            </div>
          </div>

          <div className="glass-card">
            <h3 className="flex items-center gap-2">
              <Users size={18} className="text-primary" />
              Staff Online
            </h3>
            <div className="mt-4 flex flex-col gap-3">
              {onlineStaff.length > 0 ? (
                onlineStaff.map((staff, i) => (
                  <div key={i} className="flex items-center gap-3 py-1">
                    <div className="status-dot" style={{ background: 'var(--success)', boxShadow: '0 0 8px var(--success)' }}></div>
                    <div className="flex flex-col">
                      <p className="text-sm font-medium leading-none">{staff.full_name || staff.username}</p>
                      <p className="text-xs text-muted mt-1">{staff.role.toUpperCase()}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted py-2">No other staff currently active.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
