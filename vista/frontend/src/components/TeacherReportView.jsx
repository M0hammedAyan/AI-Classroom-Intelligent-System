import React, { useEffect, useState } from 'react';
import { getMyTeacherReport, downloadMyTeacherPdf, downloadMyTeacherCsv } from '../api/client';

export default function TeacherReportView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState('');

  useEffect(() => {
    setLoading(true);
    getMyTeacherReport()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleDownload = async (type) => {
    if (!data) return;
    setDownloading(type);
    try {
      const name = data.teacher?.name || 'teacher';
      if (type === 'pdf') await downloadMyTeacherPdf(name);
      else await downloadMyTeacherCsv(name);
    } catch (e) {
      alert('Download failed: ' + e.message);
    } finally {
      setDownloading('');
    }
  };

  if (loading) {
    return <div className="card"><p className="notice">Loading teacher performance report...</p></div>;
  }

  if (error) {
    return <div className="card"><p className="error">Failed to load report: {error}</p></div>;
  }

  const { teacher = {}, summary = {}, subjects = [], recent_sessions = [] } = data || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header Banner */}
      <div className="report-header-banner">
        <div>
          <p style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontSize: 11, color: '#d7ef61', margin: '0 0 4px', fontWeight: 700 }}>
            Faculty Performance Report
          </p>
          <h2>{teacher.name}</h2>
          <p>
            Email: <b style={{ color: '#fff' }}>{teacher.email}</b>  ·  Department: <b style={{ color: '#fff' }}>{teacher.department_id || 'AIML'}</b>
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            className="btn btn-secondary"
            onClick={() => handleDownload('pdf')}
            disabled={downloading === 'pdf'}
            style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, padding: '8px 16px' }}
          >
            {downloading === 'pdf' ? '⏳ Generating…' : '📄 Download PDF'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => handleDownload('csv')}
            disabled={downloading === 'csv'}
            style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, padding: '8px 16px' }}
          >
            {downloading === 'csv' ? '⏳ Exporting…' : '📊 Download CSV'}
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="report-summary-cards">
        <div className="report-kpi">
          <span>Weekly Commitment</span>
          <strong>{summary.scheduled_slots_per_week ?? 0}</strong>
          <small>scheduled timetable slots/week</small>
        </div>

        <div className="report-kpi">
          <span>Conducted Sessions</span>
          <strong className="green">{summary.held_sessions_count ?? 0}</strong>
          <small>total classes/labs held</small>
        </div>

        <div className="report-kpi">
          <span>Extra Classes</span>
          <strong style={{ color: '#8b5cf6' }}>{summary.extra_classes_count ?? 0}</strong>
          <small>beyond regular schedule</small>
        </div>

        <div className="report-kpi">
          <span>AI Face Captures</span>
          <strong style={{ color: '#0284c7' }}>{summary.captures_count ?? 0}</strong>
          <small>automated camera sessions</small>
        </div>

        <div className="report-kpi">
          <span>Manual Corrections</span>
          <strong style={{ color: '#f59e0b' }}>{summary.manual_corrections_count ?? 0}</strong>
          <small>audited teacher adjustments</small>
        </div>
      </div>

      {/* Subject Summaries Table */}
      <div className="card">
        <div className="card-title">
          <div>
            <p className="eyebrow">Subject-Wise Analytics</p>
            <h2>Teaching Portfolio Attendance</h2>
            <p>Average student attendance and total sessions delivered per subject</p>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Subject</th>
                <th>Sessions Held</th>
                <th>Total Student-Sessions Attended</th>
                <th>Average Attendance</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((s) => (
                <tr key={s.subject_id}>
                  <td>
                    <b>{s.subject_name}</b>
                    <small style={{ display: 'block', color: '#64748b' }}>{s.subject_code}</small>
                  </td>
                  <td><b>{s.sessions_held}</b></td>
                  <td>{s.total_present_count}</td>
                  <td>
                    <b className={s.average_attendance_pct >= 75 ? 'green' : 'red'}>
                      {s.average_attendance_pct !== null ? `${s.average_attendance_pct}%` : 'N/A'}
                    </b>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Sessions Table */}
      <div className="card">
        <div className="card-title">
          <div>
            <p className="eyebrow">Class Log</p>
            <h2>Recent Teaching Sessions</h2>
            <p>Chronological log of classes held, students present, and extra classes</p>
          </div>
        </div>

        {recent_sessions.length === 0 ? (
          <p className="muted" style={{ padding: '16px 0' }}>No sessions recorded yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Period</th>
                  <th>Subject</th>
                  <th>Present</th>
                  <th>Absent</th>
                  <th>Type</th>
                  <th>Capture Sources</th>
                </tr>
              </thead>
              <tbody>
                {recent_sessions.map((sess, idx) => (
                  <tr key={idx}>
                    <td className="mono"><b>{sess.date}</b></td>
                    <td><span className="mono">{sess.period_label || 'S1'}</span></td>
                    <td>{sess.subject_name || sess.subject_id}</td>
                    <td><b className="green">{sess.present_count}</b></td>
                    <td><span className="red">{sess.absent_count}</span></td>
                    <td>
                      {sess.is_extra_class ? (
                        <span className="badge" style={{ background: '#ede9fe', color: '#6b21a8' }}>
                          Extra Class: {sess.extra_class_reason || 'Special session'}
                        </span>
                      ) : (
                        <span className="badge" style={{ background: '#f1f5f9', color: '#475569' }}>
                          Regular
                        </span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 4 }}>
                        {(sess.sources || []).map((src) => (
                          <span key={src} className={`badge ${src}`}>{src}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
