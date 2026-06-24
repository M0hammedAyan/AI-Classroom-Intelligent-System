function HOSStudents() {
  return (
    <div className="dashboard">
      <h2>Students</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Attendance</div>
          <div className="stat-value">—</div>
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

      <h3 className="section-title">All Students in School</h3>
      <table className="data-table">
        <thead>
          <tr><th>Name</th><th>Roll No</th><th>Department</th><th>Attendance</th><th>Risk</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No students found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOSStudents;
