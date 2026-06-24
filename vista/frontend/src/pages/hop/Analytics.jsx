function HOPAnalytics() {
  return (
    <div className="dashboard">
      <h2>Department Analytics</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Dept Attendance %</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Score</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">At-Risk Count</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pass Rate</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Attendance Trends</h3>
      <div className="chart-placeholder" style={{ height: 200, background: '#f1f5f9', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
        Chart will be rendered here
      </div>

      <h3 className="section-title">Subject Performance</h3>
      <div className="chart-placeholder" style={{ height: 200, background: '#f1f5f9', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
        Chart will be rendered here
      </div>
    </div>
  );
}

export default HOPAnalytics;
