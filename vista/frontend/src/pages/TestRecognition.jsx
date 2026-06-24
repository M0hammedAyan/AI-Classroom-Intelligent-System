import { useState } from 'react';
import './TestRecognition.css';

const BASE_URL = '/api/v1';

function TestRecognition({ auth }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('single'); // 'single' or 'batch'

  function handleFileChange(e) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setResult(null);
    setError('');
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result);
    reader.readAsDataURL(f);
  }

  async function handleTest() {
    if (!file) { setError('Select an image first'); return; }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const reader = new FileReader();
      const base64 = await new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
      const today = new Date().toISOString().split('T')[0];

      const endpoint = mode === 'batch' ? '/attendance/mark-batch' : '/attendance/mark';
      const res = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          image: base64,
          classroom_id: 'CSE-3A',
          session_date: today,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail?.message || data.detail?.code || 'Recognition failed');
        return;
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="test-page">
      <h2>Test Face Recognition</h2>
      <p className="test-desc">
        Upload a photo to test if the system can identify the person.
        The image will be processed through the full pipeline: detection → embedding → matching → liveness.
      </p>

      <div className="test-controls">
        <div className="mode-toggle">
          <button
            className={mode === 'single' ? 'active' : ''}
            onClick={() => setMode('single')}
          >
            Single Face
          </button>
          <button
            className={mode === 'batch' ? 'active' : ''}
            onClick={() => setMode('batch')}
          >
            Multi-Face (Batch)
          </button>
        </div>

        <div className="upload-area">
          <input
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileChange}
            id="test-image"
          />
          <label htmlFor="test-image" className="upload-label">
            {file ? file.name : 'Choose an image...'}
          </label>
        </div>

        <button
          className="test-btn"
          onClick={handleTest}
          disabled={loading || !file}
        >
          {loading ? 'Processing...' : 'Run Recognition'}
        </button>
      </div>

      {preview && (
        <div className="preview-section">
          <h3>Input Image</h3>
          <img src={preview} alt="Test input" className="preview-img" />
        </div>
      )}

      {error && <div className="error-msg" role="alert">{error}</div>}

      {result && mode === 'single' && (
        <div className={`result-card ${result.status}`}>
          <h3>Recognition Result</h3>
          <div className="result-grid">
            <div className="result-item">
              <span className="result-label">Status</span>
              <span className={`result-value status-${result.status}`}>
                {result.status === 'present' ? '✓ Recognized' :
                 result.status === 'unrecognized' ? '? Unrecognized' :
                 '✗ Liveness Failed'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Student</span>
              <span className="result-value">
                {result.student_name || result.student_id || 'None'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Confidence</span>
              <span className="result-value">
                {result.confidence != null ? `${(result.confidence * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Liveness</span>
              <span className="result-value">
                {result.liveness_passed ? '✓ Passed' : '✗ Failed'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Attendance ID</span>
              <span className="result-value">
                {result.attendance_id || 'Not recorded'}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Time</span>
              <span className="result-value">
                {result.marked_at ? new Date(result.marked_at).toLocaleTimeString() : '—'}
              </span>
            </div>
          </div>
        </div>
      )}

      {result && mode === 'batch' && (
        <div className="result-card batch">
          <h3>Batch Recognition Result</h3>
          <p className="batch-summary">
            Faces detected: <strong>{result.faces_detected}</strong>
          </p>
          {result.results && result.results.length > 0 ? (
            <div className="batch-results">
              {result.results.map((r, i) => (
                <div className={`batch-item ${r.status}`} key={i}>
                  <span className="batch-student">
                    {r.student_name || r.student_id || 'Unknown'}
                  </span>
                  <span className={`batch-status status-${r.status}`}>
                    {r.status}
                  </span>
                  <span className="batch-conf">
                    {r.confidence != null ? `${(r.confidence * 100).toFixed(0)}%` : '—'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p>No faces recognized.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default TestRecognition;
