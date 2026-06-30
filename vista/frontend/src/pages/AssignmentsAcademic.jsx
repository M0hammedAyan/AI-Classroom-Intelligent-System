import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function AssignmentsAcademic({ auth }) {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [maxMarks, setMaxMarks] = useState('');
  const [subjectId, setSubjectId] = useState('sub-dsa');
  const [classSectionId, setClassSectionId] = useState('class-aiml-4a');

  const headers = { Authorization: `Bearer ${auth.token}`, 'Content-Type': 'application/json' };
  const canCreate = ['admin', 'teacher', 'hop'].includes(auth.role);

  useEffect(() => { loadAssignments(); }, []);

  async function loadAssignments() {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/assignments`, { headers });
      if (res.ok) {
        const data = await res.json();
        setAssignments(data.assignments || []);
      }
    } catch {}
    setLoading(false);
  }

  async function handleCreate(e) {
    e.preventDefault();
    try {
      const res = await fetch(`${BASE_URL}/assignments`, {
        method: 'POST', headers,
        body: JSON.stringify({
          subject_id: subjectId, class_section_id: classSectionId,
          title, description, max_marks: maxMarks ? parseFloat(maxMarks) : null, due_date: dueDate,
        }),
      });
      if (res.ok) {
        setTitle(''); setDescription(''); setDueDate(''); setShowForm(false);
        loadAssignments();
      }
    } catch {}
  }

  async function handleSubmit(assignmentId) {
    try {
      const res = await fetch(`${BASE_URL}/assignments/${assignmentId}/submit`, {
        method: 'POST', headers,
        body: JSON.stringify({ notes: 'Submitted via portal' }),
      });
      if (res.ok) alert('Submitted!');
      else {
        const data = await res.json();
        alert(data.detail || 'Failed');
      }
    } catch {}
  }

  function isOverdue(dueDate) {
    return new Date(dueDate) < new Date();
  }

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Assignments</h2>
          <p className="v-page-subtitle">{assignments.length} total</p>
        </div>
        {canCreate && (
          <button className="v-btn v-btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ New Assignment'}
          </button>
        )}
      </div>

      {showForm && (
        <form className="v-card" style={{marginBottom:'var(--s5)',maxWidth:'500px'}} onSubmit={handleCreate}>
          <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
            <input className="v-input" placeholder="Assignment title" value={title} onChange={e => setTitle(e.target.value)} required />
            <textarea className="v-input" placeholder="Description (optional)" value={description} onChange={e => setDescription(e.target.value)} rows={3} style={{resize:'vertical'}} />
            <div style={{display:'flex',gap:'var(--s3)'}}>
              <input className="v-input" type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} required style={{flex:1}} />
              <input className="v-input" type="number" placeholder="Max marks" value={maxMarks} onChange={e => setMaxMarks(e.target.value)} style={{width:'100px'}} />
            </div>
            <button className="v-btn v-btn-primary" style={{alignSelf:'flex-start'}}>Create</button>
          </div>
        </form>
      )}

      <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
        {assignments.length === 0 ? (
          <div className="v-empty">No assignments</div>
        ) : assignments.map(a => (
          <div key={a.id} className="v-card" style={{padding:'var(--s4)',borderLeft:`3px solid ${isOverdue(a.due_date) ? 'var(--danger)' : 'var(--primary)'}`}}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
              <div>
                <h4 style={{fontSize:'14px',fontWeight:600}}>{a.title}</h4>
                <p style={{fontSize:'12px',color:'var(--text-muted)',marginTop:'2px'}}>
                  {a.subject_code} · Due: {a.due_date} · Max: {a.max_marks || '—'} marks
                </p>
                {a.description && <p style={{fontSize:'12px',color:'var(--text-secondary)',marginTop:'var(--s2)'}}>{a.description}</p>}
              </div>
              <div style={{textAlign:'right'}}>
                {canCreate && <span style={{fontSize:'11px',color:'var(--text-muted)'}}>{a.submissions_count} submissions</span>}
                {auth.role === 'student' && !isOverdue(a.due_date) && (
                  <button className="v-btn v-btn-secondary" style={{fontSize:'11px',padding:'4px 10px'}} onClick={() => handleSubmit(a.id)}>Submit</button>
                )}
                {isOverdue(a.due_date) && <span className="v-badge v-badge-high" style={{fontSize:'10px'}}>Overdue</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AssignmentsAcademic;
