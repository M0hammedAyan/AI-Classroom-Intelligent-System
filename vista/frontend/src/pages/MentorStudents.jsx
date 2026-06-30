import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function MentorStudents({ auth }) {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/mentor/students`, { headers: { Authorization: `Bearer ${auth.token}` } })
      .then(r => r.ok ? r.json() : { students: [] })
      .then(d => setStudents(d.students || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading students...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">My Students ({students.length})</h2>
          <p className="v-page-subtitle">Students assigned to you — sorted by risk</p>
        </div>
      </div>

      {students.length === 0 ? (
        <div className="v-empty">No students assigned. Ask your HOP to assign students.</div>
      ) : (
        <div className="v-table-container">
          <table className="v-table">
            <thead><tr><th>Name</th><th>ID</th><th>Class</th><th>Risk</th><th>Primary Reason</th></tr></thead>
            <tbody>
              {students.map(s => (
                <tr key={s.student_id} onClick={() => navigate(`/student/${s.student_id}`)}>
                  <td style={{fontWeight:500}}>{s.name}</td>
                  <td style={{fontFamily:'var(--mono)',fontSize:'12px'}}>{s.student_id}</td>
                  <td>{s.class}</td>
                  <td><span className={`v-badge v-badge-${s.risk_level === 'unknown' ? 'info' : s.risk_level}`}>{s.risk_level}</span></td>
                  <td style={{fontSize:'12px',color:'var(--text-muted)'}}>{s.risk_reasons?.[0] || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default MentorStudents;
