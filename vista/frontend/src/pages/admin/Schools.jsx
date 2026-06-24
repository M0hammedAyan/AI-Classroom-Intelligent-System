function AdminSchools() {
  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>School Management</h2>
        <button className="btn btn-primary">+ Create School</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Schools</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Departments</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Students</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Schools</h3>
      <table className="data-table">
        <thead>
          <tr><th>School Name</th><th>Code</th><th>Departments</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>No schools found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default AdminSchools;
