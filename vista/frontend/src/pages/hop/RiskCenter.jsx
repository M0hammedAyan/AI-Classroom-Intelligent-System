function HOPRiskCenter() {
  return (
    <div className="dashboard">
      <h2>Risk Center</h2>

      <div className="stats-grid">
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
        <div className="stat-card">
          <div className="stat-label">Interventions Active</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">At-Risk Students</h3>
      <table className="data-table">
        <thead>
          <tr><th>Student</th><th>Risk Level</th><th>SHAP Reasons</th><th>Recommendation</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>No at-risk students</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default HOPRiskCenter;
