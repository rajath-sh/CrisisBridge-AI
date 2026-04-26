import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Terminal, Search, Loader2, Database, Shield, Trash2, Clock, Zap, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [clearing, setClearing] = useState(false);
  const [activeTab, setActiveTab] = useState('queries'); // 'queries' or 'incidents'

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 'queries') {
        const response = await axios.get('/api/v1/logs/queries');
        setLogs(Array.isArray(response.data) ? response.data : []);
      } else {
        const response = await axios.get('/api/v1/logs/incidents');
        setIncidents(Array.isArray(response.data) ? response.data : []);
      }
    } catch (err) {
      console.error('Failed to fetch logs', err);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const clearLogs = async () => {
    const logType = activeTab === 'queries' ? 'AI interaction' : 'incident history';
    if (!window.confirm(`Are you sure you want to permanently delete all ${logType} logs? This cannot be undone.`)) return;
    setClearing(true);
    try {
      if (activeTab === 'queries') {
        await axios.delete('/api/v1/logs/queries');
        setLogs([]);
      } else {
        // Need a clear incidents endpoint? For now just handle queries as requested
        await axios.delete('/api/v1/logs/incidents');
        setIncidents([]);
      }
    } catch (err) {
      console.error('Failed to clear logs', err);
      alert('Failed to clear logs. Please try again.');
    } finally {
      setClearing(false);
    }
  };

  const filteredLogs = logs.filter(log =>
    log.original_query?.toLowerCase().includes(filter.toLowerCase()) ||
    log.answer?.toLowerCase().includes(filter.toLowerCase())
  );

  const filteredIncidents = incidents.filter(inc =>
    inc.title?.toLowerCase().includes(filter.toLowerCase()) ||
    inc.incident_type?.toLowerCase().includes(filter.toLowerCase())
  );

  const hitCount = logs.filter(l => l.cache_status === 'hit').length;
  const hitRate = logs.length > 0 ? Math.round((hitCount / logs.length) * 100) : 0;
  const avgTime = logs.length > 0
    ? Math.round(logs.reduce((s, l) => s + (l.response_time_ms || 0), 0) / logs.length)
    : 0;

  const getCacheBadge = (status) => {
    if (status === 'hit') {
      return (
        <span style={{
          padding: '2px 8px', borderRadius: '999px', fontSize: '0.7rem', fontWeight: '700',
          background: 'rgba(16, 185, 129, 0.15)', color: 'var(--success)',
          border: '1px solid rgba(16, 185, 129, 0.3)', letterSpacing: '0.05em'
        }}>CACHED</span>
      );
    }
    return (
      <span style={{
        padding: '2px 8px', borderRadius: '999px', fontSize: '0.7rem', fontWeight: '700',
        background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)',
        border: '1px solid var(--border)', letterSpacing: '0.05em'
      }}>LIVE</span>
    );
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence === null || confidence === undefined) return <span className="text-muted" style={{ fontSize: '0.75rem' }}>—</span>;
    const pct = Math.round(confidence * 100);
    const color = pct >= 80 ? 'var(--success)' : pct >= 50 ? 'var(--warning)' : 'var(--danger)';
    return <span style={{ color, fontWeight: '700', fontSize: '0.8rem', fontFamily: 'monospace' }}>{pct}%</span>;
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{ maxWidth: '1400px', margin: '0 auto' }}
    >
      {/* Header */}
      <div className="mb-8 flex justify-between items-end flex-wrap gap-4">
        <div>
          <h1>System Activity Logs</h1>
          <div className="flex gap-4 mt-4">
            <button 
              className={`btn btn-sm ${activeTab === 'queries' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('queries')}
            >
              AI Interactions
            </button>
            <button 
              className={`btn btn-sm ${activeTab === 'incidents' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab('incidents')}
            >
              Incident History
            </button>
          </div>
        </div>
        <div className="flex gap-3 items-center flex-wrap">
          {/* Search */}
          <div style={{ position: 'relative' }}>
            <Search size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }} />
            <input
              type="text"
              className="input-field"
              placeholder="Filter logs…"
              style={{ paddingLeft: '2.25rem', width: '260px' }}
              value={filter}
              onChange={e => setFilter(e.target.value)}
            />
          </div>
          {/* Refresh */}
          <button className="btn btn-ghost btn-sm flex items-center gap-2" onClick={fetchData} title="Refresh logs">
            <RefreshCw size={14} />
            Refresh
          </button>
          {/* Clear */}
          {((activeTab === 'queries' && logs.length > 0) || (activeTab === 'incidents' && incidents.length > 0)) && (
            <button
              className="btn btn-sm flex items-center gap-2"
              style={{ background: 'rgba(239,68,68,0.12)', color: 'var(--danger)', border: '1px solid rgba(239,68,68,0.3)' }}
              onClick={clearLogs}
              disabled={clearing}
            >
              {clearing ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
              Clear Logs
            </button>
          )}
        </div>
      </div>

      {activeTab === 'queries' ? (
        <>
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="glass-card flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>
                <Terminal size={22} />
              </div>
              <div>
                <h4 style={{ fontSize: '0.8rem', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Interactions</h4>
                <p className="text-xl font-bold">{logs.length}</p>
              </div>
            </div>
            <div className="glass-card flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
                <Database size={22} />
              </div>
              <div>
                <h4 style={{ fontSize: '0.8rem', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Cache Hit Rate</h4>
                <p className="text-xl font-bold">{hitRate}%</p>
              </div>
            </div>
            <div className="glass-card flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>
                <Clock size={22} />
              </div>
              <div>
                <h4 style={{ fontSize: '0.8rem', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Avg Response Time</h4>
                <p className="text-xl font-bold">{avgTime > 0 ? `${avgTime}ms` : '—'}</p>
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
            {/* Table header */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '140px 1fr 1.4fr 70px 90px 100px',
              gap: '1rem', padding: '0.875rem 1.5rem',
              borderBottom: '1px solid var(--border)',
              background: 'rgba(255,255,255,0.02)',
              fontSize: '0.7rem', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em'
            }}>
              <span>Timestamp</span>
              <span>User Query</span>
              <span>AI Response</span>
              <span>Conf.</span>
              <span>Time</span>
              <span>Status</span>
            </div>

            {/* Rows */}
            <div style={{ maxHeight: 'calc(100vh - 420px)', overflowY: 'auto' }}>
              {loading ? (
                <div className="flex items-center justify-center py-20">
                  <Loader2 className="animate-spin text-primary" size={32} />
                </div>
              ) : filteredLogs.length === 0 ? (
                <div className="py-20 text-center text-muted">
                  <Database size={48} style={{ opacity: 0.1, margin: '0 auto 1rem' }} />
                  <p>{filter ? 'No logs match your filter.' : 'No activity logs yet.'}</p>
                </div>
              ) : (
                filteredLogs.map((log, i) => (
                  <div
                    key={log.id ?? i}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '140px 1fr 1.4fr 70px 90px 100px',
                      gap: '1rem', padding: '1.1rem 1.5rem',
                      borderBottom: '1px solid var(--border)',
                      fontSize: '0.85rem',
                      transition: 'background 0.15s',
                    }}
                    className="log-row"
                  >
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <div style={{ fontWeight: '600', color: 'var(--text-main)' }}>
                        {log.created_at ? new Date(log.created_at).toLocaleTimeString() : '—'}
                      </div>
                      <div style={{ opacity: 0.55, marginTop: '2px' }}>
                        {log.created_at ? new Date(log.created_at).toLocaleDateString() : ''}
                      </div>
                    </div>
                    <div style={{ fontWeight: '500', color: 'var(--text-main)', lineHeight: 1.4 }}>
                      {log.original_query}
                    </div>
                    <div style={{
                      color: 'var(--text-muted)',
                      display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical',
                      overflow: 'hidden', lineHeight: 1.45, fontSize: '0.8rem'
                    }}>
                      {log.answer}
                    </div>
                    <div className="flex items-center">
                      {getConfidenceBadge(log.confidence)}
                    </div>
                    <div className="flex items-center gap-1" style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      <Zap size={11} style={{ opacity: 0.5 }} />
                      {log.response_time_ms != null ? `${Math.round(log.response_time_ms)}ms` : '—'}
                    </div>
                    <div className="flex items-center">
                      {getCacheBadge(log.cache_status)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      ) : (
        <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '140px 150px 1fr 120px 100px',
            gap: '1rem', padding: '0.875rem 1.5rem',
            borderBottom: '1px solid var(--border)',
            background: 'rgba(255,255,255,0.02)',
            fontSize: '0.7rem', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em'
          }}>
            <span>Timestamp</span>
            <span>Type</span>
            <span>Incident Details</span>
            <span>Severity</span>
            <span>Status</span>
          </div>
          <div style={{ maxHeight: 'calc(100vh - 350px)', overflowY: 'auto' }}>
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="animate-spin text-primary" size={32} />
              </div>
            ) : filteredIncidents.length === 0 ? (
              <div className="py-20 text-center text-muted">
                <Shield size={48} style={{ opacity: 0.1, margin: '0 auto 1rem' }} />
                <p>No incident history found.</p>
              </div>
            ) : (
              filteredIncidents.map((inc) => (
                <div 
                  key={inc.id}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '140px 150px 1fr 120px 100px',
                    gap: '1rem', padding: '1.1rem 1.5rem',
                    borderBottom: '1px solid var(--border)',
                    fontSize: '0.85rem'
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <div style={{ fontWeight: '600', color: 'var(--text-main)' }}>
                      {new Date(inc.reported_at).toLocaleTimeString()}
                    </div>
                    <div style={{ opacity: 0.55 }}>
                      {new Date(inc.reported_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ fontWeight: '600', textTransform: 'uppercase', fontSize: '0.75rem' }}>
                    {inc.incident_type}
                  </div>
                  <div>
                    <div style={{ fontWeight: '600' }}>{inc.title}</div>
                    <div className="text-muted text-xs mt-1">{inc.description}</div>
                  </div>
                  <div>
                    <span className={`badge badge-${inc.severity.toLowerCase()}`}>{inc.severity}</span>
                  </div>
                  <div>
                    <span className={`badge badge-${inc.status.toLowerCase()}`}>{inc.status}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Logs;
