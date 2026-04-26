import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Map, Loader2, Info, Edit, Trash2, Plus, MapPin, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const HotelMaps = () => {
  const [maps, setMaps] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showMapModal, setShowMapModal] = useState(false);
  const [showLocModal, setShowLocModal] = useState(false);
  const [mapData, setMapData] = useState({ file: null, floor: 1, description: '' });
  const [locData, setLocData] = useState({ name: '', floor: '' });
  const [editingLocId, setEditingLocId] = useState(null);
  
  const { user } = useAuth();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [mapsRes, locsRes] = await Promise.all([
        axios.get('/api/v1/hotel/maps'),
        axios.get('/api/v1/hotel/locations')
      ]);
      setMaps(mapsRes.data);
      setLocations(locsRes.data);
    } catch (err) {
      console.error("Failed to load data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const submitMap = async (e) => {
    e.preventDefault();
    if (!mapData.file) return alert("Please select an image file.");
    const formData = new FormData();
    formData.append('file', mapData.file);
    formData.append('floor_number', mapData.floor);
    formData.append('description', mapData.description);
    try {
      await axios.post('/api/v1/hotel/maps/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setShowMapModal(false);
      setMapData({ file: null, floor: 1, description: '' });
      fetchData();
    } catch (err) { alert("Failed to upload map."); }
  };

  const submitLocation = async (e) => {
    e.preventDefault();
    try {
      if (editingLocId) {
        await axios.put(`/api/v1/hotel/locations/${editingLocId}`, locData);
      } else {
        await axios.post('/api/v1/hotel/locations', locData);
      }
      setShowLocModal(false);
      setEditingLocId(null);
      setLocData({ name: '', floor: '' });
      fetchData();
    } catch (err) { alert(editingLocId ? "Failed to update location." : "Failed to add location. It might already exist."); }
  };

  const deleteMap = async (id) => {
    if (!window.confirm("Delete this map?")) return;
    try { await axios.delete(`/api/v1/hotel/maps/${id}`); fetchData(); } catch (err) { alert("Failed to delete map."); }
  };

  const deleteLocation = async (id) => {
    if (!window.confirm("Delete this location?")) return;
    try { await axios.delete(`/api/v1/hotel/locations/${id}`); fetchData(); } catch (err) { alert("Failed to delete location."); }
  };

  const openEditLocation = (loc) => {
    setEditingLocId(loc.id);
    setLocData({ name: loc.name, floor: loc.floor || '' });
    setShowLocModal(true);
  };

  const updateDescription = async (id, oldDesc) => {
    const newDesc = window.prompt("Enter new description:", oldDesc);
    if (newDesc === null || newDesc === oldDesc) return;
    const formData = new FormData();
    formData.append('description', newDesc);
    try {
      await axios.put(`/api/v1/hotel/maps/${id}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchData();
    } catch (err) { alert("Failed to update description."); }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Map size={32} className="text-primary" />
          <div>
            <h1>Hotel Management</h1>
            <p className="text-muted mt-2">Manage floor maps and predefined locations for incident reporting</p>
          </div>
        </div>
        
        {user?.role === 'admin' && (
          <div className="flex gap-3">
            <button className="btn btn-ghost" onClick={() => setShowLocModal(true)} style={{ color: '#fbbf24', borderColor: 'rgba(251,191,36,0.3)' }}>
              <MapPin size={18} /> ADD LOCATION
            </button>
            <button className="btn btn-ghost" onClick={() => setShowMapModal(true)} style={{ color: '#60a5fa', borderColor: 'rgba(96,165,250,0.3)' }}>
              <Plus size={18} /> UPLOAD MAP
            </button>
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
        {/* Main Maps Section */}
        <div>
          {loading ? (
            <div className="flex justify-center items-center py-20"><Loader2 className="animate-spin text-primary" size={48} /></div>
          ) : maps.length === 0 ? (
            <div className="glass-card flex flex-col items-center justify-center py-20 text-muted">
              <Map size={64} style={{ opacity: 0.2, marginBottom: '1rem' }} /><p>No floor maps uploaded.</p>
            </div>
          ) : (
            <div className="grid gap-6">
              {maps.map((map) => (
                <div key={map.id} className="glass-card overflow-hidden" style={{ padding: 0 }}>
                  <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between' }}>
                    <div>
                      <h2 style={{ fontSize: '1.25rem' }}>Floor {map.floor_number}</h2>
                      <p className="text-muted flex items-center gap-2 mt-1"><Info size={16} /> {map.description}</p>
                    </div>
                    {user?.role === 'admin' && (
                      <div className="flex gap-2">
                        <button className="btn btn-ghost" onClick={() => updateDescription(map.id, map.description)} style={{ padding: '0.5rem' }}><Edit size={16} /></button>
                        <button className="btn btn-ghost" onClick={() => deleteMap(map.id)} style={{ padding: '0.5rem', color: '#ef4444' }}><Trash2 size={16} /></button>
                      </div>
                    )}
                  </div>
                  <div style={{ width: '100%', background: '#000', display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                    <img 
                      src={`/api/v1/hotel/maps/image/${map.id}`} 
                      alt="Map" 
                      style={{ maxWidth: '100%', maxHeight: '500px', borderRadius: '8px' }} 
                      onError={(e) => {
                        console.error("Image load failed for map:", map.id);
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <div style={{ display: 'none', color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                      <Info size={48} style={{ opacity: 0.2, margin: '0 auto 1rem' }} />
                      <p>Image could not be loaded from server.</p>
                      <p style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>ID: {map.id}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar: Locations Management */}
        <div className="flex flex-col gap-6">
          <div className="glass-card">
            <h3 className="flex items-center gap-2 mb-4"><MapPin size={18} className="text-primary" /> Active Locations</h3>
            <div className="flex flex-col gap-2">
              {locations.length === 0 ? (
                <p className="text-xs text-muted">No predefined locations yet.</p>
              ) : (
                locations.map(loc => (
                  <div 
                    key={loc.id} 
                    className="flex items-center justify-between p-3 rounded-lg transition-all hover:bg-white/10" 
                    style={{ 
                      background: 'rgba(255,255,255,0.05)', 
                      border: '1px solid rgba(255,255,255,0.1)',
                      marginBottom: '0.5rem'
                    }}
                  >
                    <div>
                      <p className="text-sm font-semibold text-white">{loc.name}</p>
                      {loc.floor && <p className="text-xs text-muted" style={{ color: '#94a3b8' }}>Floor {loc.floor}</p>}
                    </div>
                    {user?.role === 'admin' && (
                      <div className="flex gap-2">
                        <button 
                          onClick={() => openEditLocation(loc)} 
                          className="hover:text-primary transition-colors" 
                          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', color: '#60a5fa' }}
                          title="Edit Location"
                        >
                          <Edit size={16} />
                        </button>
                        <button 
                          onClick={() => deleteLocation(loc.id)} 
                          className="hover:text-danger transition-colors" 
                          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', color: '#ef4444' }}
                          title="Delete Location"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <AnimatePresence>
        {showMapModal && (
          <div className="modal-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(8px)' }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }} className="glass-card" style={{ width: '100%', maxWidth: '500px', padding: '2rem' }}>
              <h2>Upload Floor Map</h2>
              <form onSubmit={submitMap} className="flex flex-col gap-4 mt-6">
                <div className="input-group"><label>Map Image</label><input type="file" className="input-field" accept="image/*" onChange={e => setMapData({...mapData, file: e.target.files[0]})} required /></div>
                <div className="input-group"><label>Floor Number</label><input type="number" className="input-field" value={mapData.floor} onChange={e => setMapData({...mapData, floor: e.target.value})} required /></div>
                <div className="input-group"><label>Description</label><input type="text" className="input-field" value={mapData.description} onChange={e => setMapData({...mapData, description: e.target.value})} required /></div>
                <div className="flex gap-4 mt-4"><button type="button" className="btn btn-ghost flex-1" onClick={() => setShowMapModal(false)}>CANCEL</button><button type="submit" className="btn btn-primary flex-1">UPLOAD</button></div>
              </form>
            </motion.div>
          </div>
        )}

        {showLocModal && (
          <div className="modal-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(8px)' }}>
            <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }} className="glass-card" style={{ width: '100%', maxWidth: '400px', padding: '2rem' }}>
              <h2>{editingLocId ? 'Edit Location' : 'Add Location'}</h2>
              <form onSubmit={submitLocation} className="flex flex-col gap-4 mt-6">
                <div className="input-group"><label>Location Name</label><input type="text" className="input-field" placeholder="e.g. Grand Lobby" value={locData.name} onChange={e => setLocData({...locData, name: e.target.value})} required /></div>
                <div className="input-group"><label>Floor (Optional)</label><input type="number" className="input-field" value={locData.floor} onChange={e => setLocData({...locData, floor: e.target.value})} /></div>
                <div className="flex gap-4 mt-4">
                  <button type="button" className="btn btn-ghost flex-1" onClick={() => { setShowLocModal(false); setEditingLocId(null); setLocData({ name: '', floor: '' }); }}>CANCEL</button>
                  <button type="submit" className="btn btn-primary flex-1">{editingLocId ? 'UPDATE' : 'ADD'}</button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default HotelMaps;
