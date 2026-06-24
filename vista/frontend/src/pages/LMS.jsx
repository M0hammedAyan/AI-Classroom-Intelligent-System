import { useState, useEffect } from 'react';
import { getStudents } from '../api/client';
import './LMS.css';

const BASE_URL = '/api/v1';

function LMS({ auth }) {
  const [tab, setTab] = useState('scores');
  const [students, setStudents] = useState([]);
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    getStudents().then((res) => setStudents(res.students)).catch(() => {});
    loadScores();
  }, []);

  async function loadScores() {
    try {
      const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
      const res = await fetch(`${BASE_URL}/lms/scores`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setScores(data.scores || []);
      }
    } catch {}
  }

  return (
    <div className="lms-page">
      <h2>LMS Portal</h2>
      <p className="lms-desc">
        Manage academic scores, import from CSV, or sync with Moodle.
      </p>

      <div className="lms-tabs">
        <button className={tab === 'scores' ? 'active' : ''} onClick={() => setTab('scores')}>
          View Scores
        </button>
        <button className={tab === 'add' ? 'active' : ''} onClick={() => setTab('add')}>
          Add Score
        </button>
        <button className={tab === 'import' ? 'active' : ''} onClick={() => setTab('import')}>
          Import CSV
        </button>
        <button className={tab === 'moodle' ? 'active' : ''} onClick={() => setTab('moodle')}>
          Moodle Sync
        </button>
      </div>

      {message && (
        <div className={`lms-message ${message.type}`}>
          {message.text}
          <button onClick={() => setMessage(null)}>×</button>
        </div>
      )}

      {tab === 'scores' && <ScoresView scores={scores} loading={loading} />}
      {tab === 'add' && <AddScore students={students} onSuccess={() => { loadScores(); setMessage({ type: 'success', text: 'Score added successfully' }); }} />}
      {tab === 'import' && <ImportCSV onSuccess={(count) => { loadScores(); setMessage({ type: 'success', text: `Imported ${count} scores` }); }} />}
      {tab === 'moodle' && <MoodleSync onMessage={setMessage} />}
    </div>
  );
}

function ScoresView({ scores }) {
  const [filter, setFilter] = useState('');

  const filtered = scores.filter((s) =>
    !filter || s.student_id.includes(filter) || (s.subject || '').toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="lms-section">
      <div className="lms-toolbar">
        <input
          type="text"
          placeholder="Filter by student ID or subject..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="lms-filter"
        />
        <span className="lms-count">{filtered.length} records</span>
      </div>

      {filtered.length === 0 ? (
        <p className="lms-empty">No scores found. Add scores manually or import a CSV.</p>
      ) : (
        <div className="lms-table-wrap">
          <table className="lms-table">
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Subject</th>
                <th>Score</th>
                <th>Max</th>
                <th>Percentage</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 50).map((s, i) => {
                const pct = s.max_score > 0 ? ((s.score / s.max_score) * 100).toFixed(0) : '—';
                return (
                  <tr key={i}>
                    <td>{s.student_id}</td>
                    <td>{s.subject}</td>
                    <td>{s.score}</td>
                    <td>{s.max_score}</td>
                    <td>
                      <span className={`pct-badge ${pct >= 60 ? 'good' : pct >= 40 ? 'warn' : 'bad'}`}>
                        {pct}%
                      </span>
                    </td>
                    <td>{s.date}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AddScore({ students, onSuccess }) {
  const [form, setForm] = useState({
    student_id: '',
    subject: '',
    score: '',
    max_score: '100',
    date: new Date().toISOString().split('T')[0],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
      const res = await fetch(`${BASE_URL}/lms/add-score`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          student_id: form.student_id,
          subject: form.subject,
          score: parseFloat(form.score),
          max_score: parseFloat(form.max_score),
          date: form.date,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail?.message || 'Failed to add score');
      }

      setForm({ ...form, score: '', subject: '' });
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="lms-section">
      <form onSubmit={handleSubmit} className="lms-form">
        <div className="form-row">
          <div className="form-group">
            <label>Student</label>
            <select value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })} required>
              <option value="">Select student...</option>
              {students.map((s) => (
                <option key={s.student_id} value={s.student_id}>{s.student_id} — {s.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Subject</label>
            <input type="text" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} placeholder="e.g., Data Structures" required />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Score</label>
            <input type="number" value={form.score} onChange={(e) => setForm({ ...form, score: e.target.value })} min="0" step="0.5" required />
          </div>
          <div className="form-group">
            <label>Max Score</label>
            <input type="number" value={form.max_score} onChange={(e) => setForm({ ...form, max_score: e.target.value })} min="1" required />
          </div>
          <div className="form-group">
            <label>Date</label>
            <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
          </div>
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button type="submit" className="lms-btn" disabled={loading}>
          {loading ? 'Adding...' : 'Add Score'}
        </button>
      </form>
    </div>
  );
}

function ImportCSV({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  async function handleImport() {
    if (!file) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${BASE_URL}/lms/import-csv`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Import failed');

      setResult(data);
      onSuccess(data.imported);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="lms-section">
      <div className="csv-info">
        <h4>CSV Format Required</h4>
        <code>student_id,subject,score,max_score,date</code>
        <p>Example:</p>
        <pre>
{`student_id,subject,score,max_score,date
CS22B001,Data Structures,78,100,2026-06-15
CS22B002,Data Structures,62,100,2026-06-15
CS22B003,Data Structures,45,100,2026-06-15`}
        </pre>
      </div>

      <div className="import-controls">
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button className="lms-btn" onClick={handleImport} disabled={!file || loading}>
          {loading ? 'Importing...' : 'Import CSV'}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {result && (
        <div className="import-result">
          <p>✓ Imported: <strong>{result.imported}</strong> scores</p>
          {result.errors > 0 && <p>✗ Errors: {result.errors}</p>}
          {result.error_details && result.error_details.length > 0 && (
            <ul className="error-list">
              {result.error_details.map((e, i) => (
                <li key={i}>Row {e.row}: {e.error}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function MoodleSync({ onMessage }) {
  const [loading, setLoading] = useState(false);

  async function handleSync() {
    setLoading(true);
    try {
      const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
      const res = await fetch(`${BASE_URL}/lms/sync-moodle`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Sync failed');

      onMessage({ type: 'success', text: `Synced ${data.imported} grades from Moodle` });
    } catch (err) {
      onMessage({ type: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="lms-section">
      <div className="moodle-info">
        <h4>Moodle LMS Integration</h4>
        <p>
          Sync grades directly from your Moodle instance. Requires server-side configuration:
        </p>
        <ul>
          <li><code>MOODLE_URL</code> — Your Moodle base URL</li>
          <li><code>MOODLE_TOKEN</code> — Web service API token</li>
          <li><code>MOODLE_COURSE_ID</code> — Course to pull grades from</li>
        </ul>
        <p className="moodle-note">
          Contact your Moodle admin to generate a web service token with <code>gradereport_user_get_grade_items</code> capability.
        </p>
      </div>

      <button className="lms-btn moodle-btn" onClick={handleSync} disabled={loading}>
        {loading ? 'Syncing...' : 'Sync from Moodle'}
      </button>
    </div>
  );
}

export default LMS;
