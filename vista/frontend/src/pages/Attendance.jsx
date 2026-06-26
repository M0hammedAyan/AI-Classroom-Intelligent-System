import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function AttendancePage({ auth }) {
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => { loadLog(); }, [date]);

  async function loadLog() {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/attendance/log?classroom_id=CSE-3A&date=${date}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setRecords(data.records || []);
      }
    } catch {} finally { setLoading(false); }
  }

  async function handleExport() {
    try {
      const res = await fetch(`${BASE_URL}/export/report?classroom_id=CSE-3A&from_date=${date}&to_date=${date}&format=csv`, { headers });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = `attendance_${date}.csv`; a.click();
        URL.revokeObjectURL(url);
      }
    } catch {}
  }

  const present = records.filter(r => r.status === 'present').length;
  const absent = records.filter(r => r.status === 'absent').length;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Attendance Log</h2>
          <p className="v-page-subtitle">Present: {present} · Absent: {absent} · Total: {records.length}</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input className="v-input" type="date" value={date} onChange={e => setDate(e.target.value)} style={{ width: '160px' }} />
          <button className="v-btn v-btn-secondary" onClick={handleExport}>Export CSV</button>
        </div>
      </div>

      {loading ? <div className="v-loading">Loading...</div> : (
        <div className="v-table-container">
          <table className="v-table">
            <thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Confidence</th><th>Time</th></tr></thead>
            <tbody>
              {records.length === 0 ? (
                <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No records for {date}</td></tr>
              ) : records.map(r => (
                <tr key={r.student_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{r.student_id}</td>
                  <td style={{ fontWeight: 500 }}>{r.student_name}</td>
                  <td><span className={`v-badge ${r.status === 'present' ? 'v-badge-low' : r.status === 'absent' ? 'v-badge-high' : 'v-badge-medium'}`}>{r.status}</span></td>
                  <td>{r.confidence ? `${(r.confidence * 100).toFixed(0)}%` : '—'}</td>
                  <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{r.marked_at ? new Date(r.marked_at).toLocaleTimeString() : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AttendancePage;
