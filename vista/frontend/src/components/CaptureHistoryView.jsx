import React, { useEffect, useState } from 'react';
import { getCaptureHistory } from '../api/client';

export default function CaptureHistoryView({ userRole = 'teacher', classId = '' }) {
  const [data, setData] = useState({ events: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const loadData = () => {
    setLoading(true);
    const params = { limit: 50 };
    if (statusFilter) params.status = statusFilter;
    if (classId) params.class_id = classId;

    getCaptureHistory(params)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, classId]);

  return (
    <div className="card">
      <div className="card-title">
        <div>
          <p className="eyebrow">Biometric Security & Auditing</p>
          <h2>Face Attendance Capture History {classId ? `· Filtered by ${classId}` : ''}</h2>
          <p>Complete audit log of classroom face capture sessions</p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: 'auto', padding: '6px 12px', fontSize: 13 }}
          >
            <option value="">All statuses</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          <button className="secondary" onClick={loadData}>Refresh</button>
        </div>
      </div>

      {/* Privacy Guarantee Notice */}
      <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 8, padding: '12px 16px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 20 }}>🛡️</span>
        <div style={{ fontSize: 12, color: '#166534' }}>
          <b>Zero-Biometric-Storage Architecture:</b> In compliance with student privacy regulations, captured classroom images and facial embeddings are permanently discarded after processing. Only SHA-256 cryptographic hashes and event metadata are retained for tamper-evident auditing.
        </div>
      </div>

      {loading && <p className="notice">Loading capture audit records...</p>}
      {error && <p className="error">Failed to load capture records: {error}</p>}

      {!loading && !error && data.events.length === 0 && (
        <p className="muted" style={{ padding: '24px 0', textAlign: 'center' }}>
          No face attendance capture sessions recorded yet.
        </p>
      )}

      {!loading && !error && data.events.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Captured At (IST)</th>
                <th>Subject & Class</th>
                <th>Status</th>
                <th>Detected</th>
                <th>Recognized</th>
                <th>Unrecognized</th>
                <th>Liveness Rej.</th>
                <th>Duplicates</th>
                <th>Type</th>
                <th>Integrity SHA-256</th>
              </tr>
            </thead>
            <tbody>
              {data.events.map((e) => (
                <tr key={e.id}>
                  <td className="mono" style={{ whiteSpace: 'nowrap' }}>
                    {e.captured_at ? e.captured_at.replace('T', ' ').slice(0, 19) : '-'}
                  </td>
                  <td>
                    <b>{e.subject_id || 'Class Session'}</b>
                    <small style={{ display: 'block', color: '#64748b' }}>
                      {e.class_id || 'AIML-4A'} {e.slot_id ? `· Slot ${e.slot_id}` : ''}
                    </small>
                  </td>
                  <td>
                    <span className={`audit-chip-status ${e.status}`}>
                      {e.status === 'completed' ? '✓ Completed' : '✕ Failed'}
                    </span>
                  </td>
                  <td><b>{e.faces_detected}</b></td>
                  <td><span className="green"><b>{e.recognized_count}</b></span></td>
                  <td>
                    <span className={e.unrecognized_count > 0 ? 'red' : ''}>
                      {e.unrecognized_count}
                    </span>
                  </td>
                  <td>
                    <span className={e.liveness_rejected_count > 0 ? 'red' : ''}>
                      {e.liveness_rejected_count}
                    </span>
                  </td>
                  <td>{e.duplicates_skipped}</td>
                  <td>
                    {e.is_extra_class ? (
                      <span className="badge" style={{ background: '#ede9fe', color: '#6b21a8' }}>
                        Extra Class
                      </span>
                    ) : (
                      <span className="badge" style={{ background: '#f1f5f9', color: '#475569' }}>
                        Regular
                      </span>
                    )}
                  </td>
                  <td>
                    <span className="hash-pill" title={e.image_sha256}>
                      {e.image_sha256 ? `${e.image_sha256.slice(0, 12)}...` : 'N/A'}
                    </span>
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
