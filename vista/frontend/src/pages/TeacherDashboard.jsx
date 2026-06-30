import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function TeacherDashboard({ auth }) {
  const navigate = useNavigate();
  const [subjects, setSubjects] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/admin/teacher/my-subjects`, { headers }).then(r => r.ok ? r.json() : { subjects: [] }),
      fetch(`${BASE_URL}/assignments`, { headers }).then(r => r.ok ? r.json() : { assignments: [] }),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.ok ? r.json() : { flags: [] }),
    ]).then(([s, a, r]) => {
      setSubjects(s.subjects || []);
      setAssignments((a.assignments || []).slice(0, 5));
      setFlags(r.flags || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  const high = flags.filter(f => f.risk_level === 'high');
  const totalStudents = subjects.reduce((sum, s) => sum + s.student_count, 0);

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Teacher Dashboard</h2>
          <p className="v-page-subtitle">Welcome, {auth.name}</p>
        </div>
      </div>

      {/* KPIs */}
      <div className="v-kpi-grid" style={{gridTemplateColumns:'repeat(4,1fr)'}}>
        <div className="v-kpi" onClick={() => navigate('/students')}>
          <div className="v-kpi-label">My Students</div>
          <div className="v-kpi-value">{totalStudents}</div>
        </div>
        <div className="v-kpi">
          <div className="v-kpi-label">Subjects</div>
          <div className="v-kpi-value">{subjects.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/hw')}>
          <div className="v-kpi-label">Assignments</div>
          <div className="v-kpi-value">{assignments.length}</div>
        </div>
        <div className="v-kpi" onClick={() => navigate('/risk')}>
          <div className="v-kpi-label">At Risk</div>
          <div className="v-kpi-value danger">{high.length}</div>
        </div>
      </div>

      {/* My Subjects + Classes */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s4)',marginBottom:'var(--s5)'}}>
        <div className="v-card">
          <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>📚 My Subjects & Classes</h4>
          {subjects.length === 0 ? (
            <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No subjects assigned</p>
          ) : subjects.map((s, i) => (
            <div key={i} style={{padding:'var(--s2) 0',borderBottom: i < subjects.length - 1 ? '1px solid var(--border)' : 'none'}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <div>
                  <span style={{fontSize:'13px',fontWeight:600,color:'var(--primary)'}}>{s.subject_code}</span>
                  <span style={{fontSize:'12px',color:'var(--text-secondary)',marginLeft:'var(--s2)'}}>{s.subject_name}</span>
                </div>
                <span style={{fontSize:'11px',color:'var(--text-muted)'}}>{s.student_count} students</span>
              </div>
              <div style={{fontSize:'11px',color:'var(--text-muted)'}}>Class: {s.class_code}</div>
            </div>
          ))}
        </div>

        {/* At-risk students */}
        <div className="v-card">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'var(--s3)'}}>
            <h4 style={{fontSize:'13px',fontWeight:600}}>⚠️ Students at Risk</h4>
            <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => navigate('/risk')}>View All</button>
          </div>
          {high.length === 0 ? (
            <p style={{fontSize:'12px',color:'var(--success)'}}>No high-risk students in your classes</p>
          ) : high.slice(0, 5).map((f, i) => (
            <div key={i} style={{padding:'var(--s2) 0',borderBottom:'1px solid var(--border)',cursor:'pointer'}} onClick={() => navigate(`/student/${f.student_id}`)}>
              <div style={{display:'flex',justifyContent:'space-between'}}>
                <span style={{fontSize:'12px',fontWeight:500}}>{f.student_name}</span>
                <span className="v-badge v-badge-high" style={{fontSize:'10px'}}>HIGH</span>
              </div>
              <div style={{fontSize:'11px',color:'var(--text-muted)'}}>{f.reasons?.[0] || '—'}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="v-card">
        <h4 style={{fontSize:'13px',fontWeight:600,marginBottom:'var(--s3)'}}>Quick Actions</h4>
        <div style={{display:'flex',gap:'var(--s3)',flexWrap:'wrap'}}>
          <button className="v-btn v-btn-primary" onClick={() => navigate('/mark-attendance')}>📸 Mark Attendance</button>
          <button className="v-btn v-btn-secondary" onClick={() => navigate('/marks')}>📝 Enter Marks</button>
          <button className="v-btn v-btn-secondary" onClick={() => navigate('/hw')}>📋 Assignments</button>
          <button className="v-btn v-btn-secondary" onClick={() => navigate('/materials')}>📁 Upload Material</button>
        </div>
      </div>
    </div>
  );
}

export default TeacherDashboard;
