function TeacherAssignments() {
  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>Assignments</h2>
        <button className="btn btn-primary">+ Create Assignment</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Active Assignments</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Submissions Pending</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Graded</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overdue</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">All Assignments</h3>
      <table className="data-table">
        <thead>
          <tr><th>Title</th><th>Class</th><th>Subject</th><th>Due Date</th><th>Submissions</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="6" style={{ textAlign: 'center', color: '#64748b' }}>No assignments created</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default TeacherAssignments;
