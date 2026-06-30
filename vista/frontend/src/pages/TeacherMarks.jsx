import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function TeacherMarks({ auth }) {
  const [students, setStudents] = useState([]);
  const [subject, setSubject] = useState('Data Structures and Algorithms');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [maxScore, setMaxScore] = useState('100');
  const [marks, setMarks] = useState({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => {
    fetch(`${BASE_URL}/students`, { headers })
      .then(r => r.ok ? r.json() : { students: [] })
      .then(d => setStudents(d.students || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function handleMarkChange(studentId, value) {
    setMarks(prev => ({ ...prev, [studentId]: value }));
    setSaved(false);
  }

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    let count = 0;

    for (const [studentId, score] of Object.entries(marks)) {
      if (!score || score === '') continue;
      try {
        await fetch(`${BASE_URL}/lms/add-score`, {
          method: 'POST',
          headers: { ...headers, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_id: studentId,
            subject: subject,
            score: parseFloat(score),
            max_score: parseFloat(maxScore),
            date: date,
          }),
        });
        count++;
      } catch {}
    }

    setSaving(false);
    setSaved(true);
    setMarks({});
    alert(`Saved ${count} scores successfully.`);
  }

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Enter Marks</h2>
          <p className="v-page-subtitle">Record assessment scores for your students</p>
        </div>
      </div>

      {/* Config */}
      <div className="v-card" style={{marginBottom:'var(--s5)',display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:'var(--s4)'}}>
        <div>
          <label className="v-label">Subject</label>
          <input className="v-input" value={subject} onChange={e => setSubject(e.target.value)} />
        </div>
        <div>
          <label className="v-label">Max Score</label>
          <input className="v-input" type="number" value={maxScore} onChange={e => setMaxScore(e.target.value)} />
        </div>
        <div>
          <label className="v-label">Date</label>
          <input className="v-input" type="date" value={date} onChange={e => setDate(e.target.value)} />
        </div>
      </div>

      {/* Marks Table */}
      <div className="v-table-container">
        <div className="v-table-header">
          <span className="v-table-title">Student Scores</span>
          <button className="v-btn v-btn-primary" onClick={handleSave} disabled={saving || Object.keys(marks).length === 0}>
            {saving ? 'Saving...' : `Save ${Object.keys(marks).filter(k => marks[k]).length} Scores`}
          </button>
        </div>
        <table className="v-table">
          <thead><tr><th>ID</th><th>Name</th><th>Class</th><th>Score (/{maxScore})</th></tr></thead>
          <tbody>
            {students.map(s => (
              <tr key={s.student_id}>
                <td style={{fontFamily:'var(--mono)',fontSize:'12px'}}>{s.student_id}</td>
                <td style={{fontWeight:500}}>{s.name}</td>
                <td>{s.class}</td>
                <td>
                  <input
                    className="v-input"
                    type="number"
                    min="0"
                    max={maxScore}
                    step="0.5"
                    placeholder="—"
                    value={marks[s.student_id] || ''}
                    onChange={e => handleMarkChange(s.student_id, e.target.value)}
                    style={{width:'100px',padding:'4px 8px'}}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TeacherMarks;
