import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Login from './pages/Login';
import RoleLayout from './layouts/RoleLayout';
import Dashboard from './pages/Dashboard';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import MentorDashboard from './pages/MentorDashboard';
import StudentAttendancePage from './pages/StudentAttendance';
import StudentScoresPage from './pages/StudentScores';
import StudentRiskPage from './pages/StudentRisk';
import StudentsPage from './pages/Students';
import AttendancePage from './pages/Attendance';
import RiskPage from './pages/Risk';
import StudentProfile from './pages/shared/StudentProfile';
import EnrollPage from './pages/Enroll';
import TestRecognition from './pages/TestRecognition';
import TeacherAttendance from './pages/TeacherAttendance';
import TeacherMarks from './pages/TeacherMarks';
import MentorStudents from './pages/MentorStudents';
import MentorWatchlist from './pages/MentorWatchlist';
import MentorInterventions from './pages/MentorInterventions';
import StudentSubjects from './pages/StudentSubjects';
import Settings from './pages/Settings';
import Assignments from './pages/Assignments';
import Timetable from './pages/Timetable';
import Announcements from './pages/Announcements';
import Materials from './pages/Materials';
import AssignmentsAcademic from './pages/AssignmentsAcademic';
import AttendanceOverride from './pages/AttendanceOverride';

function App() {
  const [auth, setAuth] = useState(() => {
    const stored = localStorage.getItem('vista_auth');
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (auth) {
      localStorage.setItem('vista_auth', JSON.stringify(auth));
      // Apply theme
      document.documentElement.setAttribute('data-theme', auth.theme || 'light');
    } else {
      localStorage.removeItem('vista_auth');
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }, [auth]);

  function handleThemeChange(newTheme) {
    setAuth(prev => ({ ...prev, theme: newTheme }));
  }

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

  const navItems = [];

  if (auth.role === 'student') {
    navItems.push({ path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true });
    navItems.push({ path: '/my-attendance', label: 'My Attendance', icon: '✅' });
    navItems.push({ path: '/my-scores', label: 'My Scores', icon: '📝' });
    navItems.push({ path: '/my-subjects', label: 'My Subjects', icon: '📚' });
    navItems.push({ path: '/timetable', label: 'Timetable', icon: '🗓️' });
    navItems.push({ path: '/hw', label: 'Assignments', icon: '📋' });
    navItems.push({ path: '/materials', label: 'Study Materials', icon: '📁' });
    navItems.push({ path: '/announcements', label: 'Notices', icon: '📢' });
    navItems.push({ path: '/my-risk', label: 'Risk Status', icon: '⚠️' });
  } else if (auth.role === 'mentor') {
    navItems.push({ path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true });
    navItems.push({ path: '/my-students', label: 'My Students', icon: '🎓' });
    navItems.push({ path: '/watchlist', label: 'Watchlist', icon: '👁️' });
    navItems.push({ path: '/interventions', label: 'Interventions', icon: '🤝' });
    navItems.push({ path: '/risk', label: 'Risk (Assigned)', icon: '⚠️' });
    navItems.push({ path: '/announcements', label: 'Notices', icon: '📢' });
    navItems.push({ path: '/timetable', label: 'Timetable', icon: '🗓️' });
  } else if (auth.role === 'teacher') {
    navItems.push({ path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true });
    navItems.push({ path: '/mark-attendance', label: 'Mark Attendance', icon: '📸' });
    navItems.push({ path: '/override', label: 'Override Attendance', icon: '✏️' });
    navItems.push({ path: '/attendance', label: 'Attendance Log', icon: '✅' });
    navItems.push({ path: '/marks', label: 'Enter Marks', icon: '📝' });
    navItems.push({ path: '/hw', label: 'Assignments', icon: '📋' });
    navItems.push({ path: '/materials', label: 'Study Materials', icon: '📁' });
    navItems.push({ path: '/students', label: 'Students (Class)', icon: '🎓' });
    navItems.push({ path: '/risk', label: 'Risk (Class)', icon: '⚠️' });
    navItems.push({ path: '/announcements', label: 'Notices', icon: '📢' });
    navItems.push({ path: '/timetable', label: 'Timetable', icon: '🗓️' });
    navItems.push({ path: '/test', label: 'Test Recognition', icon: '🔍' });
  } else if (auth.role === 'hop') {
    navItems.push({ path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true });
    navItems.push({ path: '/students', label: 'Students (Dept)', icon: '🎓' });
    navItems.push({ path: '/attendance', label: 'Attendance', icon: '✅' });
    navItems.push({ path: '/mark-attendance', label: 'Mark Attendance', icon: '📸' });
    navItems.push({ path: '/marks', label: 'Scores', icon: '📝' });
    navItems.push({ path: '/hw', label: 'Assignments', icon: '📋' });
    navItems.push({ path: '/materials', label: 'Study Materials', icon: '📁' });
    navItems.push({ path: '/risk', label: 'Risk (Dept)', icon: '⚠️' });
    navItems.push({ path: '/announcements', label: 'Announcements', icon: '📢' });
    navItems.push({ path: '/timetable', label: 'Timetable', icon: '🗓️' });
    navItems.push({ path: '/assignments', label: 'User Assignments', icon: '🔗' });
    navItems.push({ path: '/enroll', label: 'Face Enrollment', icon: '🎯' });
    navItems.push({ path: '/test', label: 'Test Recognition', icon: '🔍' });
  } else if (auth.role === 'hos') {
    navItems.push({ path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true });
    navItems.push({ path: '/students', label: 'Students (School)', icon: '🎓' });
    navItems.push({ path: '/attendance', label: 'Attendance', icon: '✅' });
    navItems.push({ path: '/mark-attendance', label: 'Mark Attendance', icon: '📸' });
    navItems.push({ path: '/marks', label: 'Scores', icon: '📝' });
    navItems.push({ path: '/hw', label: 'Assignments', icon: '📋' });
    navItems.push({ path: '/materials', label: 'Study Materials', icon: '📁' });
    navItems.push({ path: '/risk', label: 'Risk (School)', icon: '⚠️' });
    navItems.push({ path: '/announcements', label: 'Announcements', icon: '📢' });
    navItems.push({ path: '/timetable', label: 'Timetable', icon: '🗓️' });
    navItems.push({ path: '/assignments', label: 'User Assignments', icon: '🔗' });
    navItems.push({ path: '/enroll', label: 'Face Enrollment', icon: '🎯' });
    navItems.push({ path: '/test', label: 'Test Recognition', icon: '🔍' });
  } else {
    // Admin: Everything
    navItems.push({ path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true });
    navItems.push({ path: '/students', label: 'All Students', icon: '🎓' });
    navItems.push({ path: '/attendance', label: 'Attendance', icon: '✅' });
    navItems.push({ path: '/mark-attendance', label: 'Mark Attendance', icon: '📸' });
    navItems.push({ path: '/marks', label: 'Scores / LMS', icon: '📝' });
    navItems.push({ path: '/hw', label: 'Assignments', icon: '📋' });
    navItems.push({ path: '/materials', label: 'Study Materials', icon: '📁' });
    navItems.push({ path: '/risk', label: 'Risk Flags', icon: '⚠️' });
    navItems.push({ path: '/announcements', label: 'Announcements', icon: '📢' });
    navItems.push({ path: '/timetable', label: 'Timetable', icon: '🗓️' });
    navItems.push({ path: '/assignments', label: 'User Assignments', icon: '🔗' });
    navItems.push({ path: '/enroll', label: 'Face Enrollment', icon: '🎯' });
    navItems.push({ path: '/test', label: 'Test Recognition', icon: '🔍' });
  }

  return (
    <BrowserRouter>
      <RoleLayout auth={auth} onLogout={() => setAuth(null)} title={auth.role.toUpperCase()} subtitle="VISTA Platform" navItems={navItems}>
        <Routes>
          <Route path="/dashboard" element={
            auth.role === 'student' ? <StudentDashboard auth={auth} /> :
            auth.role === 'teacher' ? <TeacherDashboard auth={auth} /> :
            auth.role === 'mentor' ? <MentorDashboard auth={auth} /> :
            <Dashboard auth={auth} />
          } />
          <Route path="/students" element={<StudentsPage auth={auth} />} />
          <Route path="/attendance" element={<AttendancePage auth={auth} />} />
          <Route path="/mark-attendance" element={<TeacherAttendance auth={auth} />} />
          <Route path="/marks" element={<TeacherMarks auth={auth} />} />
          <Route path="/my-students" element={<MentorStudents auth={auth} />} />
          <Route path="/watchlist" element={<MentorWatchlist auth={auth} />} />
          <Route path="/interventions" element={<MentorInterventions auth={auth} />} />
          <Route path="/risk" element={<RiskPage auth={auth} />} />
          <Route path="/enroll" element={<EnrollPage auth={auth} />} />
          <Route path="/test" element={<TestRecognition auth={auth} />} />
          <Route path="/student/:studentId" element={<StudentProfile auth={auth} />} />
          {/* Student-only routes (separate pages) */}
          <Route path="/my-attendance" element={<StudentAttendancePage auth={auth} />} />
          <Route path="/my-scores" element={<StudentScoresPage auth={auth} />} />
          <Route path="/my-subjects" element={<StudentSubjects auth={auth} />} />
          <Route path="/my-risk" element={<StudentRiskPage auth={auth} />} />
          <Route path="/settings" element={<Settings auth={auth} onThemeChange={handleThemeChange} />} />
          <Route path="/assignments" element={<Assignments auth={auth} />} />
          <Route path="/timetable" element={<Timetable auth={auth} />} />
          <Route path="/announcements" element={<Announcements auth={auth} />} />
          <Route path="/materials" element={<Materials auth={auth} />} />
          <Route path="/hw" element={<AssignmentsAcademic auth={auth} />} />
          <Route path="/override" element={<AttendanceOverride auth={auth} />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </RoleLayout>
    </BrowserRouter>
  );
}

export default App;
