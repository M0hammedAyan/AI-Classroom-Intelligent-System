function HOPClasses() {
  return (
    <div className="dashboard">
      <h2>Class Sections</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Classes</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Class Size</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Classes in Department</h3>
      <table className="data-table">
        <thead>
          <tr><th>Class</th><th>Section</th><th>Students</th><th>Class Teacher</th><th>Attendance %</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No classes found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOPClasses;
