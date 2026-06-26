import { useState } from 'react';

const BASE_URL = '/api/v1';

function TestRecognition({ auth }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const headers = { Authorization: `Bearer ${auth.token}` };

  async function handleTest() {
    if (!file) return;
    setLoading(true); setError(''); setResult(null);

    const base64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

    try {
      const today = new Date().toISOString().split('T')[0];
      const res = await fetch(`${BASE_URL}/attendance/mark`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64, classroom_id: 'CSE-3A', session_date: today }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Recognition failed');
      setResult(data);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div>
      <div className="v-page-header">
        <h2 className="v-page-title">Test Face Recognition</h2>
      </div>

      <div className="v-card" style={{ maxWidth: '500px' }}>
        <div style={{ marginBottom: '12px' }}>
          <label className="v-label">Upload a face photo</label>
          <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} style={{ fontSize: '13px' }} />
        </div>
        <button className="v-btn v-btn-primary" onClick={handleTest} disabled={!file || loading}>
          {loading ? 'Processing...' : 'Run Recognition'}
        </button>

        {error && <p style={{ color: 'var(--red)', fontSize: '13px', marginTop: '12px' }}>{error}</p>}

        {result && (
          <div style={{ marginTop: '16px', padding: '12px', border: '1px solid var(--border)', borderRadius: '6px' }}>
            <p style={{ fontWeight: 500, marginBottom: '8px' }}>Result:</p>
            <table style={{ width: '100%', fontSize: '13px' }}>
              <tbody>
                <tr><td style={{ color: 'var(--text-muted)' }}>Student</td><td style={{ fontWeight: 500 }}>{result.student_name || result.student_id || 'Unknown'}</td></tr>
                <tr><td style={{ color: 'var(--text-muted)' }}>Status</td><td><span className={`v-badge ${result.status === 'present' ? 'v-badge-low' : 'v-badge-medium'}`}>{result.status}</span></td></tr>
                <tr><td style={{ color: 'var(--text-muted)' }}>Confidence</td><td>{result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : '—'}</td></tr>
                <tr><td style={{ color: 'var(--text-muted)' }}>Liveness</td><td>{result.liveness_passed ? '✓ Passed' : '✗ Failed'}</td></tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default TestRecognition;
