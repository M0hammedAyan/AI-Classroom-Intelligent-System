import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function StudentAttendancePage({ auth }) {
  const [records, setRecords] = useState([]);
  const [subjectBreakdown, setSubjectBreakdown] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/student-portal/attendance`, { headers: { Authorization: `Bearer ${auth.token}` } })
        .then(r => r.ok ? r.json() : { records: [] }),
      fetch(`${BASE_URL}/student-portal/attendance/by-subject`, { headers: { Authorization: `Bearer ${auth.token}` } })
        .then(r => r.ok ? r.json() : null)
        .catch(() => null),
    ]).then(([attData, subjData]) => {
      setRecords(attData.records || []);
      setSubjectBreakdown(subjData);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading attendance...</div>;

  const present = records.filter(r => r.status === 'present').length;
  const total = records.length;
  const pct = total > 0 ? ((present / total) * 100).toFixed(1) : 0;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">My Attendance</h2>
          <p className="v-page-subtitle">
            Overall: {subjectBreakdown?.overall?.attendance_pct ?? pct}% · 
            {subjectBreakdown?.overall?.sessions_attended ?? present}/{subjectBreakdown?.overall?.total_sessions ?? total} sessions
          </p>
        </div>
      </div>

      {/* Per-subject breakdown */}
      {subjectBreakdown && subjectBreakdown.by_subject && subjectBreakdown.by_subject.length > 0 && (
        <div style={{marginBottom:'var(--s5)'}}>
          <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>By Subject</h4>
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(180px,1fr))',gap:'var(--s3)'}}>
            {subjectBreakdown.by_subject.map((s, i) => (
              <div key={i} className="v-card" style={{padding:'var(--s3)',textAlign:'center'}}>
                <div style={{fontSize:'13px',fontWeight:700,color:'var(--primary)'}}>{s.subject_code}</div>
                <div style={{fontSize:'11px',color:'var(--text-muted)',marginBottom:'var(--s2)',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{s.subject_name}</div>
                <div style={{
                  fontSize:'22px',fontWeight:700,
                  color: s.attendance_pct === null ? 'var(--text-muted)' : s.attendance_pct >= 75 ? 'var(--success)' : s.attendance_pct >= 60 ? 'var(--warning)' : 'var(--danger)',
                }}>
                  {s.attendance_pct !== null ? `${s.attendance_pct}%` : '—'}
                </div>
                <div style={{fontSize:'10px',color:'var(--text-muted)'}}>{s.sessions_attended}/{s.total_sessions} sessions</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overall KPI bar */}
      <div className="v-card" style={{padding:'var(--s4)',marginBottom:'var(--s5)',display:'flex',gap:'var(--s6)'}}>
        <div style={{textAlign:'center'}}>
          <div style={{fontSize:'28px',fontWeight:700,color: parseFloat(pct) >= 75 ? 'var(--success)' : parseFloat(pct) >= 60 ? 'var(--warning)' : 'var(--danger)' }}>{pct}%</div>
          <div style={{fontSize:'11px',color:'var(--text-muted)'}}>Attendance Rate</div>
        </div>
        <div style={{textAlign:'center'}}>
          <div style={{fontSize:'28px',fontWeight:700,color:'var(--success)'}}>{present}</div>
          <div style={{fontSize:'11px',color:'var(--text-muted)'}}>Present</div>
        </div>
        <div style={{textAlign:'center'}}>
          <div style={{fontSize:'28px',fontWeight:700,color:'var(--danger)'}}>{total - present}</div>
          <div style={{fontSize:'11px',color:'var(--text-muted)'}}>Absent</div>
        </div>
      </div>

      {/* Daily log */}
      <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>Daily Log</h4>
      <div className="v-table-container">
        <table className="v-table">
          <thead><tr><th>Date</th><th>Status</th><th>Confidence</th></tr></thead>
          <tbody>
            {records.length === 0 ? (
              <tr><td colSpan="3" style={{textAlign:'center',color:'var(--text-muted)'}}>No attendance records</td></tr>
            ) : records.map((r, i) => (
              <tr key={i}>
                <td>{r.date}</td>
                <td><span className={`v-badge v-badge-${r.status === 'present' ? 'low' : 'high'}`}>{r.status}</span></td>
                <td style={{color:'var(--text-muted)'}}>{r.confidence ? `${(r.confidence * 100).toFixed(0)}%` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StudentAttendancePage;
