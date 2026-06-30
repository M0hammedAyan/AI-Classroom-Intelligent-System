import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function StudentDashboard({ auth }) {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [timetable, setTimetable] = useState({});
  const [assignments, setAssignments] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const today = days[new Date().getDay() - 1] || 'Monday';

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/student-portal/dashboard`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${BASE_URL}/timetable/class-aiml-4a`, { headers }).then(r => r.ok ? r.json() : { timetable: {} }),
      fetch(`${BASE_URL}/assignments`, { headers }).then(r => r.ok ? r.json() : { assignments: [] }),
      fetch(`${BASE_URL}/announcements?page_size=3`, { headers }).then(r => r.ok ? r.json() : { announcements: [] }),
      fetch(`${BASE_URL}/student-portal/attendance`, { headers }).then(r => r.ok ? r.json() : { records: [] }),
    ]).then(([d, t, a, ann, att]) => {
      setData(d);
      setTimetable(t.timetable || {});
      setAssignments((a.assignments || []).slice(0, 3));
      setAnnouncements(ann.announcements || []);
      setAttendance((att.records || []).slice(0, 14));
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading your dashboard...</div>;
  if (!data) return <div className="v-empty">Unable to load dashboard</div>;

  const todayClasses = timetable[today] || [];

  return (
    <div>
      {/* Header */}
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 17 ? 'afternoon' : 'evening'}, {data.name.split(' ')[0]}</h2>
          <p className="v-page-subtitle">{data.student_id} · {data.class} · {today}</p>
        </div>
        <span className={`v-badge v-badge-${data.risk_level}`} style={{fontSize:'12px',padding:'4px 12px'}}>
          {data.risk_level} risk
        </span>
      </div>

      {/* KPIs */}
      <div className="v-kpi-grid" style={{gridTemplateColumns:'repeat(3,1fr)'}}>
        <div className="v-kpi" onClick={() => navigate('/my-attendance')}>
          <div className="v-kpi-label">Attendance</div>
          <div className={`v-kpi-value ${data.attendance_pct >= 75 ? 'success' : data.attendance_pct >= 60 ? 'warning' : 'danger'}`}>{data.attendance_pct}%</div>
          <div className="v-kpi-change">{data.total_present}/{data.total_sessions} sessions</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/my-scores')}>
          <div className="v-kpi-label">Avg Score</div>
          <div className={`v-kpi-value ${data.avg_score >= 60 ? 'success' : data.avg_score >= 40 ? 'warning' : 'danger'}`}>{data.avg_score}%</div>
          <div className="v-kpi-change">{data.assessments} assessments</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/my-risk')}>
          <div className="v-kpi-label">Risk</div>
          <div className={`v-kpi-value ${data.risk_level === 'high' ? 'danger' : data.risk_level === 'medium' ? 'warning' : 'success'}`}>{data.risk_level.toUpperCase()}</div>
          <div className="v-kpi-change">{data.risk_confidence || '—'}</div>
        </div>
      </div>

      {/* Main grid: Today's Schedule + Attendance heatmap */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s4)',marginBottom:'var(--s5)'}}>
        {/* Today's Timetable */}
        <div className="v-card">
          <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>📅 Today's Schedule</h4>
          {todayClasses.length === 0 ? (
            <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No classes today (or weekend)</p>
          ) : (
            <div style={{display:'flex',flexDirection:'column',gap:'var(--s2)'}}>
              {todayClasses.map((slot, i) => (
                <div key={i} style={{
                  display:'flex',alignItems:'center',gap:'var(--s3)',
                  padding:'var(--s2) var(--s3)',borderRadius:'var(--r-sm)',
                  background:'var(--bg-secondary)',border:'1px solid var(--border)',
                }}>
                  <div style={{fontSize:'11px',fontWeight:600,color:'var(--text-muted)',minWidth:'80px'}}>
                    {slot.start_time}-{slot.end_time}
                  </div>
                  <div style={{flex:1}}>
                    <div style={{fontSize:'12px',fontWeight:600,color:'var(--primary)'}}>{slot.subject_code}</div>
                    <div style={{fontSize:'11px',color:'var(--text-muted)'}}>{slot.teacher_name} · {slot.room}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Attendance Heatmap (last 14 days) */}
        <div className="v-card">
          <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>📊 Last 14 Days</h4>
          <div style={{display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:'4px',marginBottom:'var(--s2)'}}>
            {attendance.map((a, i) => (
              <div key={i} style={{
                width:'100%',aspectRatio:'1',borderRadius:'4px',
                background: a.status === 'present' ? 'var(--success)' : a.status === 'absent' ? 'var(--danger)' : 'var(--bg-hover)',
                opacity: a.status === 'present' ? 0.8 : a.status === 'absent' ? 0.7 : 0.3,
              }} title={`${a.date}: ${a.status}`} />
            ))}
          </div>
          <div style={{display:'flex',gap:'var(--s3)',fontSize:'10px',color:'var(--text-muted)'}}>
            <span>🟢 Present</span><span>🔴 Absent</span>
          </div>
          {data.attendance_pct < 75 && (
            <p style={{fontSize:'11px',color:'var(--danger)',marginTop:'var(--s2)',fontWeight:500}}>
              ⚠ Below 75% — attendance shortage
            </p>
          )}
        </div>
      </div>

      {/* Announcements + Upcoming Assignments */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s4)',marginBottom:'var(--s5)'}}>
        {/* Upcoming Assignments */}
        <div className="v-card">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'var(--s3)'}}>
            <h4 style={{fontSize:'13px',fontWeight:600}}>📋 Assignments</h4>
            <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/hw')}>View All</button>
          </div>
          {assignments.length === 0 ? (
            <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No pending assignments</p>
          ) : assignments.map((a, i) => (
            <div key={i} style={{
              padding:'var(--s2) 0',borderBottom: i < assignments.length - 1 ? '1px solid var(--border)' : 'none',
            }}>
              <div style={{fontSize:'12px',fontWeight:500}}>{a.title}</div>
              <div style={{fontSize:'11px',color:'var(--text-muted)'}}>
                {a.subject_code} · Due: {a.due_date}
                {new Date(a.due_date) < new Date() && <span style={{color:'var(--danger)',marginLeft:'6px'}}>OVERDUE</span>}
              </div>
            </div>
          ))}
        </div>

        {/* Announcements */}
        <div className="v-card">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'var(--s3)'}}>
            <h4 style={{fontSize:'13px',fontWeight:600}}>📢 Notices</h4>
            <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/announcements')}>View All</button>
          </div>
          {announcements.length === 0 ? (
            <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No announcements</p>
          ) : announcements.map((a, i) => (
            <div key={i} style={{
              padding:'var(--s2) 0',borderBottom: i < announcements.length - 1 ? '1px solid var(--border)' : 'none',
            }}>
              <div style={{fontSize:'12px',fontWeight:600}}>{a.title}</div>
              <div style={{fontSize:'11px',color:'var(--text-muted)',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{a.content}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Reasons */}
      {data.risk_reasons && data.risk_reasons.length > 0 && (
        <div className="v-card" style={{borderLeft:'3px solid var(--warning)',background:'var(--warning-light)'}}>
          <strong style={{fontSize:'13px',color:'var(--warning)'}}>⚠ Areas to Improve</strong>
          <ul style={{paddingLeft:'20px',marginTop:'8px',fontSize:'12px',color:'var(--text-secondary)'}}>
            {data.risk_reasons.map((r, i) => <li key={i} style={{marginBottom:'3px'}}>{r}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default StudentDashboard;
