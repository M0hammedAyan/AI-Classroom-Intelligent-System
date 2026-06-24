function TeacherReports() {
  return (
    <div className="dashboard">
      <h2>Class & Subject Reports</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Reports Generated</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Classes Covered</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Last Report</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Generate Report</h3>
      <div className="form-row" style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <select className="form-input"><option>Select Class</option></select>
        <select className="form-input"><option>Select Subject</option></select>
        <input type="date" className="form-input" />
        <input type="date" className="form-input" />
      </div>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button className="btn btn-primary">Attendance Report</button>
        <button className="btn btn-primary">Marks Report</button>
        <button className="btn btn-primary">Student Progress</button>
      </div>
    </div>
  );
}

export default TeacherReports;
