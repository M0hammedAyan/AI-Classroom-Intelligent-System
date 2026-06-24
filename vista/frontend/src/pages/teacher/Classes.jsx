function TeacherClasses() {
  return (
    <div className="dashboard">
      <h2>My Classes</h2>

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
          <div className="stat-label">Avg Attendance</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Assigned Classes</h3>
      <table className="data-table">
        <thead>
          <tr><th>Class</th><th>Section</th><th>Students</th><th>Subject</th><th>Avg Attendance %</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No classes assigned</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default TeacherClasses;
