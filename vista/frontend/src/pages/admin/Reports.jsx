function AdminReports() {
  return (
    <div className="dashboard">
      <h2>Reports Center</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Reports Generated</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Last Generated</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Exports</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Date Range</h3>
      <div className="form-row" style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <input type="date" className="form-input" placeholder="Start Date" />
        <input type="date" className="form-input" placeholder="End Date" />
      </div>

      <h3 className="section-title">Generate Report</h3>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button className="btn btn-primary">Attendance Report</button>
        <button className="btn btn-primary">Risk Report</button>
        <button className="btn btn-primary">Performance Report</button>
      </div>
    </div>
  );
}

export default AdminReports;
