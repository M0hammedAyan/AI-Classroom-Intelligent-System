function HOSDashboard() {
  return (
    <div className="dashboard">
      <h2>School Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Departments</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Teachers</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Attendance Rate</div>
          <div className="stat-value">— %</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">High Risk</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-label">Medium Risk</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Risk Distribution</h3>
      <div className="chart-placeholder" style={{ height: 200, background: '#f1f5f9', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
        Chart will be rendered here
      </div>
    </div>
  );
}

export default HOSDashboard;
