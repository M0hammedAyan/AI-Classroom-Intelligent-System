function HOPDashboard() {
  return (
    <div className="dashboard">
      <h2>Department Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Classes</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Subjects</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">At-Risk Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Attendance Rate</div>
          <div className="stat-value">— %</div>
        </div>
      </div>

      <h3 className="section-title">Recent Alerts</h3>
      <table className="data-table">
        <thead>
          <tr><th>Student</th><th>Risk Level</th><th>Reason</th><th>Date</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>No alerts</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOPDashboard;
