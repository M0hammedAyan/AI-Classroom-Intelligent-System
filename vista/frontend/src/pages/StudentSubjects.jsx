import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function StudentSubjects({ auth }) {
  const [subjects, setSubjects] = useState([]);
  const [classInfo, setClassInfo] = useState('');
  const [semester, setSemester] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadSubjects(); }, []);

  async function loadSubjects() {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/student-portal/subjects`, {
        headers: { Authorization: `Bearer ${auth.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setSubjects(data.subjects || []);
        setClassInfo(data.class || '');
        setSemester(data.semester || '');
      }
    } catch {}
    setLoading(false);
  }

  if (loading) return <div className="v-loading">Loading subjects...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">My Subjects</h2>
          <p className="v-page-subtitle">
            {classInfo} {semester && `· Semester ${semester}`} · {subjects.length} subjects
          </p>
        </div>
      </div>

      {subjects.length === 0 ? (
        <div className="v-empty">
          <p>No subjects assigned to your class yet.</p>
          <p style={{fontSize:'12px',color:'var(--text-muted)'}}>Subjects are added by your HOP/HOS.</p>
        </div>
      ) : (
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))',gap:'var(--s4)'}}>
          {subjects.map((s, i) => (
            <div key={i} className="v-card" style={{padding:'var(--s4)'}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:'var(--s2)'}}>
                <div>
                  <h4 style={{fontSize:'14px',fontWeight:700,color:'var(--primary)'}}>{s.subject_code}</h4>
                  <p style={{fontSize:'13px',fontWeight:500}}>{s.subject_name}</p>
                </div>
                {s.semester && (
                  <span className="v-badge" style={{fontSize:'10px',background:'var(--primary-light)',color:'var(--primary)'}}>
                    Sem {s.semester}
                  </span>
                )}
              </div>
              <div style={{marginTop:'var(--s3)',paddingTop:'var(--s3)',borderTop:'1px solid var(--border)'}}>
                <div style={{display:'flex',alignItems:'center',gap:'var(--s2)'}}>
                  <span style={{fontSize:'12px',color:'var(--text-muted)'}}>Faculty:</span>
                  <span style={{fontSize:'13px',fontWeight:500}}>{s.teacher_name}</span>
                </div>
                {s.teacher_email && (
                  <span style={{fontSize:'11px',color:'var(--text-muted)'}}>{s.teacher_email}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default StudentSubjects;
