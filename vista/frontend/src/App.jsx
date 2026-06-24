import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AttendanceLog from './pages/AttendanceLog';
import RiskFlags from './pages/RiskFlags';
import StudentDetail from './pages/StudentDetail';
import Enroll from './pages/Enroll';
import TestRecognition from './pages/TestRecognition';
import Layout from './components/Layout';

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

  const handleLogin = (data) => {
    setAuth(data);
  };

  const handleLogout = () => {
    setAuth(null);
  };

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

  return (
    <BrowserRouter>
      <Layout auth={auth} onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Dashboard auth={auth} />} />
          <Route path="/attendance" element={<AttendanceLog auth={auth} />} />
          <Route path="/risk" element={<RiskFlags auth={auth} />} />
          <Route path="/student/:studentId" element={<StudentDetail auth={auth} />} />
          <Route path="/enroll" element={<Enroll auth={auth} />} />
          <Route path="/test" element={<TestRecognition auth={auth} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
