function TeacherMarks() {
  return (
    <div className="dashboard">
      <h2>Marks Entry</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Subjects</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Entries Pending</div>
          <div className="stat-value">—</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Score</div>
          <div className="stat-value">—</div>
        </div>
      </div>

      <h3 className="section-title">Enter Marks</h3>
      <div className="form-row" style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <select className="form-input"><option>Select Class</option></select>
        <select className="form-input"><option>Select Subject</option></select>
        <select className="form-input"><option>Exam Type</option></select>
      </div>

      <h3 className="section-title">Student Marks</h3>
      <table className="data-table">
        <thead>
          <tr><th>Roll No</th><th>Student</th><th>Max Marks</th><th>Obtained</th><th>Grade</th></tr>
        </thead>
        <tbody>
          <tr><td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>Select class and subject to view</td></tr>
        </tbody>
      </table>
    </div>
  );
}

export default TeacherMarks;
