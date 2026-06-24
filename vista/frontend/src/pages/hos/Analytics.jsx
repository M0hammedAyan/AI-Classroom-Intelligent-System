function HOSAnalytics() {
  return (
    <div className="dashboard">
      <h2>School Analytics</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">School Attendance %</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg GPA</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">At-Risk Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Interventions Active</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Attendance Trends</h3>
      <div className="chart-placeholder" style={{ height: 200, background: '#f1f5f9', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
        Chart will be rendered here
      </div>

      <h3 className="section-title">Department Comparison</h3>
      <div className="chart-placeholder" style={{ height: 200, background: '#f1f5f9', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
        Chart will be rendered here
      </div>
    </div>
  );
}

export default HOSAnalytics;
