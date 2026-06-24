import { useState, useEffect } from 'react';
import { listRiskFlags, recomputeRisk } from '../api/client';
import './RiskFlags.css';

function RiskFlags({ auth }) {
  const [flags, setFlags] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [recomputing, setRecomputing] = useState('');

  useEffect(() => {
    loadFlags();
  }, [filter]);

  async function loadFlags() {
    setLoading(true);
    setError('');
    try {
      const res = await listRiskFlags(filter || null);
      setFlags(res.flags);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRecompute(studentId) {
    if (auth.role !== 'admin') {
      alert('Only admins can recompute risk.');
      return;
    }
    setRecomputing(studentId);
    try {
      await recomputeRisk(studentId);
      await loadFlags();
    } catch (err) {
      alert(`Recompute failed: ${err.message}`);
    } finally {
      setRecomputing('');
    }
  }

  return (
    <div className="risk-page">
      <div className="page-header">
        <h2>Risk Flags</h2>
        <div className="header-controls">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            aria-label="Filter by risk level"
          >
            <option value="">All Levels</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading-msg">Loading risk data...</div>
      ) : flags.length === 0 ? (
        <p className="no-data-msg">No risk flags found for the selected filter.</p>
      ) : (
        <div className="risk-cards">
          {flags.map((flag) => (
            <div className={`risk-card ${flag.risk_level}`} key={flag.student_id}>
              <div className="risk-card-header">
                <div>
                  <div className="risk-card-name">{flag.student_name}</div>
                  <div className="risk-card-id">{flag.student_id}</div>
                </div>
                <span className={`risk-badge ${flag.risk_level}`}>
                  {flag.risk_level}
                </span>
              </div>

              {flag.reasons.length > 0 && (
                <ul className="risk-reasons">
                  {flag.reasons.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              )}

              <div className="risk-card-footer">
                <span className="confidence-tag">
                  Confidence: {flag.confidence}
                </span>
                <span className="computed-at">
                  {flag.computed_at
                    ? new Date(flag.computed_at).toLocaleDateString()
                    : '—'}
                </span>
                {auth.role === 'admin' && (
                  <button
                    className="recompute-btn"
                    onClick={() => handleRecompute(flag.student_id)}
                    disabled={recomputing === flag.student_id}
                  >
                    {recomputing === flag.student_id ? 'Computing...' : 'Recompute'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RiskFlags;
