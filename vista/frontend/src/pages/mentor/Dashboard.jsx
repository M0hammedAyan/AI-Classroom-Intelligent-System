function MentorDashboard() {
  return (
    <div className="dashboard">
      <h2>Mentor Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">My Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">High Risk</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Attendance %</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Score</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Interventions</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Students Needing Attention</h3>
      <table className="data-table">
        <thead>
          <tr><th>Student</th><th>Risk Level</th><th>Attendance</th><th>Last Contact</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>All students on track</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default MentorDashboard;
