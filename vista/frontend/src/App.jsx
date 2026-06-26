import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import RoleLayout from './layouts/RoleLayout';
import Dashboard from './pages/Dashboard';
import StudentsPage from './pages/Students';
import AttendancePage from './pages/Attendance';
import RiskPage from './pages/Risk';
import StudentProfile from './pages/shared/StudentProfile';
import EnrollPage from './pages/Enroll';
import TestRecognition from './pages/TestRecognition';

function App() {
  const [auth, setAuth] = useState(() => {
    const stored = localStorage.getItem('vista_auth');
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (auth) localStorage.setItem('vista_auth', JSON.stringify(auth));
    else localStorage.removeItem('vista_auth');
  }, [auth]);

  if (!auth) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login onLogin={setAuth} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    );
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true },
    { path: '/students', label: 'Students', icon: '🎓' },
    { path: '/attendance', label: 'Attendance', icon: '✅' },
    { path: '/risk', label: 'Risk Flags', icon: '⚠️' },
  ];

  // Add role-specific items
  if (['admin', 'hos'].includes(auth.role)) {
    navItems.push({ path: '/enroll', label: 'Enrollment', icon: '📸' });
  }
  navItems.push({ path: '/test', label: 'Test Recognition', icon: '🔍' });

  return (
    <BrowserRouter>
      <RoleLayout auth={auth} onLogout={() => setAuth(null)} title={auth.role.toUpperCase()} subtitle="VISTA Platform" navItems={navItems}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard auth={auth} />} />
          <Route path="/students" element={<StudentsPage auth={auth} />} />
          <Route path="/attendance" element={<AttendancePage auth={auth} />} />
          <Route path="/risk" element={<RiskPage auth={auth} />} />
          <Route path="/enroll" element={<EnrollPage auth={auth} />} />
          <Route path="/test" element={<TestRecognition auth={auth} />} />
          <Route path="/student/:studentId" element={<StudentProfile auth={auth} />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </RoleLayout>
    </BrowserRouter>
  );
}

export default App;
