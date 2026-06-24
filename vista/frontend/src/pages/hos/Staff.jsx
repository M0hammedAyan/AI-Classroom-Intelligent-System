function HOSStaff() {
  return (
    <div className="dashboard">
      <h2>Staff</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">HOPs</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Mentors</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Teachers</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Staff</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Staff List</h3>
      <table className="data-table">
        <thead>
          <tr><th>Name</th><th>Role</th><th>Department</th><th>Email</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>No staff found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOSStaff;
