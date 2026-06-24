function MentorStudents() {
  return (
    <div className="dashboard">
      <h2>My Students</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Assigned</div>
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
        <div className="stat-card low">
          <div className="stat-label">Low Risk</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Student List</h3>
      <table className="data-table">
        <thead>
          <tr><th>Name</th><th>Roll No</th><th>Class</th><th>Attendance</th><th>Risk Level</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No students assigned</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default MentorStudents;
