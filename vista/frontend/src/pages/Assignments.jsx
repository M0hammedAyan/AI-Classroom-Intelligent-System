import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function Assignments({ auth }) {
  const [students, setStudents] = useState([]);
  const [users, setUsers] = useState([]);
  const [tab, setTab] = useState('mentor');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // Mentor assignment form
  const [mentorId, setMentorId] = useState('');
  const [selectedStudents, setSelectedStudents] = useState([]);

  // Teacher assignment form
  const [teacherId, setTeacherId] = useState('');
  const [subjectName, setSubjectName] = useState('');
  const [classSection, setClassSection] = useState('');

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/students`, { headers }).then(r => r.ok ? r.json() : { students: [] }),
      fetch(`${BASE_URL}/admin/users`, { headers }).then(r => r.ok ? r.json() : { users: [] }),
    ]).then(([s, u]) => {
      setStudents(s.students || []);
      setUsers(u.users || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const mentors = users.filter(u => u.role === 'mentor');
  const teachers = users.filter(u => u.role === 'teacher');

  async function handleAssignMentor(e) {
    e.preventDefault();
    if (!mentorId || selectedStudents.length === 0) return;
    setMessage(null);
    try {
      const res = await fetch(`${BASE_URL}/admin/assign-mentor`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ mentor_id: mentorId, student_ids: selectedStudents }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ type: 'success', text: `Assigned ${data.assigned} students to mentor` });
        setSelectedStudents([]);
      } else {
        setMessage({ type: 'error', text: data.detail?.message || 'Failed' });
      }
    } catch {}
  }

  async function handleAssignTeacher(e) {
    e.preventDefault();
    if (!teacherId || !subjectName || !classSection) return;
    setMessage(null);
    try {
      // Create subject group via teacher endpoint
      const res = await fetch(`${BASE_URL}/admin/assign-teacher`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ teacher_id: teacherId, subject_id: subjectName, class_section_id: classSection }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ type: 'success', text: 'Teacher assigned to subject successfully' });
      } else {
        setMessage({ type: 'error', text: data.detail?.message || 'Failed' });
      }
    } catch {}
  }

  function toggleStudent(sid) {
    setSelectedStudents(prev => prev.includes(sid) ? prev.filter(s => s !== sid) : [...prev, sid]);
  }

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Manage Assignments</h2>
          <p className="v-page-subtitle">Assign mentors to students and teachers to subjects</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{display:'flex',gap:0,borderBottom:'1px solid var(--border)',marginBottom:'var(--s5)'}}>
        <button onClick={() => setTab('mentor')} style={{padding:'var(--s3) var(--s4)',fontSize:'13px',fontWeight:500,color:tab==='mentor'?'var(--primary)':'var(--text-muted)',borderBottom:tab==='mentor'?'2px solid var(--primary)':'2px solid transparent',background:'none'}}>Mentor → Students</button>
        <button onClick={() => setTab('teacher')} style={{padding:'var(--s3) var(--s4)',fontSize:'13px',fontWeight:500,color:tab==='teacher'?'var(--primary)':'var(--text-muted)',borderBottom:tab==='teacher'?'2px solid var(--primary)':'2px solid transparent',background:'none'}}>Teacher → Subject</button>
      </div>

      {message && (
        <div style={{marginBottom:'var(--s4)',padding:'var(--s3) var(--s4)',borderRadius:'var(--r-sm)',fontSize:'12px',color:message.type==='error'?'var(--danger)':'var(--success)',background:message.type==='error'?'var(--danger-light)':'var(--success-light)'}}>
          {message.text}
        </div>
      )}

      {/* Mentor Assignment */}
      {tab === 'mentor' && (
        <div className="v-card" style={{maxWidth:'600px'}}>
          <form onSubmit={handleAssignMentor}>
            <div style={{marginBottom:'var(--s4)'}}>
              <label className="v-label">Select Mentor</label>
              <select className="v-select" value={mentorId} onChange={e => setMentorId(e.target.value)} required>
                <option value="">Choose mentor...</option>
                {mentors.map(m => <option key={m.id} value={m.id}>{m.name} ({m.email})</option>)}
              </select>
            </div>
            <div style={{marginBottom:'var(--s4)'}}>
              <label className="v-label">Select Students ({selectedStudents.length} selected)</label>
              <div style={{maxHeight:'200px',overflow:'auto',border:'1px solid var(--border)',borderRadius:'var(--r-sm)',padding:'var(--s2)'}}>
                {students.map(s => (
                  <label key={s.student_id} style={{display:'flex',alignItems:'center',gap:'var(--s2)',padding:'4px var(--s2)',fontSize:'13px',cursor:'pointer'}}>
                    <input type="checkbox" checked={selectedStudents.includes(s.student_id)} onChange={() => toggleStudent(s.student_id)} />
                    <span style={{fontWeight:500}}>{s.name}</span>
                    <span style={{color:'var(--text-muted)',fontSize:'11px'}}>{s.student_id}</span>
                  </label>
                ))}
              </div>
            </div>
            <button className="v-btn v-btn-primary" type="submit">Assign Students to Mentor</button>
          </form>
        </div>
      )}

      {/* Teacher Assignment */}
      {tab === 'teacher' && (
        <div className="v-card" style={{maxWidth:'600px'}}>
          <form onSubmit={handleAssignTeacher}>
            <div style={{marginBottom:'var(--s4)'}}>
              <label className="v-label">Select Teacher</label>
              <select className="v-select" value={teacherId} onChange={e => setTeacherId(e.target.value)} required>
                <option value="">Choose teacher...</option>
                {teachers.map(t => <option key={t.id} value={t.id}>{t.name} ({t.email})</option>)}
              </select>
            </div>
            <div style={{marginBottom:'var(--s4)'}}>
              <label className="v-label">Subject ID</label>
              <input className="v-input" value={subjectName} onChange={e => setSubjectName(e.target.value)} placeholder="e.g. sub-dsa" required />
            </div>
            <div style={{marginBottom:'var(--s4)'}}>
              <label className="v-label">Class Section ID</label>
              <input className="v-input" value={classSection} onChange={e => setClassSection(e.target.value)} placeholder="e.g. class-aiml-4a" required />
            </div>
            <button className="v-btn v-btn-primary" type="submit">Assign Teacher to Subject</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default Assignments;
