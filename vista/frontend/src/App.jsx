import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';

// Role-specific layouts
import AdminLayout from './layouts/AdminLayout';
import HOSLayout from './layouts/HOSLayout';
import HOPLayout from './layouts/HOPLayout';
import MentorLayout from './layouts/MentorLayout';
import TeacherLayout from './layouts/TeacherLayout';

function App() {
  const [auth, setAuth] = useState(() => {
    const stored = localStorage.getItem('vista_auth');
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (auth) {
      localStorage.setItem('vista_auth', JSON.stringify(auth));
    } else {
      localStorage.removeItem('vista_auth');
    }
  }, [auth]);

  const handleLogin = (data) => setAuth(data);
  const handleLogout = () => setAuth(null);

  if (!auth) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    );
  }

  // Role-based redirect after login
  const roleHome = {
    admin: '/admin',
    hos: '/hos',
    hop: '/hop',
    mentor: '/mentor',
    teacher: '/teacher',
  };

  const home = roleHome[auth.role] || '/teacher';

  return (
    <BrowserRouter>
      <Routes>
        {/* Role-specific route groups */}
        <Route path="/admin/*" element={<AdminLayout auth={auth} onLogout={handleLogout} />} />
        <Route path="/hos/*" element={<HOSLayout auth={auth} onLogout={handleLogout} />} />
        <Route path="/hop/*" element={<HOPLayout auth={auth} onLogout={handleLogout} />} />
        <Route path="/mentor/*" element={<MentorLayout auth={auth} onLogout={handleLogout} />} />
        <Route path="/teacher/*" element={<TeacherLayout auth={auth} onLogout={handleLogout} />} />

        {/* Default redirect to role home */}
        <Route path="/" element={<Navigate to={home} replace />} />
        <Route path="/login" element={<Navigate to={home} replace />} />
        <Route path="*" element={<Navigate to={home} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
