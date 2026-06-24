import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function AdminDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState({ students: [], flags: [] });
  const [loading, setLoading] = useState(true);

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/students`, { headers }).then(r => r.json()),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.json()),
    ]).then(([s, r]) => {
      setData({ students: s.students || [], flags: r.flags || [] });
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  const high = data.flags.filter(f => f.risk_level === 'high');
  const medium = data.flags.filter(f => f.risk_level === 'medium');
  const urgent = [...high, ...medium];

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Dashboard</h2>
          <p className="v-page-subtitle">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
        </div>
      </div>

      {/* KPI strip — compact */}
      <div className="v-kpi-grid">
        <div className="v-kpi" onClick={() => navigate('/admin/users')}>
          <div className="v-kpi-label">Students</div>
          <div className="v-kpi-value">{data.students.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/admin/analytics')}>
          <div className="v-kpi-label">High Risk</div>
          <div className="v-kpi-value danger">{high.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/admin/analytics')}>
          <div className="v-kpi-label">Medium Risk</div>
          <div className="v-kpi-value warning">{medium.length}</div>
        </div>
        <div className="v-kpi">
          <div className="v-kpi-label">Flagged Total</div>
          <div className="v-kpi-value">{data.flags.length}</div>
        </div>
      </div>

      {/* Work queue — what needs attention today */}
      {urgent.length > 0 && (
        <div className="v-section">
          <div className="v-table-container">
            <div className="v-table-header">
              <span className="v-table-title">Needs Attention ({urgent.length})</span>
            </div>
            <table className="v-table">
              <thead>
                <tr><th>Student</th><th>Level</th><th>Reason</th><th>Confidence</th></tr>
              </thead>
              <tbody>
                {urgent.map(s => (
                  <tr key={s.student_id} onClick={() => navigate(`/admin/student/${s.student_id}`)}>
                    <td style={{ fontWeight: 500 }}>{s.student_name || s.student_id}</td>
                    <td><span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span></td>
                    <td style={{ color: 'var(--text-secondary)' }}>{s.reasons?.[0] || '—'}</td>
                    <td>{s.confidence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* All students — dense table */}
      <div className="v-section">
        <div className="v-table-container">
          <div className="v-table-header">
            <span className="v-table-title">All Students</span>
            <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/admin/reports')}>Export</button>
          </div>
          <table className="v-table">
            <thead>
              <tr><th>ID</th><th>Name</th><th>Class</th><th>Status</th></tr>
            </thead>
            <tbody>
              {data.students.map(s => (
                <tr key={s.student_id} onClick={() => navigate(`/admin/student/${s.student_id}`)}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{s.student_id}</td>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                  <td>{s.class}</td>
                  <td>{s.is_active ? <span className="v-badge v-badge-low">Active</span> : <span className="v-badge v-badge-high">Inactive</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
