import { useState } from 'react';

const BASE_URL = '/api/v1';

function TeacherAttendance({ auth }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [date] = useState(() => new Date().toISOString().split('T')[0]);
  const [classroomId, setClassroomId] = useState('CSE-3A');

  const headers = { Authorization: `Bearer ${auth.token}` };

  function handleFile(e) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setResults(null);
    setError('');
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result);
    reader.readAsDataURL(f);
  }

  async function handleMark() {
    if (!file) return;
    setLoading(true);
    setError('');
    setResults(null);

    const base64 = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.readAsDataURL(file);
    });

    try {
      const res = await fetch(`${BASE_URL}/attendance/mark-batch`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64, classroom_id: classroomId, session_date: date }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Recognition failed');
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Mark Attendance</h2>
          <p className="v-page-subtitle">Upload a classroom photo — AI identifies all students</p>
        </div>
        <span style={{fontSize:'13px',color:'var(--text-muted)'}}>Date: {date}</span>
      </div>

      {/* Class Selector */}
      <div style={{marginBottom:'var(--s4)',display:'flex',gap:'var(--s3)',alignItems:'center'}}>
        <label className="v-label" style={{marginBottom:0}}>Class:</label>
        <select className="v-select" style={{width:'200px'}} value={classroomId} onChange={e => setClassroomId(e.target.value)}>
          <option value="CSE-3A">CSE-3A</option>
          <option value="AIML-4A">AIML-4A</option>
          <option value="AIML-3A">AIML-3A</option>
          <option value="CSE-2B">CSE-2B</option>
          <option value="ISE-3A">ISE-3A</option>
        </select>
      </div>

      {/* Upload Area */}
      <div className="v-card" style={{marginBottom:'var(--s6)'}}>
        <div style={{display:'flex',gap:'var(--s4)',alignItems:'flex-start'}}>
          <div style={{flex:1}}>
            <label className="v-label">Classroom Photo</label>
            <div style={{border:'2px dashed var(--border)',borderRadius:'var(--r-md)',padding:'var(--s6)',textAlign:'center',cursor:'pointer',position:'relative'}}>
              <input type="file" accept="image/*" onChange={handleFile} style={{position:'absolute',inset:0,opacity:0,cursor:'pointer'}} />
              {preview ? (
                <img src={preview} alt="Preview" style={{maxHeight:'200px',borderRadius:'var(--r-sm)'}} />
              ) : (
                <div>
                  <p style={{fontSize:'13px',color:'var(--text-muted)'}}>📸 Click or drop a classroom image here</p>
                  <p style={{fontSize:'11px',color:'var(--text-muted)',marginTop:'var(--s1)'}}>JPEG or PNG, max 5MB</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div style={{marginTop:'var(--s4)',display:'flex',gap:'var(--s3)'}}>
          <button className="v-btn v-btn-primary" onClick={handleMark} disabled={!file || loading}>
            {loading ? '⏳ Processing...' : '✅ Mark Attendance'}
          </button>
          {file && <button className="v-btn v-btn-secondary" onClick={() => {setFile(null);setPreview(null);setResults(null);}}>Clear</button>}
        </div>
      </div>

      {error && <div className="v-card" style={{borderLeft:'3px solid var(--danger)',marginBottom:'var(--s4)',padding:'var(--s3) var(--s4)',fontSize:'13px',color:'var(--danger)'}}>{error}</div>}

      {/* Results */}
      {results && (
        <div className="v-section">
          <div className="v-kpi-grid" style={{marginBottom:'var(--s4)'}}>
            <div className="v-kpi">
              <div className="v-kpi-label">Faces Detected</div>
              <div className="v-kpi-value">{results.faces_detected}</div>
            </div>
            <div className="v-kpi">
              <div className="v-kpi-label">Students Marked</div>
              <div className="v-kpi-value success">{results.results?.filter(r => r.status === 'present').length || 0}</div>
            </div>
            <div className="v-kpi">
              <div className="v-kpi-label">Unrecognized</div>
              <div className="v-kpi-value warning">{results.results?.filter(r => r.status === 'unrecognized').length || 0}</div>
            </div>
          </div>

          <div className="v-table-container">
            <div className="v-table-header">
              <span className="v-table-title">Recognition Results</span>
            </div>
            <table className="v-table">
              <thead><tr><th>Student</th><th>Status</th><th>Confidence</th></tr></thead>
              <tbody>
                {(results.results || []).map((r, i) => (
                  <tr key={i}>
                    <td style={{fontWeight:500}}>{r.student_name || r.student_id || 'Unknown'}</td>
                    <td><span className={`v-badge v-badge-${r.status === 'present' ? 'low' : r.status === 'unrecognized' ? 'medium' : 'high'}`}>{r.status}</span></td>
                    <td>{r.confidence ? `${(r.confidence * 100).toFixed(1)}%` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default TeacherAttendance;
