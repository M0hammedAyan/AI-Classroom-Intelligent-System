import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function Dashboard({ auth }) {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = auth.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/students`, { headers }).then(r => r.ok ? r.json() : { students: [] }),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.ok ? r.json() : { flags: [] }),
    ]).then(([s, r]) => {
      setStudents(s.students || []);
      setFlags(r.flags || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  const high = flags.filter(f => f.risk_level === 'high');
  const medium = flags.filter(f => f.risk_level === 'medium');
  const urgent = [...high, ...medium];

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Dashboard</h2>
          <p className="v-page-subtitle">Welcome, {auth.name} ({auth.role})</p>
        </div>
      </div>

      <div className="v-kpi-grid">
        <div className="v-kpi" onClick={() => navigate('/students')}>
          <div className="v-kpi-label">Students</div>
          <div className="v-kpi-value">{students.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/risk')}>
          <div className="v-kpi-label">High Risk</div>
          <div className="v-kpi-value danger">{high.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/risk')}>
          <div className="v-kpi-label">Medium Risk</div>
          <div className="v-kpi-value warning">{medium.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/attendance')}>
          <div className="v-kpi-label">Total Flags</div>
          <div className="v-kpi-value">{flags.length}</div>
        </div>
      </div>

      {urgent.length > 0 && (
        <div className="v-section">
          <div className="v-table-container">
            <div className="v-table-header">
              <span className="v-table-title">Needs Attention ({urgent.length})</span>
              <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/risk')}>View All</button>
            </div>
            <table className="v-table">
              <thead><tr><th>Student</th><th>Level</th><th>Reason</th></tr></thead>
              <tbody>
                {urgent.map(s => (
                  <tr key={s.student_id} onClick={() => navigate(`/student/${s.student_id}`)}>
                    <td style={{ fontWeight: 500 }}>{s.student_name || s.student_id}</td>
                    <td><span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span></td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{s.reasons?.[0] || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
