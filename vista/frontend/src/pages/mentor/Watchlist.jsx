function MentorWatchlist() {
  return (
    <div className="dashboard">
      <h2>Watchlist</h2>

      <div className="stats-grid">
        <div className="stat-card high">
          <div className="stat-label">High Risk</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-label">Medium Risk</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total on Watchlist</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Students by Severity</h3>
      <table className="data-table">
        <thead>
          <tr><th>Student</th><th>Risk Level</th><th>Key Reason</th><th>Days Absent (30d)</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>Watchlist empty</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default MentorWatchlist;
