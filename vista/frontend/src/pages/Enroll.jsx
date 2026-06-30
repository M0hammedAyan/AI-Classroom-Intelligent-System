import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function EnrollPage({ auth }) {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [bulkResult, setBulkResult] = useState(null);
  const [error, setError] = useState('');

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => {
    fetch(`${BASE_URL}/students`, { headers })
      .then(r => r.json())
      .then(data => setStudents(data.students || []))
      .catch(() => {});
  }, []);

  async function handleEnroll(e) {
    e.preventDefault();
    if (!selectedStudent) { setError('Select a student'); return; }
    if (files.length === 0) { setError('Upload at least 1 image'); return; }

    setLoading(true); setError(''); setResult(null);

    const images = await Promise.all(
      Array.from(files).map(file => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      }))
    );

    try {
      const res = await fetch(`${BASE_URL}/students/${selectedStudent}/enroll`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ images }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Enrollment failed');
      setResult(data);
      setFiles([]);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  async function handleBulkEnroll(e) {
    const selectedFiles = e.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;
    setBulkResult(null);
    const formData = new FormData();
    for (let i = 0; i < selectedFiles.length; i++) {
      formData.append('files', selectedFiles[i]);
    }
    try {
      const res = await fetch(`${BASE_URL}/students/bulk-enroll`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.token}` },
        body: formData,
      });
      const data = await res.json();
      if (res.ok) setBulkResult(data);
      else alert(data.detail?.message || 'Bulk enrollment failed');
    } catch {}
    e.target.value = '';
  }

  return (
    <div>
      <div className="v-page-header">
        <h2 className="v-page-title">Face Enrollment</h2>
      </div>

      <div className="v-card" style={{ maxWidth: '500px' }}>
        <form onSubmit={handleEnroll}>
          <div style={{ marginBottom: '12px' }}>
            <label className="v-label">Student</label>
            <select className="v-select" value={selectedStudent} onChange={e => setSelectedStudent(e.target.value)}>
              <option value="">Select student...</option>
              {students.map(s => <option key={s.student_id} value={s.student_id}>{s.student_id} — {s.name}</option>)}
            </select>
          </div>
          <div style={{ marginBottom: '12px' }}>
            <label className="v-label">Face Photos (3-5 images)</label>
            <input type="file" accept="image/*" multiple onChange={e => setFiles(e.target.files)} style={{ fontSize: '13px' }} />
          </div>
          {error && <p style={{ color: 'var(--red)', fontSize: '13px', marginBottom: '12px' }}>{error}</p>}
          <button className="v-btn v-btn-primary" disabled={loading}>{loading ? 'Enrolling...' : 'Enroll Face'}</button>
        </form>

        {result && (
          <div style={{ marginTop: '16px', padding: '12px', background: 'var(--green-bg)', borderRadius: '6px' }}>
            <p style={{ fontWeight: 500, color: 'var(--green)' }}>✓ Enrolled successfully</p>
            <p style={{ fontSize: '12px' }}>Processed: {result.images_processed} · Quality: {result.embedding_quality}</p>
          </div>
        )}
      </div>

      {/* Bulk Enrollment */}
      <div className="v-card" style={{maxWidth:'500px',marginTop:'var(--s5)'}}>
        <h4 style={{fontSize:'14px',fontWeight:600,marginBottom:'var(--s3)'}}>Bulk Enrollment</h4>
        <p style={{fontSize:'12px',color:'var(--text-muted)',marginBottom:'var(--s3)'}}>
          Upload multiple images. Name files as: <code style={{background:'var(--bg-secondary)',padding:'2px 4px',borderRadius:'3px',fontSize:'11px'}}>STUDENTID_1.jpg</code>, <code style={{background:'var(--bg-secondary)',padding:'2px 4px',borderRadius:'3px',fontSize:'11px'}}>STUDENTID_2.jpg</code>
        </p>
        <input type="file" accept="image/*" multiple onChange={handleBulkEnroll} style={{fontSize:'13px'}} />
        {bulkResult && (
          <div style={{marginTop:'var(--s3)',fontSize:'12px'}}>
            <p style={{color:'var(--success)'}}>Enrolled: {bulkResult.enrolled} / {bulkResult.total_students} students</p>
            {bulkResult.failed > 0 && <p style={{color:'var(--danger)'}}>Failed: {bulkResult.failed}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default EnrollPage;
