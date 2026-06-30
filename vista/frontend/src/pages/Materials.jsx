import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function Materials({ auth }) {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [subjectId, setSubjectId] = useState('sub-dsa');
  const [file, setFile] = useState(null);

  const headers = { Authorization: `Bearer ${auth.token}` };
  const canUpload = ['admin', 'hos', 'hop', 'teacher'].includes(auth.role);

  useEffect(() => { loadMaterials(); }, []);

  async function loadMaterials() {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/materials`, { headers });
      if (res.ok) {
        const data = await res.json();
        setMaterials(data.materials || []);
      }
    } catch {}
    setLoading(false);
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const params = new URLSearchParams({ subject_id: subjectId, title });
      const res = await fetch(`${BASE_URL}/materials?${params}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.token}` },
        body: formData,
      });
      if (res.ok) {
        setTitle(''); setFile(null); setShowForm(false);
        loadMaterials();
      }
    } catch {}
    setUploading(false);
  }

  function formatSize(bytes) {
    if (!bytes) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }

  const typeIcons = { pdf: '📄', pptx: '📊', docx: '📝', xlsx: '📈', zip: '📦', jpg: '🖼️', png: '🖼️' };

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Study Materials</h2>
          <p className="v-page-subtitle">{materials.length} files available</p>
        </div>
        {canUpload && (
          <button className="v-btn v-btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '+ Upload Material'}
          </button>
        )}
      </div>

      {showForm && (
        <form className="v-card" style={{marginBottom:'var(--s5)',maxWidth:'500px'}} onSubmit={handleUpload}>
          <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
            <input className="v-input" placeholder="Title (e.g. Unit 3 Notes)" value={title} onChange={e => setTitle(e.target.value)} required />
            <select className="v-select" value={subjectId} onChange={e => setSubjectId(e.target.value)}>
              <option value="sub-dsa">Data Structures & Algorithms</option>
              <option value="sub-ml101">Machine Learning</option>
            </select>
            <input type="file" onChange={e => setFile(e.target.files[0])} required accept=".pdf,.pptx,.docx,.xlsx,.zip,.jpg,.png" />
            <button className="v-btn v-btn-primary" style={{alignSelf:'flex-start'}} disabled={uploading}>
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </form>
      )}

      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))',gap:'var(--s3)'}}>
        {materials.map(m => (
          <div key={m.id} className="v-card" style={{padding:'var(--s4)'}}>
            <div style={{display:'flex',gap:'var(--s3)',alignItems:'flex-start'}}>
              <span style={{fontSize:'24px'}}>{typeIcons[m.file_type] || '📁'}</span>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:'13px',fontWeight:600,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{m.title}</div>
                <div style={{fontSize:'11px',color:'var(--text-muted)'}}>{m.subject_code} · {formatSize(m.file_size)} · {m.file_type?.toUpperCase()}</div>
                <div style={{fontSize:'11px',color:'var(--text-muted)',marginTop:'2px'}}>by {m.uploaded_by} · {new Date(m.created_at).toLocaleDateString()}</div>
              </div>
            </div>
            <a
              href={`${BASE_URL}/materials/${m.id}/download`}
              style={{display:'inline-block',marginTop:'var(--s3)',fontSize:'12px',color:'var(--primary)',fontWeight:500}}
              onClick={e => { e.preventDefault(); window.open(`${BASE_URL}/materials/${m.id}/download`, '_blank'); }}
            >
              Download ↓
            </a>
          </div>
        ))}
        {materials.length === 0 && <div className="v-empty">No materials uploaded yet</div>}
      </div>
    </div>
  );
}

export default Materials;
