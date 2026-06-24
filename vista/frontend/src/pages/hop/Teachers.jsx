function HOPTeachers() {
  return (
    <div className="dashboard">
      <h2>Teachers</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Teachers</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Subjects Covered</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Classes/Teacher</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Teacher Assignments</h3>
      <table className="data-table">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Subjects</th><th>Classes</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>No teachers found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOPTeachers;
