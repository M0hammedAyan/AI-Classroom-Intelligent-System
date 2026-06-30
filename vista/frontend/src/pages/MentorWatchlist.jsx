import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function MentorWatchlist({ auth }) {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/mentor/watchlist`, { headers: { Authorization: `Bearer ${auth.token}` } })
      .then(r => r.ok ? r.json() : { students: [] })
      .then(d => setStudents(d.students || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading watchlist...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">⚠️ Watchlist</h2>
          <p className="v-page-subtitle">High and medium risk students — needs your attention</p>
        </div>
      </div>

      {students.length === 0 ? (
        <div className="v-card" style={{textAlign:'center',padding:'var(--s10)'}}>
          <p style={{fontSize:'16px',marginBottom:'var(--s2)'}}>🎉</p>
          <p style={{color:'var(--text-muted)'}}>No students currently at risk. Great work!</p>
        </div>
      ) : (
        <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
          {students.map(s => (
            <div key={s.student_id} className="v-card" style={{cursor:'pointer',borderLeft:`3px solid ${s.risk_level === 'high' ? 'var(--danger)' : 'var(--warning)'}`}} onClick={() => navigate(`/student/${s.student_id}`)}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                <div>
                  <strong style={{fontSize:'14px'}}>{s.name}</strong>
                  <p style={{fontSize:'12px',color:'var(--text-muted)',marginTop:'2px'}}>{s.student_id} · {s.class}</p>
                </div>
                <span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span>
              </div>
              {s.risk_reasons?.length > 0 && (
                <ul style={{marginTop:'var(--s3)',paddingLeft:'var(--s5)',fontSize:'12px',color:'var(--text-secondary)'}}>
                  {s.risk_reasons.slice(0, 2).map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              )}
              <div style={{marginTop:'var(--s3)',display:'flex',gap:'var(--s2)'}}>
                <button className="v-btn v-btn-sm v-btn-secondary" onClick={(e) => {e.stopPropagation(); navigate(`/student/${s.student_id}`);}}>View Profile</button>
                <button className="v-btn v-btn-sm v-btn-primary" onClick={(e) => {e.stopPropagation(); navigate('/interventions');}}>Log Intervention</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MentorWatchlist;
