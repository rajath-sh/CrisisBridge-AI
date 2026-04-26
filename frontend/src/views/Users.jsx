import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users as UsersIcon, ShieldAlert, Loader2, Trash2, ShieldCheck, User as UserIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user: currentUser } = useAuth();

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/v1/users');
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await axios.patch(`/api/v1/users/${userId}/role`, { role: newRole });
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      alert('Failed to update role. Only admins can do this.');
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to permanently remove user @${username}?`)) return;
    try {
      await axios.delete(`/api/v1/users/${userId}`);
      setUsers(users.filter(u => u.id !== userId));
    } catch (err) {
      alert('Failed to remove user: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  if (currentUser?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '50vh' }}>
        <div className="glass-card text-center" style={{ padding: '3rem' }}>
          <ShieldAlert size={48} className="text-danger mx-auto mb-4" />
          <h2>Access Denied</h2>
          <p className="text-muted mt-2">Only administrators can manage users.</p>
        </div>
      </div>
    );
  }

  const staffUsers = users.filter(u => u.role === 'admin' || u.role === 'staff');
  const guestUsers = users.filter(u => u.role === 'guest');

  const UserTable = ({ title, userList, icon: Icon, color }) => (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon size={20} color={color} />
        <h2 style={{ fontSize: '1.25rem' }}>{title} <span className="text-sm text-muted">({userList.length})</span></h2>
      </div>
      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: 'rgba(255,255,255,0.02)' }}>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>User</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Details</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Role</th>
              <th style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {userList.map((u) => (
                <motion.tr 
                  key={u.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
                >
                  <td style={{ padding: '1rem' }}>
                    <div className="flex items-center gap-3">
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.8rem' }}>
                        {u.username[0].toUpperCase()}
                      </div>
                      <div>
                        <div className="font-bold text-sm">{u.full_name || 'N/A'}</div>
                        <div className="text-xs text-muted">@{u.username}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <div className="text-xs">{u.email}</div>
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <select 
                      className="input-field"
                      style={{ padding: '0.4rem', width: 'auto', minWidth: '100px', fontSize: '0.8rem' }}
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      disabled={u.id === currentUser.id}
                    >
                      <option value="guest">Guest</option>
                      <option value="staff">Staff</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
                    {u.id !== currentUser.id && (
                      <button 
                        onClick={() => handleDeleteUser(u.id, u.username)}
                        className="btn btn-ghost" 
                        style={{ padding: '0.4rem', color: 'var(--danger)', border: '1px solid rgba(239, 68, 68, 0.2)' }}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
            {userList.length === 0 && (
              <tr>
                <td colSpan="4" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No users found in this category.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="dashboard-container"
      style={{ maxWidth: '1200px', margin: '0 auto' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '3rem' }}>
        <div style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '1rem' }}>
          <UsersIcon size={32} color="#3b82f6" />
        </div>
        <div>
          <h1>User Management</h1>
          <p className="text-muted">Maintain security by managing personnel roles and access</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="animate-spin text-primary" size={32} />
        </div>
      ) : (
        <div className="flex flex-col gap-12">
          <UserTable 
            title="Operational Staff" 
            userList={staffUsers} 
            icon={ShieldCheck} 
            color="#3b82f6" 
          />
          
          <UserTable 
            title="Guests & Registered Users" 
            userList={guestUsers} 
            icon={UserIcon} 
            color="#94a3b8" 
          />
        </div>
      )}
    </motion.div>
  );
};

export default Users;
