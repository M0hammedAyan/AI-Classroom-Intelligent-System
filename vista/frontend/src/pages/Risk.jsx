import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function RiskPage({ auth }) {
  const navigate = useNavigate();
  const [flags, setFlags] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => { loadFlags(); }, [filter]);

  async function loadFlags() {
    setLoading(true);
    const url = filter ? `${BASE_URL}/risk?risk_level=${filter}` : `${BASE_URL}/risk`;
    try {
      const res = await fetch(url, { headers });
      if (res.ok) { const data = await res.json(); setFlags(data.flags || []); }
    } catch {} finally { setLoading(false); }
  }

  async function recomputeAll() {
    await fetch(`${BASE_URL}/risk/recompute-all`, { method: 'POST', headers });
    loadFlags();
  }

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Risk Flags ({flags.length})</h2>
          <p className="v-page-subtitle">Click student for SHAP explanation</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <select className="v-select" value={filter} onChange={e => setFilter(e.target.value)} style={{ width: '140px' }}>
            <option value="">All levels</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          {auth.role === 'admin' && <button className="v-btn v-btn-primary" onClick={recomputeAll}>Recompute All</button>}
        </div>
      </div>

      {loading ? <div className="v-loading">Loading...</div> : (
        <div className="v-table-container">
          <table className="v-table">
            <thead><tr><th>Student</th><th>Level</th><th>Reasons</th><th>Confidence</th><th>Computed</th></tr></thead>
            <tbody>
              {flags.length === 0 ? (
                <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No risk flags</td></tr>
              ) : flags.map(f => (
                <tr key={f.student_id} onClick={() => navigate(`/student/${f.student_id}`)}>
                  <td style={{ fontWeight: 500 }}>{f.student_name || f.student_id}</td>
                  <td><span className={`v-badge v-badge-${f.risk_level}`}>{f.risk_level}</span></td>
                  <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{(f.reasons || []).slice(0, 2).join(' · ') || '—'}</td>
                  <td>{f.confidence}</td>
                  <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{f.computed_at ? new Date(f.computed_at).toLocaleDateString() : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default RiskPage;
