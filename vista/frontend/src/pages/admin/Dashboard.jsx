function AdminDashboard() {
  return (
    <div className="dashboard">
      <h2>Welcome, Admin</h2>

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
        <div className="stat-card">
          <div className="stat-label">Total Teachers</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">High Risk Students</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Attendance Today</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Requests</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Users</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Recent Activity</h3>
      <table className="data-table">
        <thead>
          <tr><th>Time</th><th>User</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="3" style={{ textAlign: 'center', color: '#64748b' }}>No recent activity</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default AdminDashboard;
