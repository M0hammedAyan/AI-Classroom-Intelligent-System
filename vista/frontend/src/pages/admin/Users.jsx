function AdminUsers() {
  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>User Management</h2>
        <button className="btn btn-primary">+ Create User</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Users</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Admins</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Teachers</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Mentors</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">All Users</h3>
      <table className="data-table">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Role</th><th>School/Dept</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No users found</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default AdminUsers;
