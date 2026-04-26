import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import BroadcastListener from './components/BroadcastListener';
import Login from './views/Login';
import Register from './views/Register';
import Dashboard from './views/Dashboard';
import Chat from './views/Chat';
import Safety from './views/Safety';
import Logs from './views/Logs';
import Users from './views/Users';
import LiveChat from './views/LiveChat';
import Sensors from './views/Sensors';
import HotelMaps from './views/HotelMaps';

const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  if (loading) return <div className="loading">Loading...</div>;
  if (!token) return <Navigate to="/login" />;
  return children;
};

const AppContent = () => {
  const { token } = useAuth();

  return (
    <div className="app-container">
      {token && <Navbar />}
      {token && <BroadcastListener />}
      <main className="main-content">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route 
            path="/dashboard" 
            element={<ProtectedRoute><Dashboard /></ProtectedRoute>} 
          />
          <Route 
            path="/chat" 
            element={<ProtectedRoute><Chat /></ProtectedRoute>} 
          />
          <Route 
            path="/maps" 
            element={<ProtectedRoute><HotelMaps /></ProtectedRoute>} 
          />
          <Route 
            path="/safety" 
            element={<ProtectedRoute><Safety /></ProtectedRoute>} 
          />
          <Route 
            path="/logs" 
            element={<ProtectedRoute><Logs /></ProtectedRoute>} 
          />
          <Route 
            path="/users" 
            element={<ProtectedRoute><Users /></ProtectedRoute>} 
          />
          <Route 
            path="/live-support" 
            element={<ProtectedRoute><LiveChat /></ProtectedRoute>} 
          />
          <Route 
            path="/sensors" 
            element={<ProtectedRoute><Sensors /></ProtectedRoute>} 
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
