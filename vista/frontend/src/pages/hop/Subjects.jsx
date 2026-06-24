function HOPSubjects() {
  return (
    <div className="dashboard">
      <h2>Subject Management</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Subjects</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Theory</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Practicals</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Electives</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Subjects</h3>
      <table className="data-table">
        <thead>
          <tr><th>Subject</th><th>Code</th><th>Type</th><th>Teacher</th><th>Credits</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No subjects found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOPSubjects;
