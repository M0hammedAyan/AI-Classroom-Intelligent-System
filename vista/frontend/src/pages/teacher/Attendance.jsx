function TeacherAttendance() {
  return (
    <div className="dashboard">
      <h2>Attendance</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Marked Today</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Present Today</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Absent Today</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Mark Attendance</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxWidth: 500, marginBottom: '1.5rem' }}>
        <select className="form-input"><option>Select Class</option></select>
        <div style={{ border: '2px dashed #cbd5e1', borderRadius: 8, padding: '2rem', textAlign: 'center', color: '#64748b' }}>
          Upload class image for face recognition attendance
        </div>
        <button className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Submit Attendance</button>
      </div>

      <h3 className="section-title">Attendance Log</h3>
      <table className="data-table">
        <thead>
          <tr><th>Date</th><th>Class</th><th>Present</th><th>Absent</th><th>Percentage</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>No records</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default TeacherAttendance;
