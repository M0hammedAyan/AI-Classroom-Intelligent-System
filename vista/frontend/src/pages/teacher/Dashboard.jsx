function TeacherDashboard() {
  return (
    <div className="dashboard">
      <h2>Teacher Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">My Classes</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">My Subjects</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Attendance Today</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">At-Risk in Class</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Assignments</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Today's Schedule</h3>
      <table className="data-table">
        <thead>
          <tr><th>Time</th><th>Class</th><th>Subject</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>No classes scheduled</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default TeacherDashboard;
