import { Routes, Route, Navigate } from 'react-router-dom';
import RoleLayout from './RoleLayout';
import TeacherDashboard from '../pages/teacher/Dashboard';
import TeacherClasses from '../pages/teacher/Classes';
import TeacherAttendance from '../pages/teacher/Attendance';
import TeacherMarks from '../pages/teacher/Marks';
import TeacherAssignments from '../pages/teacher/Assignments';
import TeacherReports from '../pages/teacher/Reports';

const NAV_ITEMS = [
  { path: '/teacher', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/teacher/classes', label: 'My Classes', icon: '📚' },
  { path: '/teacher/attendance', label: 'Attendance', icon: '✅' },
  { path: '/teacher/marks', label: 'Marks', icon: '📝' },
  { path: '/teacher/assignments', label: 'Assignments', icon: '📄' },
  { path: '/teacher/reports', label: 'Reports', icon: '📋' },
];

function TeacherLayout({ auth, onLogout }) {
  if (!['teacher', 'admin', 'hos', 'hop'].includes(auth.role)) return <Navigate to="/" replace />;

  return (
    <RoleLayout auth={auth} onLogout={onLogout} title="Teacher" subtitle="Subject Teacher" navItems={NAV_ITEMS} accentColor="#312e81">
      <Routes>
        <Route index element={<TeacherDashboard />} />
        <Route path="classes" element={<TeacherClasses />} />
        <Route path="attendance" element={<TeacherAttendance />} />
        <Route path="marks" element={<TeacherMarks />} />
        <Route path="assignments" element={<TeacherAssignments />} />
        <Route path="reports" element={<TeacherReports />} />
      </Routes>
    </RoleLayout>
  );
}

export default TeacherLayout;
