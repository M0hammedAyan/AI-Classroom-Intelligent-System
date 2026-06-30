import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function AttendanceOverride({ auth }) {
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [classroomId, setClassroomId] = useState('CSE-3A');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const headers = { Authorization: `Bearer ${auth.token}`, 'Content-Type': 'application/json' };

  async function loadLog() {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`${BASE_URL}/attendance/log?classroom_id=${classroomId}&date=${date}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setRecords(data.records || []);
      }
    } catch {}
    setLoading(false);
  }

  useEffect(() => { loadLog(); }, [date, classroomId]);

  async function handleOverride(record, newStatus) {
    if (!record.attendance_id && newStatus === 'present') {
      // Need to manually mark present — use mark endpoint with manual flag
      // For now, show info
      setMessage({ type: 'info', text: `Manual marking for absent students requires the mark endpoint. Use Mark Attendance page.` });
      return;
    }
    if (!record.attendance_id) return;

    try {
      const res = await fetch(`${BASE_URL}/attendance/${record.attendance_id}`, {
        method: 'PATCH', headers,
        body: JSON.stringify({ status: newStatus, note: 'Manual override by teacher' }),
      });
      if (res.ok) {
        setMessage({ type: 'success', text: `${record.student_name} marked as ${newStatus}` });
        loadLog();
      } else {
        const data = await res.json();
        setMessage({ type: 'error', text: data.detail?.message || 'Failed' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Network error' });
    }
  }

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Attendance Override</h2>
          <p className="v-page-subtitle">Manually correct attendance records</p>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 'var(--s3)', marginBottom: 'var(--s5)', alignItems: 'center', flexWrap: 'wrap' }}>
        <div>
          <label className="v-label">Date</label>
          <input className="v-input" type="date" value={date} onChange={e => setDate(e.target.value)} style={{ width: '160px' }} />
        </div>
        <div>
          <label className="v-label">Class</label>
          <select className="v-select" style={{ width: '160px' }} value={classroomId} onChange={e => setClassroomId(e.target.value)}>
            <option value="CSE-3A">CSE-3A</option>
            <option value="AIML-4A">AIML-4A</option>
          </select>
        </div>
        <button className="v-btn v-btn-secondary" style={{ marginTop: '18px' }} onClick={loadLog}>Refresh</button>
      </div>

      {message && (
        <div style={{
          padding: 'var(--s3) var(--s4)', marginBottom: 'var(--s4)', borderRadius: 'var(--r-sm)',
          fontSize: '12px', fontWeight: 500,
          background: message.type === 'success' ? 'var(--success-light)' : message.type === 'error' ? 'var(--danger-light)' : 'var(--primary-light)',
          color: message.type === 'success' ? 'var(--success)' : message.type === 'error' ? 'var(--danger)' : 'var(--primary)',
        }}>
          {message.text}
        </div>
      )}

      {loading ? (
        <div className="v-loading">Loading attendance log...</div>
      ) : (
        <div className="v-table-container">
          <div className="v-table-header">
            <span className="v-table-title">{records.length} students · {date}</span>
          </div>
          <table className="v-table">
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Override</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: 'var(--mono)', fontSize: '12px' }}>{r.student_id}</td>
                  <td style={{ fontWeight: 500 }}>{r.student_name}</td>
                  <td>
                    <span className={`v-badge v-badge-${r.status === 'present' ? 'low' : 'high'}`}>
                      {r.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>
                    {r.confidence ? `${(r.confidence * 100).toFixed(0)}%` : '—'}
                  </td>
                  <td>
                    {r.is_manual_override && (
                      <span style={{ fontSize: '10px', color: 'var(--warning)' }}>✏️ Manual</span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {r.status !== 'present' && r.attendance_id && (
                        <button
                          className="v-btn v-btn-sm v-btn-secondary"
                          style={{ fontSize: '11px', padding: '2px 8px' }}
                          onClick={() => handleOverride(r, 'present')}
                        >
                          Mark Present
                        </button>
                      )}
                      {r.status === 'present' && r.attendance_id && (
                        <button
                          className="v-btn v-btn-sm v-btn-secondary"
                          style={{ fontSize: '11px', padding: '2px 8px', color: 'var(--danger)' }}
                          onClick={() => handleOverride(r, 'absent')}
                        >
                          Mark Absent
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr><td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No records for this date</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AttendanceOverride;
