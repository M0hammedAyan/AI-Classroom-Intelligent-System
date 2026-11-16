import React, { useEffect, useState } from 'react';
import { getMyStudentReport, downloadStudentPdf, downloadMyStudentCsv } from '../api/client';

export default function StudentReportView({ studentId = null }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState('');

  useEffect(() => {
    setLoading(true);
    getMyStudentReport()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [studentId]);

  const handleDownload = async (type = 'pdf') => {
    if (!data?.student) return;
    setDownloading(type);
    try {
      if (type === 'pdf') {
        await downloadStudentPdf(data.student.student_id, data.student.name);
      } else {
        await downloadMyStudentCsv(data.student.student_id);
      }
    } catch (err) {
      alert(`Download failed: ${err.message}`);
    } finally {
      setDownloading('');
    }
  };

  if (loading) {
    return <div className="card"><p className="notice">Compiling comprehensive academic report...</p></div>;
  }

  if (error) {
    return <div className="card"><p className="error">Failed to generate report: {error}</p></div>;
  }

  const { student = {}, overall_attendance = {}, subjects = [], academic_risk = {} } = data || {};
  const riskLevel = academic_risk?.level || 'LOW';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Header Banner */}
      <div className="report-header-banner">
        <div>
          <p style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontSize: 11, color: '#d7ef61', margin: '0 0 4px', fontWeight: 700 }}>
            Official Academic Record
          </p>
          <h2>{student.name}</h2>
          <p>
            USN: <b style={{ color: '#fff' }}>{student.student_id}</b>  ·  Class: <b style={{ color: '#fff' }}>{student.class_code || '4th Year AIML'}</b>
            {student.batch && <span className="slot-badge-pill pill-lab" style={{ marginLeft: 8 }}>Batch {student.batch}</span>}
          </p>
        </div>
        <div>
          <button
            className="primary"
            onClick={() => handleDownload('pdf')}
            disabled={!!downloading}
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 20px', fontSize: 14 }}
          >
            <span>📄</span>
            <span>{downloading === 'pdf' ? 'Generating PDF...' : 'Download PDF'}</span>
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => handleDownload('csv')}
            disabled={!!downloading}
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px', fontSize: 13, marginTop: 8 }}
          >
            <span>📊</span>
            <span>{downloading === 'csv' ? 'Exporting CSV...' : 'Download CSV'}</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="report-summary-cards">
        <div className="report-kpi">
          <span>Overall Attendance</span>
          <strong className={overall_attendance.percentage >= 75 ? 'green' : 'red'}>
            {overall_attendance.percentage !== null ? `${overall_attendance.percentage}%` : '-'}
          </strong>
          <small>{overall_attendance.attended_sessions} of {overall_attendance.total_sessions} sessions</small>
        </div>

        <div className="report-kpi">
          <span>Attendance Health</span>
          <strong style={{ fontSize: 20, color: '#334155' }}>
            {overall_attendance.percentage >= 75 ? (
              <span className="green">✓ Safe ({overall_attendance.missable_classes ?? 0} missable)</span>
            ) : (
              <span className="red">⚠️ Critical ({overall_attendance.recovery_classes_needed ?? 0} needed)</span>
            )}
          </strong>
          <small>Minimum 75% VTU rule</small>
        </div>

        <div className="report-kpi">
          <span>Source Verification</span>
          <div style={{ marginTop: 6, fontSize: 12, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <div>Face: <b>{overall_attendance.by_source?.face ?? 0}</b></div>
            <div>Manual: <b>{overall_attendance.by_source?.manual ?? 0}</b></div>
            <div>Seed: <b>{overall_attendance.by_source?.seed ?? 0}</b></div>
          </div>
          <small>Audited session origins</small>
        </div>

        <div className="report-kpi">
          <span>Rule-Based Risk</span>
          <strong className={`risk-value ${riskLevel.toLowerCase()}`}>
            {riskLevel}
          </strong>
          <small>
            {academic_risk?.confidence ? `Confidence: ${Math.round(academic_risk.confidence * 100)}%` : 'Rule-engine checked'}
          </small>
        </div>
      </div>

      {/* Risk Reasons Notice if any */}
      {academic_risk?.reasons && academic_risk.reasons.length > 0 && (
        <div className="card" style={{ borderLeft: '4px solid #f59e0b', background: '#fffbeb' }}>
          <p className="eyebrow" style={{ color: '#b45309' }}>Advisory / Risk Factors Identified</p>
          <ul style={{ margin: '8px 0 0', paddingLeft: 20, color: '#78350f', fontSize: 13, lineHeight: 1.6 }}>
            {academic_risk.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {/* CIE Assessment Table */}
      <div className="card">
        <div className="card-title">
          <div>
            <p className="eyebrow">Academic Performance</p>
            <h2>CIE Assessment & Eligibility</h2>
            <p>Computed according to official VTU Continuous Internal Evaluation policy (Best 2 of 3 CIEs)</p>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Subject</th>
                <th>CIE 1 (25)</th>
                <th>CIE 2 (25)</th>
                <th>CIE 3 (25)</th>
                <th>Final CIE</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((s) => {
                const cie = s.cie || {};
                const assList = cie.assessments || [];
                const c1 = assList.find((a) => a.assessment_type === 'CIE 1');
                const c2 = assList.find((a) => a.assessment_type === 'CIE 2');
                const c3 = assList.find((a) => a.assessment_type === 'CIE 3');

                const isEligible = cie.is_eligible;

                return (
                  <tr key={s.subject_id}>
                    <td>
                      <b>{s.subject_name}</b>
                      <small style={{ display: 'block', color: '#64748b' }}>{s.subject_code} · {s.credits} Credits</small>
                    </td>
                    <td>
                      {c1 ? (
                        c1.status === 'absent' ? (
                          <span className="badge cie-absent">ABSENT</span>
                        ) : (
                          <b>{c1.score} <small>/ {c1.max_score}</small></b>
                        )
                      ) : (
                        <span style={{ color: '#94a3b8' }}>-</span>
                      )}
                    </td>
                    <td>
                      {c2 ? (
                        c2.status === 'absent' ? (
                          <span className="badge cie-absent">ABSENT</span>
                        ) : (
                          <b>{c2.score} <small>/ {c2.max_score}</small></b>
                        )
                      ) : (
                        <span style={{ color: '#94a3b8' }}>-</span>
                      )}
                    </td>
                    <td>
                      {c3 ? (
                        c3.status === 'absent' ? (
                          <span className="badge cie-absent">ABSENT</span>
                        ) : (
                          <b>{c3.score} <small>/ {c3.max_score}</small></b>
                        )
                      ) : (
                        <span style={{ color: '#94a3b8' }}>-</span>
                      )}
                    </td>
                    <td>
                      <b>{cie.final_cie !== null && cie.final_cie !== undefined ? cie.final_cie : (cie.best_two_average ?? '-')}</b>
                    </td>
                    <td>
                      <span className={`badge ${isEligible ? 'cie-eligible' : 'cie-ineligible'}`}>
                        {isEligible ? '✓ Eligible' : 'Ineligible'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Attendance by Subject & Period Breakdown */}
      <div className="card">
        <div className="card-title">
          <div>
            <p className="eyebrow">Attendance Drill-Down</p>
            <h2>Attendance by Subject & Period (S1 - S7)</h2>
            <p>Period distribution and verified capture sources</p>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Subject</th>
                <th>Attended / Total</th>
                <th>Attendance %</th>
                <th>Period Breakdown (S1 - S7 Attended)</th>
                <th>Sources</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((s) => {
                const att = s.attendance || {};
                const periods = att.periods || {};
                const src = att.by_source || {};

                return (
                  <tr key={s.subject_id}>
                    <td>
                      <b>{s.subject_name}</b>
                      <small style={{ display: 'block', color: '#64748b' }}>{s.subject_code}</small>
                    </td>
                    <td>
                      <b>{att.attended}</b> / {att.total}
                    </td>
                    <td>
                      <b className={att.percentage !== null && att.percentage >= 75 ? 'green' : 'red'}>
                        {att.percentage !== null ? `${att.percentage}%` : 'No sessions'}
                      </b>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'].map((p) => {
                          const pInfo = periods[p];
                          if (!pInfo || pInfo.total === 0) return null;
                          return (
                            <span
                              key={p}
                              className="slot-badge-pill"
                              style={{ background: '#f1f5f9', color: '#334155', border: '1px solid #cbd5e1' }}
                              title={`${p}: ${pInfo.attended}/${pInfo.total} (${pInfo.percentage}%)`}
                            >
                              {p}: {pInfo.attended}/{pInfo.total}
                            </span>
                          );
                        })}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 4 }}>
                        {src.face > 0 && <span className="badge face">Face: {src.face}</span>}
                        {src.manual > 0 && <span className="badge manual">Manual: {src.manual}</span>}
                        {src.seed > 0 && <span className="badge seed">Seed: {src.seed}</span>}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
