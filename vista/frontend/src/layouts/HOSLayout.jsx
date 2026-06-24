import { Routes, Route, Navigate } from 'react-router-dom';
import RoleLayout from './RoleLayout';
import HOSDashboard from '../pages/hos/Dashboard';
import HOSDepartments from '../pages/hos/Departments';
import HOSStaff from '../pages/hos/Staff';
import HOSStudents from '../pages/hos/Students';
import HOSAnalytics from '../pages/hos/Analytics';
import HOSReports from '../pages/hos/Reports';

const NAV_ITEMS = [
  { path: '/hos', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/hos/departments', label: 'Departments', icon: '🏛️' },
  { path: '/hos/staff', label: 'Staff', icon: '👨‍🏫' },
  { path: '/hos/students', label: 'Students', icon: '🎓' },
  { path: '/hos/analytics', label: 'Analytics', icon: '📈' },
  { path: '/hos/reports', label: 'Reports', icon: '📋' },
];

function HOSLayout({ auth, onLogout }) {
  if (auth.role !== 'hos' && auth.role !== 'admin') return <Navigate to="/" replace />;

  return (
    <RoleLayout auth={auth} onLogout={onLogout} title="HOS" subtitle="Head of School" navItems={NAV_ITEMS} accentColor="#16213e">
      <Routes>
        <Route index element={<HOSDashboard />} />
        <Route path="departments" element={<HOSDepartments />} />
        <Route path="staff" element={<HOSStaff />} />
        <Route path="students" element={<HOSStudents />} />
        <Route path="analytics" element={<HOSAnalytics />} />
        <Route path="reports" element={<HOSReports />} />
      </Routes>
    </RoleLayout>
  );
}

export default HOSLayout;
