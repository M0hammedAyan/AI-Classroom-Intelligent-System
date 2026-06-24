import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function TeacherDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/dashboard/teacher`, { headers }).then(r => r.json()),
      fetch(`${BASE_URL}/students`, { headers }).then(r => r.json()),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.json()),
    ]).then(([dash, studs, risk]) => {
      setData(dash);
      const flags = risk.flags || [];
      const enriched = (studs.students || []).map(s => {
        const flag = flags.find(f => f.student_id === s.student_id);
        return { ...s, risk_level: flag?.risk_level || 'none', reasons: flag?.reasons || [] };
      });
      setStudents(enriched);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  const atRisk = students.filter(s => s.risk_level === 'high' || s.risk_level === 'medium');

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Teacher Workspace</h2>
          <p className="v-page-subtitle">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
        </div>
        <button className="v-btn v-btn-primary" onClick={() => navigate('/teacher/attendance')}>Mark Attendance</button>
      </div>

      <div className="v-kpi-grid">
        <div className="v-kpi" onClick={() => navigate('/teacher/classes')}>
          <div className="v-kpi-label">My Classes</div>
          <div className="v-kpi-value">{data?.my_classes || 0}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/teacher/marks')}>
          <div className="v-kpi-label">My Subjects</div>
          <div className="v-kpi-value">{data?.my_subjects || 0}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/teacher/attendance')}>
          <div className="v-kpi-label">Present Today</div>
          <div className="v-kpi-value">{data?.present_today || 0}</div>
        </div>
        <div className="v-kpi">
          <div className="v-kpi-label">At Risk</div>
          <div className="v-kpi-value danger">{atRisk.length}</div>
        </div>
      </div>

      {atRisk.length > 0 && (
        <div className="v-section">
          <div className="v-table-container">
            <div className="v-table-header">
              <span className="v-table-title">Students at Risk</span>
            </div>
            <table className="v-table">
              <thead><tr><th>Student</th><th>Class</th><th>Risk</th><th>Reason</th></tr></thead>
              <tbody>
                {atRisk.map(s => (
                  <tr key={s.student_id} onClick={() => navigate(`/teacher/student/${s.student_id}`)}>
                    <td style={{ fontWeight: 500 }}>{s.name}</td>
                    <td>{s.class}</td>
                    <td><span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span></td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{s.reasons?.[0] || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="v-section">
        <div className="v-table-container">
          <div className="v-table-header">
            <span className="v-table-title">All Students ({students.length})</span>
          </div>
          <table className="v-table">
            <thead><tr><th>ID</th><th>Name</th><th>Class</th><th>Risk</th></tr></thead>
            <tbody>
              {students.map(s => (
                <tr key={s.student_id} onClick={() => navigate(`/teacher/student/${s.student_id}`)}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{s.student_id}</td>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                  <td>{s.class}</td>
                  <td>{s.risk_level !== 'none' ? <span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span> : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default TeacherDashboard;
