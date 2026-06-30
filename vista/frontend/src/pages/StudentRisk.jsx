import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function StudentRiskPage({ auth }) {
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/student-portal/risk`, { headers: { Authorization: `Bearer ${auth.token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(setRisk)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading risk status...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">My Risk Status</h2>
          <p className="v-page-subtitle">AI-generated academic risk assessment</p>
        </div>
      </div>

      {!risk || risk.risk_level === 'unknown' ? (
        <div className="v-card" style={{textAlign:'center',padding:'var(--s10)'}}>
          <p style={{color:'var(--text-muted)'}}>No risk assessment computed yet. Check back after a few weeks of attendance data.</p>
        </div>
      ) : (
        <>
          {/* Risk Level Card */}
          <div className="v-kpi-grid" style={{marginBottom:'var(--s6)'}}>
            <div className="v-kpi">
              <div className="v-kpi-label">Risk Level</div>
              <div className={`v-kpi-value ${risk.risk_level === 'high' ? 'danger' : risk.risk_level === 'medium' ? 'warning' : 'success'}`}>
                {risk.risk_level.toUpperCase()}
              </div>
            </div>
            <div className="v-kpi">
              <div className="v-kpi-label">Confidence</div>
              <div className="v-kpi-value">{risk.confidence || '—'}</div>
            </div>
            <div className="v-kpi">
              <div className="v-kpi-label">Last Computed</div>
              <div className="v-kpi-value" style={{fontSize:'16px'}}>{risk.computed_at ? new Date(risk.computed_at).toLocaleDateString() : '—'}</div>
            </div>
          </div>

          {/* Reasons */}
          {risk.reasons && risk.reasons.length > 0 && (
            <div className="v-section">
              <div className="v-card" style={{borderLeft: `3px solid ${risk.risk_level === 'high' ? 'var(--danger)' : risk.risk_level === 'medium' ? 'var(--warning)' : 'var(--success)'}`}}>
                <h4 style={{fontSize:'14px',fontWeight:600,marginBottom:'var(--s3)'}}>Why this risk level?</h4>
                <ul style={{paddingLeft:'20px',fontSize:'13px',color:'var(--text-secondary)'}}>
                  {risk.reasons.map((r, i) => <li key={i} style={{marginBottom:'6px'}}>{r}</li>)}
                </ul>
              </div>
            </div>
          )}

          {/* Advice */}
          <div className="v-section">
            <div className="v-card" style={{background:'var(--success-light)',border:'1px solid rgba(5,150,105,0.2)'}}>
              <h4 style={{fontSize:'14px',fontWeight:600,color:'var(--success)',marginBottom:'var(--s3)'}}>💡 How to improve</h4>
              <ul style={{paddingLeft:'20px',fontSize:'13px',color:'var(--text-secondary)'}}>
                {risk.risk_level === 'high' && (
                  <>
                    <li>Attend every class this week — consistency matters most</li>
                    <li>Speak to your mentor about catching up</li>
                    <li>Submit any pending assignments immediately</li>
                  </>
                )}
                {risk.risk_level === 'medium' && (
                  <>
                    <li>Maintain regular attendance for the next 2 weeks</li>
                    <li>Focus on upcoming assessments — a single good score helps</li>
                    <li>Meet your mentor if you need support</li>
                  </>
                )}
                {risk.risk_level === 'low' && (
                  <>
                    <li>Keep up the good work!</li>
                    <li>Continue attending regularly</li>
                    <li>Stay consistent with assignments</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default StudentRiskPage;
