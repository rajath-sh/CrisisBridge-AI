import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Activity, ShieldAlert, ShieldCheck, Loader2, Thermometer, Flame, Droplets, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SENSOR_API_BASE = (import.meta.env.VITE_SENSOR_API_URL || 'http://localhost:8001') + '/sensor';

const Sensors = () => {
  const { user } = useAuth();
  const [sensors, setSensors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggerLoading, setTriggerLoading] = useState(false);
  const [newSensor, setNewSensor] = useState({ sensor_id: '', type: 'smoke', zone: 'lobby', threshold: 100 });
  const [registering, setRegistering] = useState(false);

  // Both Admin and Staff can access this dashboard now
  const hasAccess = user?.role === 'admin' || user?.role === 'staff';

  const fetchData = async () => {
    try {
      const [sensorsRes, alertsRes, readingsRes] = await Promise.all([
        axios.get(`${SENSOR_API_BASE}/list`),
        axios.get(`${SENSOR_API_BASE}/alerts`),
        axios.get(`${SENSOR_API_BASE}/latest-readings`)
      ]);
      setSensors(sensorsRes.data);
      setAlerts(alertsRes.data);
      setReadings(readingsRes.data.readings || []);
    } catch (err) {
      console.error("Failed to fetch sensor data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (hasAccess) {
      fetchData();
      const interval = setInterval(fetchData, 3000); // Poll every 3 seconds for live data
      return () => clearInterval(interval);
    }
  }, [hasAccess]);

  const triggerDemoSpike = async (sensorId) => {
    setTriggerLoading(true);
    try {
      await axios.post(`${SENSOR_API_BASE}/queue-spike?sensor_id=${sensorId}`);
      alert(`Spike queued for sensor ${sensorId}. It will trigger within 5 seconds.`);
    } catch (err) {
      console.error("Failed to queue spike", err);
      alert("Failed to queue spike.");
    } finally {
      setTriggerLoading(false);
    }
  };

  const deleteSensor = async (sensorId) => {
    if (!window.confirm(`Are you sure you want to delete sensor ${sensorId}?`)) return;
    try {
      await axios.delete(`${SENSOR_API_BASE}/${sensorId}`);
      fetchData();
    } catch (err) {
      console.error("Failed to delete sensor", err);
      alert("Failed to delete sensor.");
    }
  };

  const clearAlerts = async () => {
    if (!window.confirm("Are you sure you want to clear all alerts?")) return;
    try {
      await axios.delete(`${SENSOR_API_BASE}/alerts`);
      fetchData();
    } catch (err) {
      console.error("Failed to clear alerts", err);
      alert("Failed to clear alerts.");
    }
  };

  const handleRegisterSensor = async (e) => {
    e.preventDefault();
    setRegistering(true);
    try {
      await axios.post(`${SENSOR_API_BASE}/register`, newSensor);
      setNewSensor({ sensor_id: '', type: 'smoke', zone: 'lobby', threshold: 100 });
      fetchData();
    } catch (err) {
      console.error("Failed to register sensor", err);
      alert(err.response?.data?.detail || "Failed to register sensor.");
    } finally {
      setRegistering(false);
    }
  };

  if (!hasAccess) {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '50vh' }}>
        <div className="glass-card text-center" style={{ padding: '3rem' }}>
          <ShieldAlert size={48} className="text-danger mx-auto mb-4" />
          <h2>Access Denied</h2>
          <p className="text-muted mt-2">Only authorized staff can access the Sensor Dashboard.</p>
        </div>
      </div>
    );
  }

  const getSensorIcon = (type) => {
    switch(type) {
      case 'temperature': return <Thermometer size={16} />;
      case 'smoke': return <Flame size={16} />;
      case 'water': return <Droplets size={16} />;
      default: return <Activity size={16} />;
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="dashboard-container"
      style={{ maxWidth: '1200px', margin: '0 auto' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '1rem' }}>
          <Activity size={32} color="#3b82f6" />
        </div>
        <div>
          <h1>Sensor Dashboard</h1>
          <p className="text-muted">Live telemetry and alert monitoring</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="animate-spin text-primary" size={32} />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Sensors & Demo */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            
            <div className="glass-card p-0 overflow-hidden">
              <div className="p-4 flex justify-between items-center" style={{ borderBottom: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
                <h3 className="flex items-center gap-2"><Activity size={18} /> Active Sensors</h3>
              </div>

              {/* Add New Sensor Form */}
              {user.role === 'admin' && (
                <div className="p-4" style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255,255,255,0.02)' }}>
                  <form onSubmit={handleRegisterSensor} className="flex gap-2 items-center flex-wrap">
                    <input 
                      type="text" 
                      placeholder="Sensor ID (e.g. S1)" 
                      className="input-field py-1 px-2 text-sm w-32" 
                      value={newSensor.sensor_id}
                      onChange={e => setNewSensor({...newSensor, sensor_id: e.target.value})}
                      required
                    />
                    <input 
                      type="text" 
                      placeholder="Type (e.g. smoke)" 
                      className="input-field py-1 px-2 text-sm w-32"
                      value={newSensor.type}
                      onChange={e => setNewSensor({...newSensor, type: e.target.value})}
                      required
                    />
                    <input 
                      type="text" 
                      placeholder="Zone" 
                      className="input-field py-1 px-2 text-sm w-24" 
                      value={newSensor.zone}
                      onChange={e => setNewSensor({...newSensor, zone: e.target.value})}
                      required
                    />
                    <input 
                      type="number" 
                      placeholder="Threshold" 
                      className="input-field py-1 px-2 text-sm w-24" 
                      value={newSensor.threshold}
                      onChange={e => setNewSensor({...newSensor, threshold: Number(e.target.value)})}
                      required
                    />
                    <button type="submit" className="btn btn-primary btn-sm" disabled={registering}>
                      {registering ? 'Adding...' : 'Add Sensor'}
                    </button>
                  </form>
                </div>
              )}

              <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                {!Array.isArray(sensors) || sensors.length === 0 ? (
                  <p className="text-muted col-span-2">No sensors registered.</p>
                ) : (
                  sensors.map((sensor) => (
                    <div key={sensor.sensor_id} className="p-4 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-semibold flex items-center gap-2">
                            {getSensorIcon(sensor.type)} {sensor.sensor_id}
                          </h4>
                          <p className="text-xs text-muted mt-1 uppercase tracking-wider">{sensor.zone}</p>
                        </div>
                        {user.role === 'admin' && (
                          <button 
                            className="btn btn-ghost btn-sm text-danger px-2" 
                            onClick={() => deleteSensor(sensor.sensor_id)}
                            title="Remove Sensor"
                          >
                            Delete
                          </button>
                        )}
                      </div>
                      
                      <div className="flex justify-between items-end mt-4 pt-4" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                        <div>
                          <p className="text-xs text-muted mb-1">Threshold</p>
                          <p className="font-mono text-sm">{sensor?.threshold || 'N/A'}</p>
                        </div>
                        <button 
                          className="btn btn-primary btn-sm flex items-center gap-2"
                          onClick={() => triggerDemoSpike(sensor.sensor_id)}
                          disabled={triggerLoading}
                        >
                          <Zap size={14} />
                          Trigger Demo Spike
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="glass-card p-0 overflow-hidden">
              <div className="p-4" style={{ borderBottom: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
                <h3 className="flex items-center gap-2"><Activity size={18} /> Live Telemetry Feed</h3>
              </div>
              <div className="p-0 overflow-y-auto" style={{ maxHeight: '400px' }}>
                <table className="w-full text-left" style={{ borderCollapse: 'collapse' }}>
                  <thead style={{ position: 'sticky', top: 0, background: 'rgba(20,20,20,0.95)', backdropFilter: 'blur(4px)' }}>
                    <tr>
                      <th className="p-3 text-xs text-muted font-semibold uppercase tracking-wider">Time</th>
                      <th className="p-3 text-xs text-muted font-semibold uppercase tracking-wider">Sensor ID</th>
                      <th className="p-3 text-xs text-muted font-semibold uppercase tracking-wider text-right">Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <AnimatePresence>
                      {Array.isArray(readings) && readings.slice(0, 15).map((reading, idx) => (
                        <motion.tr 
                          key={idx}
                          initial={{ opacity: 0, backgroundColor: 'rgba(59, 130, 246, 0.2)' }}
                          animate={{ opacity: 1, backgroundColor: 'transparent' }}
                          style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
                        >
                          <td className="p-3 text-sm text-muted font-mono">
                            {reading?.timestamp ? new Date(reading.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second:'2-digit' }) : 'N/A'}
                          </td>
                          <td className="p-3 text-sm">{reading?.sensor_id || 'Unknown'}</td>
                          <td className="p-3 text-sm font-mono text-right">{reading?.value !== undefined ? Number(reading.value).toFixed(2) : 'N/A'}</td>
                        </motion.tr>
                      ))}
                    </AnimatePresence>
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          {/* Right Column: Alerts */}
          <div className="glass-card p-0 overflow-hidden h-fit">
            <div className="p-4 flex justify-between items-center text-danger" style={{ borderBottom: '1px solid var(--border)', background: 'rgba(239, 68, 68, 0.1)' }}>
              <div className="flex items-center gap-2">
                <ShieldAlert size={18} />
                <h3 className="font-semibold text-danger">Active Alerts</h3>
              </div>
              {user.role === 'admin' && alerts.length > 0 && (
                <button 
                  className="btn btn-ghost btn-sm text-danger px-2 border border-red-500/30"
                  onClick={clearAlerts}
                >
                  Clear All
                </button>
              )}
            </div>
            
            <div className="p-4 flex flex-col gap-3 max-h-[600px] overflow-y-auto">
              {!Array.isArray(alerts) || alerts.length === 0 ? (
                <div className="text-center py-8">
                  <ShieldCheck size={32} className="text-success mx-auto mb-2 opacity-50" />
                  <p className="text-muted text-sm">No recent alerts</p>
                </div>
              ) : (
                alerts.map((alert, idx) => (
                  <div key={idx} className="p-3 rounded-lg" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-bold text-danger text-sm">{alert.sensor_id}</span>
                      <span className="text-xs opacity-70">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-end mt-2">
                      <div className="text-xs">
                        <p className="opacity-70 mb-1">Peak Value</p>
                        <p className="font-mono text-danger font-bold">{alert?.value !== undefined ? Number(alert.value).toFixed(2) : 'N/A'}</p>
                      </div>
                      <div className="text-xs text-right">
                        <p className="opacity-70 mb-1">Type</p>
                        <p className="uppercase font-bold tracking-wider">{alert?.type || 'CRITICAL'}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      )}
    </motion.div>
  );
};

export default Sensors;
