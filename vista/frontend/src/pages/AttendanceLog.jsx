import { useState, useEffect } from 'react';
import { getAttendanceLog, patchAttendance, exportReport } from '../api/client';
import './AttendanceLog.css';

function AttendanceLog({ auth }) {
  const [classroomId] = useState('CSE-3A'); // Pilot: single classroom
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadLog();
  }, [date]);

  async function loadLog() {
    setLoading(true);
    setError('');
    try {
      const res = await getAttendanceLog(classroomId, date);
      setRecords(res.records);
      setTotal(res.total);
    } catch (err) {
      setError(err.message);
      setRecords([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

  async function handleOverride(attendanceId, currentStatus) {
    const newStatus = currentStatus === 'present' ? 'absent' : 'present';
    const note = prompt(`Mark as ${newStatus}. Reason (optional):`) ?? '';
    try {
      await patchAttendance(attendanceId, newStatus, note || null);
      loadLog(); // Refresh
    } catch (err) {
      alert(`Override failed: ${err.message}`);
    }
  }

  async function handleExport() {
    try {
      const blob = await exportReport(classroomId, date, date, 'csv');
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `attendance_${classroomId}_${date}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  }

  const presentCount = records.filter((r) => r.status === 'present').length;
  const absentCount = records.filter((r) => r.status === 'absent').length;
  const failedCount = records.filter((r) => r.status === 'liveness_failed').length;

  return (
    <div className="attendance-page">
      <div className="page-header">
        <h2>Attendance Log</h2>
        <div className="header-controls">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            aria-label="Select date"
          />
          <button className="export-btn" onClick={handleExport}>
            Export CSV
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="att-stats">
        <span className="att-stat present">Present: {presentCount}</span>
        <span className="att-stat absent">Absent: {absentCount}</span>
        {failedCount > 0 && (
          <span className="att-stat failed">Liveness Failed: {failedCount}</span>
        )}
        <span className="att-stat total">Total: {total}</span>
      </div>

      {loading ? (
        <div className="loading-msg">Loading attendance...</div>
      ) : records.length === 0 ? (
        <p className="no-data-msg">No attendance records for {date}.</p>
      ) : (
        <div className="table-wrap">
          <table className="att-table" aria-label="Attendance records">
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Marked At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.student_id}>
                  <td>{r.student_id}</td>
                  <td>{r.student_name}</td>
                  <td>
                    <span className={`status-badge ${r.status}`}>
                      {r.status === 'liveness_failed' ? 'Liveness Failed' : r.status}
                    </span>
                    {r.is_manual_override && (
                      <span className="override-tag">overridden</span>
                    )}
                  </td>
                  <td>
                    {r.confidence != null ? `${(r.confidence * 100).toFixed(0)}%` : '—'}
                  </td>
                  <td>
                    {r.marked_at
                      ? new Date(r.marked_at).toLocaleTimeString()
                      : '—'}
                  </td>
                  <td>
                    {r.attendance_id && (
                      <button
                        className="override-btn"
                        onClick={() => handleOverride(r.attendance_id, r.status)}
                        title={`Override to ${r.status === 'present' ? 'absent' : 'present'}`}
                      >
                        Override
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AttendanceLog;
