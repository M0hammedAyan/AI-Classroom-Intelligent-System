import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function MentorDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetch(`${BASE_URL}/mentor/dashboard`, { headers })
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Mentor Workspace</h2>
          <p className="v-page-subtitle">Student monitoring & intervention tracking</p>
        </div>
      </div>

      <div className="v-kpi-grid">
        <div className="v-kpi" onClick={() => navigate('/mentor/students')}>
          <div className="v-kpi-label">Assigned Students</div>
          <div className="v-kpi-value">{data?.assigned_students || 0}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/mentor/watchlist')}>
          <div className="v-kpi-label">High Risk</div>
          <div className="v-kpi-value danger">{data?.high_risk || 0}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/mentor/watchlist')}>
          <div className="v-kpi-label">Medium Risk</div>
          <div className="v-kpi-value warning">{data?.medium_risk || 0}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/mentor/interventions')}>
          <div className="v-kpi-label">Interventions</div>
          <div className="v-kpi-value">{data?.recent_interventions?.length || 0}</div>
        </div>
      </div>

      {data?.recent_interventions?.length > 0 && (
        <div className="v-section">
          <div className="v-table-container">
            <div className="v-table-header">
              <span className="v-table-title">Recent Interventions</span>
              <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/mentor/interventions')}>View All</button>
            </div>
            <table className="v-table">
              <thead><tr><th>Student</th><th>Type</th><th>Outcome</th><th>Date</th></tr></thead>
              <tbody>
                {data.recent_interventions.map(i => (
                  <tr key={i.id} onClick={() => navigate(`/mentor/student/${i.student_id}`)}>
                    <td style={{ fontWeight: 500 }}>{i.student_id}</td>
                    <td>{i.type}</td>
                    <td><span className={`v-badge v-badge-${i.outcome === 'improved' ? 'low' : i.outcome === 'pending' ? 'medium' : 'info'}`}>{i.outcome}</span></td>
                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{i.created_at?.split('T')[0]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {(!data?.assigned_students || data.assigned_students === 0) && (
        <div className="v-empty">No students assigned yet. Ask your HOP to assign students to you.</div>
      )}
    </div>
  );
}

export default MentorDashboard;
