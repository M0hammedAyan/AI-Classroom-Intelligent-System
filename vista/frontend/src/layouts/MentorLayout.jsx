import { Routes, Route, Navigate } from 'react-router-dom';
import RoleLayout from './RoleLayout';
import MentorDashboard from '../pages/mentor/Dashboard';
import MentorStudents from '../pages/mentor/Students';
import MentorWatchlist from '../pages/mentor/Watchlist';
import MentorInterventions from '../pages/mentor/Interventions';
import MentorReports from '../pages/mentor/Reports';
import StudentProfile from '../pages/shared/StudentProfile';

const NAV_ITEMS = [
  { path: '/mentor', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/mentor/students', label: 'My Students', icon: '🎓' },
  { path: '/mentor/watchlist', label: 'Watchlist', icon: '👁️' },
  { path: '/mentor/interventions', label: 'Interventions', icon: '🤝' },
  { path: '/mentor/reports', label: 'Reports', icon: '📋' },
];

function MentorLayout({ auth, onLogout }) {
  if (!['mentor', 'admin', 'hos', 'hop'].includes(auth.role)) return <Navigate to="/" replace />;

  return (
    <RoleLayout auth={auth} onLogout={onLogout} title="Mentor" subtitle="Student Mentor" navItems={NAV_ITEMS} accentColor="#1b4332">
      <Routes>
        <Route index element={<MentorDashboard />} />
        <Route path="students" element={<MentorStudents />} />
        <Route path="watchlist" element={<MentorWatchlist />} />
        <Route path="interventions" element={<MentorInterventions />} />
        <Route path="reports" element={<MentorReports />} />
        <Route path="student/:studentId" element={<StudentProfile auth={auth} />} />
      </Routes>
    </RoleLayout>
  );
}

export default MentorLayout;
