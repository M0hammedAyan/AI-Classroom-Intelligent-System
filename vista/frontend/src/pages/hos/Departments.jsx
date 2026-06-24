function HOSDepartments() {
  return (
    <div className="dashboard">
      <h2>Departments</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Departments</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Attendance</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Departments in School</h3>
      <table className="data-table">
        <thead>
          <tr><th>Department</th><th>Code</th><th>HOP</th><th>Students</th><th>Attendance %</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No departments found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOSDepartments;
