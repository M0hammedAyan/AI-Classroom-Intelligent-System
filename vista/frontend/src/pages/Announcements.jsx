import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function Announcements({ auth }) {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [priority, setPriority] = useState('normal');
  const [scope, setScope] = useState('all');

  const headers = { Authorization: `Bearer ${auth.token}`, 'Content-Type': 'application/json' };
  const canCreate = ['admin', 'hos', 'hop', 'teacher'].includes(auth.role);

  useEffect(() => { loadAnnouncements(); }, []);

  async function loadAnnouncements() {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/announcements`, { headers });
      if (res.ok) {
        const data = await res.json();
        setAnnouncements(data.announcements || []);
      }
    } catch {}
    setLoading(false);
  }

  async function handleCreate(e) {
    e.preventDefault();
    try {
      const res = await fetch(`${BASE_URL}/announcements`, {
        method: 'POST', headers,
        body: JSON.stringify({ title, content, priority, target_scope: scope }),
      });
      if (res.ok) {
        setTitle(''); setContent(''); setShowForm(false);
        loadAnnouncements();
      }
    } catch {}
  }

  const priorityStyles = {
    urgent: { borderLeft: '3px solid var(--danger)', background: 'var(--danger-light)' },
    important: { borderLeft: '3px solid var(--warning)', background: 'var(--warning-light)' },
    normal: { borderLeft: '3px solid var(--border)' },
  };

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Announcements</h2>
          <p className="v-page-subtitle">{announcements.length} notices</p>
        </div>
        {canCreate && (
          <button className="v-btn v-btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ New Announcement'}
          </button>
        )}
      </div>

      {showForm && (
        <form className="v-card" style={{marginBottom:'var(--s5)',maxWidth:'600px'}} onSubmit={handleCreate}>
          <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
            <input className="v-input" placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} required />
            <textarea className="v-input" placeholder="Content..." value={content} onChange={e => setContent(e.target.value)} rows={4} required style={{resize:'vertical'}} />
            <div style={{display:'flex',gap:'var(--s3)'}}>
              <select className="v-select" value={priority} onChange={e => setPriority(e.target.value)}>
                <option value="normal">Normal</option>
                <option value="important">Important</option>
                <option value="urgent">Urgent</option>
              </select>
              <select className="v-select" value={scope} onChange={e => setScope(e.target.value)}>
                <option value="all">All Users</option>
                <option value="dept:dept-aiml">AIML Department</option>
                <option value="class:AIML-4A">AIML 4A Only</option>
              </select>
            </div>
            <button className="v-btn v-btn-primary" style={{alignSelf:'flex-start'}}>Publish</button>
          </div>
        </form>
      )}

      <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
        {announcements.length === 0 ? (
          <div className="v-empty">No announcements</div>
        ) : announcements.map(a => (
          <div key={a.id} className="v-card" style={{...priorityStyles[a.priority], padding:'var(--s4)'}}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
              <h4 style={{fontSize:'14px',fontWeight:600}}>{a.title}</h4>
              {a.priority !== 'normal' && (
                <span className={`v-badge v-badge-${a.priority === 'urgent' ? 'high' : 'medium'}`} style={{fontSize:'10px'}}>
                  {a.priority}
                </span>
              )}
            </div>
            <p style={{fontSize:'13px',color:'var(--text-secondary)',marginTop:'var(--s2)',whiteSpace:'pre-wrap'}}>{a.content}</p>
            <div style={{fontSize:'11px',color:'var(--text-muted)',marginTop:'var(--s3)'}}>
              {a.author_name} · {new Date(a.created_at).toLocaleDateString()} · {a.target_scope}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Announcements;
