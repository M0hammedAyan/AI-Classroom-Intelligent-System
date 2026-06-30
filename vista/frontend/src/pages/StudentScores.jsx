import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function StudentScoresPage({ auth }) {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/student-portal/scores`, { headers: { Authorization: `Bearer ${auth.token}` } })
      .then(r => r.ok ? r.json() : { scores: [] })
      .then(d => setScores(d.scores || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading scores...</div>;

  const avg = scores.length > 0 ? (scores.reduce((s, x) => s + x.pct, 0) / scores.length).toFixed(1) : '—';

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">My Scores</h2>
          <p className="v-page-subtitle">Average: {avg}% across {scores.length} assessments</p>
        </div>
      </div>

      <div className="v-table-container">
        <table className="v-table">
          <thead><tr><th>Subject</th><th>Score</th><th>Max</th><th>Percentage</th><th>Date</th></tr></thead>
          <tbody>
            {scores.length === 0 ? (
              <tr><td colSpan="5" style={{textAlign:'center',color:'var(--text-muted)'}}>No scores recorded yet</td></tr>
            ) : scores.map((s, i) => (
              <tr key={i}>
                <td style={{fontWeight:500}}>{s.subject}</td>
                <td>{s.score}</td>
                <td>{s.max_score}</td>
                <td><span className={`v-badge v-badge-${s.pct >= 60 ? 'low' : s.pct >= 40 ? 'medium' : 'high'}`}>{s.pct}%</span></td>
                <td style={{color:'var(--text-muted)'}}>{s.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StudentScoresPage;
