import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function MentorDashboard({ auth }) {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [flags, setFlags] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/admin/mentor/my-students`, { headers }).then(r => r.ok ? r.json() : { students: [] }),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.ok ? r.json() : { flags: [] }),
      fetch(`${BASE_URL}/announcements?page_size=3`, { headers }).then(r => r.ok ? r.json() : { announcements: [] }),
    ]).then(([s, r, a]) => {
      setStudents(s.students || []);
      setFlags(r.flags || []);
      setAnnouncements(a.announcements || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  const high = flags.filter(f => f.risk_level === 'high');
  const medium = flags.filter(f => f.risk_level === 'medium');
  const myStudentIds = students.map(s => s.student_id);
  const myHighRisk = high.filter(f => myStudentIds.includes(f.student_id));
  const myMediumRisk = medium.filter(f => myStudentIds.includes(f.student_id));

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Mentor Dashboard</h2>
          <p className="v-page-subtitle">Welcome, {auth.name} — {students.length} assigned students</p>
        </div>
      </div>

      {/* KPIs */}
      <div className="v-kpi-grid" style={{gridTemplateColumns:'repeat(4,1fr)'}}>
        <div className="v-kpi" onClick={() => navigate('/my-students')}>
          <div className="v-kpi-label">My Students</div>
          <div className="v-kpi-value">{students.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/watchlist')}>
          <div className="v-kpi-label">High Risk</div>
          <div className="v-kpi-value danger">{myHighRisk.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/watchlist')}>
          <div className="v-kpi-label">Medium Risk</div>
          <div className="v-kpi-value warning">{myMediumRisk.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/interventions')}>
          <div className="v-kpi-label">Need Attention</div>
          <div className="v-kpi-value">{myHighRisk.length + myMediumRisk.length}</div>
        </div>
      </div>

      {/* Students at risk + Student list */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s4)',marginBottom:'var(--s5)'}}>
        {/* Watchlist */}
        <div className="v-card">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'var(--s3)'}}>
            <h4 style={{fontSize:'13px',fontWeight:600}}>🚨 Watchlist</h4>
            <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/watchlist')}>View All</button>
          </div>
          {myHighRisk.length === 0 && myMediumRisk.length === 0 ? (
            <p style={{fontSize:'12px',color:'var(--success)'}}>All students are doing well!</p>
          ) : (
            <div style={{display:'flex',flexDirection:'column',gap:'var(--s2)'}}>
              {[...myHighRisk, ...myMediumRisk].slice(0, 5).map((f, i) => (
                <div key={i} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'var(--s2) var(--s3)',background:'var(--bg-secondary)',borderRadius:'var(--r-sm)',cursor:'pointer'}} onClick={() => navigate(`/student/${f.student_id}`)}>
                  <div>
                    <div style={{fontSize:'12px',fontWeight:500}}>{f.student_name}</div>
                    <div style={{fontSize:'11px',color:'var(--text-muted)'}}>{f.reasons?.[0] || '—'}</div>
                  </div>
                  <span className={`v-badge v-badge-${f.risk_level}`} style={{fontSize:'10px'}}>{f.risk_level}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* All assigned students */}
        <div className="v-card">
          <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>🎓 Assigned Students</h4>
          <div style={{display:'flex',flexDirection:'column',gap:'var(--s2)',maxHeight:'250px',overflowY:'auto'}}>
            {students.map((s, i) => (
              <div key={i} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'var(--s2) var(--s3)',borderRadius:'var(--r-sm)',cursor:'pointer',border:'1px solid var(--border)'}} onClick={() => navigate(`/student/${s.student_id}`)}>
                <div>
                  <div style={{fontSize:'12px',fontWeight:500}}>{s.student_name}</div>
                  <div style={{fontSize:'11px',color:'var(--text-muted)'}}>{s.student_id} · {s.class}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Announcements */}
      {announcements.length > 0 && (
        <div className="v-card">
          <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>📢 Recent Notices</h4>
          {announcements.map((a, i) => (
            <div key={i} style={{padding:'var(--s2) 0',borderBottom: i < announcements.length - 1 ? '1px solid var(--border)' : 'none'}}>
              <div style={{fontSize:'12px',fontWeight:600}}>{a.title}</div>
              <div style={{fontSize:'11px',color:'var(--text-muted)'}}>{a.author_name} · {new Date(a.created_at).toLocaleDateString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MentorDashboard;
