import { Routes, Route, Navigate } from 'react-router-dom';
import RoleLayout from './RoleLayout';
import AdminDashboard from '../pages/admin/Dashboard';
import SchoolsPage from '../pages/admin/Schools';
import DepartmentsPage from '../pages/admin/Departments';
import UsersPage from '../pages/admin/Users';
import AnalyticsPage from '../pages/admin/Analytics';
import ReportsPage from '../pages/admin/Reports';

const NAV_ITEMS = [
  { path: '/admin', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/admin/schools', label: 'Schools', icon: '🏫' },
  { path: '/admin/departments', label: 'Departments', icon: '🏛️' },
  { path: '/admin/users', label: 'Users & Roles', icon: '👥' },
  { path: '/admin/analytics', label: 'Analytics', icon: '📈' },
  { path: '/admin/reports', label: 'Reports', icon: '📋' },
];

function AdminLayout({ auth, onLogout }) {
  if (auth.role !== 'admin') return <Navigate to="/" replace />;

  return (
    <RoleLayout auth={auth} onLogout={onLogout} title="Admin" subtitle="Institution Admin" navItems={NAV_ITEMS} accentColor="#1a1a2e">
      <Routes>
        <Route index element={<AdminDashboard />} />
        <Route path="schools" element={<SchoolsPage />} />
        <Route path="departments" element={<DepartmentsPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Routes>
    </RoleLayout>
  );
}

export default AdminLayout;
