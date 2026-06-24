import { Routes, Route, Navigate } from 'react-router-dom';
import RoleLayout from './RoleLayout';
import HOPDashboard from '../pages/hop/Dashboard';
import HOPClasses from '../pages/hop/Classes';
import HOPTeachers from '../pages/hop/Teachers';
import HOPSubjects from '../pages/hop/Subjects';
import HOPRiskCenter from '../pages/hop/RiskCenter';
import HOPAnalytics from '../pages/hop/Analytics';
import HOPReports from '../pages/hop/Reports';
import StudentProfile from '../pages/shared/StudentProfile';

const NAV_ITEMS = [
  { path: '/hop', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/hop/classes', label: 'Classes', icon: '📚' },
  { path: '/hop/teachers', label: 'Teachers', icon: '👨‍🏫' },
  { path: '/hop/subjects', label: 'Subjects', icon: '📖' },
  { path: '/hop/risk-center', label: 'Risk Center', icon: '⚠️' },
  { path: '/hop/analytics', label: 'Analytics', icon: '📈' },
  { path: '/hop/reports', label: 'Reports', icon: '📋' },
];

function HOPLayout({ auth, onLogout }) {
  if (!['hop', 'admin', 'hos'].includes(auth.role)) return <Navigate to="/" replace />;

  return (
    <RoleLayout auth={auth} onLogout={onLogout} title="HOP" subtitle="Head of Department" navItems={NAV_ITEMS} accentColor="#0f3460">
      <Routes>
        <Route index element={<HOPDashboard />} />
        <Route path="classes" element={<HOPClasses />} />
        <Route path="teachers" element={<HOPTeachers />} />
        <Route path="subjects" element={<HOPSubjects />} />
        <Route path="risk-center" element={<HOPRiskCenter />} />
        <Route path="analytics" element={<HOPAnalytics />} />
        <Route path="reports" element={<HOPReports />} />
        <Route path="student/:studentId" element={<StudentProfile auth={auth} />} />
      </Routes>
    </RoleLayout>
  );
}

export default HOPLayout;
