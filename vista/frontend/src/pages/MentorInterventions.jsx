import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function MentorInterventions({ auth }) {
  const [interventions, setInterventions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ student_id: '', type: 'counselling', notes: '' });
  const [saving, setSaving] = useState(false);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    const [iRes, sRes] = await Promise.all([
      fetch(`${BASE_URL}/mentor/interventions`, { headers }).then(r => r.ok ? r.json() : { interventions: [] }),
      fetch(`${BASE_URL}/mentor/students`, { headers }).then(r => r.ok ? r.json() : { students: [] }),
    ]);
    setInterventions(iRes.interventions || []);
    setStudents(sRes.students || []);
    setLoading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.student_id) return;
    setSaving(true);
    try {
      await fetch(`${BASE_URL}/mentor/interventions`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setShowForm(false);
      setForm({ student_id: '', type: 'counselling', notes: '' });
      loadData();
    } catch {}
    setSaving(false);
  }

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Interventions</h2>
          <p className="v-page-subtitle">Track actions taken for at-risk students</p>
        </div>
        <button className="v-btn v-btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Log Intervention'}
        </button>
      </div>

      {/* New Intervention Form */}
      {showForm && (
        <div className="v-card" style={{marginBottom:'var(--s5)'}}>
          <form onSubmit={handleSubmit} style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s4)'}}>
            <div>
              <label className="v-label">Student</label>
              <select className="v-select" value={form.student_id} onChange={e => setForm({...form, student_id: e.target.value})} required>
                <option value="">Select student...</option>
                {students.map(s => <option key={s.student_id} value={s.student_id}>{s.name} ({s.student_id})</option>)}
              </select>
            </div>
            <div>
              <label className="v-label">Type</label>
              <select className="v-select" value={form.type} onChange={e => setForm({...form, type: e.target.value})}>
                <option value="counselling">Counselling</option>
                <option value="call">Phone Call</option>
                <option value="meeting">Meeting</option>
                <option value="referral">Referral</option>
                <option value="email">Email</option>
              </select>
            </div>
            <div style={{gridColumn:'1/-1'}}>
              <label className="v-label">Notes</label>
              <textarea className="v-input" rows="3" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} placeholder="What was discussed or observed..." style={{resize:'vertical'}} />
            </div>
            <div>
              <button className="v-btn v-btn-primary" type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save Intervention'}</button>
            </div>
          </form>
        </div>
      )}

      {/* Interventions List */}
      {interventions.length === 0 ? (
        <div className="v-empty">No interventions logged yet. Click "+ Log Intervention" to start tracking.</div>
      ) : (
        <div className="v-table-container">
          <table className="v-table">
            <thead><tr><th>Student</th><th>Type</th><th>Notes</th><th>Outcome</th><th>Date</th></tr></thead>
            <tbody>
              {interventions.map(i => (
                <tr key={i.id}>
                  <td style={{fontWeight:500}}>{i.student_id}</td>
                  <td><span className="v-badge v-badge-info">{i.type}</span></td>
                  <td style={{fontSize:'12px',color:'var(--text-secondary)',maxWidth:'300px',overflow:'hidden',textOverflow:'ellipsis'}}>{i.notes || '—'}</td>
                  <td><span className={`v-badge v-badge-${i.outcome === 'improved' ? 'low' : i.outcome === 'pending' ? 'medium' : 'info'}`}>{i.outcome}</span></td>
                  <td style={{fontSize:'12px',color:'var(--text-muted)'}}>{i.created_at?.split('T')[0]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default MentorInterventions;
