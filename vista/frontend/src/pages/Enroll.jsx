import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function EnrollPage({ auth }) {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
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
    </div>
  );
}

export default EnrollPage;
