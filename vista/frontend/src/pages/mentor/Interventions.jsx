function MentorInterventions() {
  return (
    <div className="dashboard">
      <h2>Interventions</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Active Interventions</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completed</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Follow-up</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Log New Intervention</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxWidth: 500, marginBottom: '1.5rem' }}>
        <select className="form-input"><option>Select Student</option></select>
        <select className="form-input"><option>Type: Meeting / Call / Email / Other</option></select>
        <textarea className="form-input" rows="3" placeholder="Notes..." />
        <button className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Save Intervention</button>
      </div>

      <h3 className="section-title">Intervention Log</h3>
      <table className="data-table">
        <thead>
          <tr><th>Date</th><th>Student</th><th>Type</th><th>Notes</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No interventions logged</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default MentorInterventions;
