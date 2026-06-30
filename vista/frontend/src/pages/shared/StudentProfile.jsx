import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function StudentProfile({ auth }) {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [risk, setRisk] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [scores, setScores] = useState([]);
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [shap, setShap] = useState(null);
  const [subjectAtt, setSubjectAtt] = useState(null);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => { loadAll(); }, [studentId]);

  async function downloadReport() {
    try {
      const res = await fetch(`${BASE_URL}/reports/student/${studentId}/pdf`, { headers });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `VISTA_Report_${studentId}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      console.error('Report download failed', e);
    }
  }

  async function loadAll() {
    setLoading(true);
    try {
      const [sRes, rRes, scRes] = await Promise.all([
        fetch(`${BASE_URL}/students/${studentId}`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${BASE_URL}/students/${studentId}/risk`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${BASE_URL}/lms/scores?student_id=${studentId}`, { headers }).then(r => r.ok ? r.json() : { scores: [] }).catch(() => ({ scores: [] })),
      ]);
      setStudent(sRes);
      setRisk(rRes);
      setScores(scRes.scores || []);

      // Load SHAP
      try {
        const shapRes = await fetch(`${BASE_URL}/students/${studentId}/risk/explain`, { headers });
        if (shapRes.ok) setShap(await shapRes.json());
      } catch {}

      // Load per-subject attendance
      try {
        const subjRes = await fetch(`${BASE_URL}/attendance/by-subject/${studentId}`, { headers });
        if (subjRes.ok) setSubjectAtt(await subjRes.json());
      } catch {}

      // Load attendance (last 14 days)
      const attRecords = [];
      for (let i = 0; i < 14; i++) {
        const d = new Date(); d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0];
        try {
          const res = await fetch(`${BASE_URL}/attendance/log?classroom_id=CSE-3A&date=${dateStr}`, { headers });
          if (res.ok) {
            const data = await res.json();
            const record = data.records.find(r => r.student_id === studentId);
            attRecords.push({ date: dateStr, status: record?.status || 'no_session', confidence: record?.confidence });
          }
        } catch {}
      }
      setAttendance(attRecords);
    } catch {}
    setLoading(false);
  }

  async function handleRecompute() {
    await fetch(`${BASE_URL}/students/${studentId}/risk/recompute`, { method: 'POST', headers });
    loadAll();
  }

  if (loading) return <div className="v-loading">Loading student profile...</div>;
  if (!student) return <div className="v-empty">Student not found</div>;

  const presentDays = attendance.filter(a => a.status === 'present').length;
  const totalDays = attendance.filter(a => a.status !== 'no_session').length;
  const attendPct = totalDays > 0 ? ((presentDays / totalDays) * 100).toFixed(0) : '—';
  const avgScore = scores.length > 0 ? (scores.reduce((s, x) => s + (x.score / x.max_score) * 100, 0) / scores.length).toFixed(0) : '—';

  const tabs = ['overview', 'attendance', 'academics', 'risk & ai'];

  return (
    <div className="sp">
      <button className="sp-back" onClick={() => navigate(-1)}>← Back</button>

      {/* Header */}
      <div className="sp-header">
        <div className="sp-avatar">{student.name.charAt(0)}</div>
        <div className="sp-info">
          <h2>{student.name}</h2>
          <p>{student.student_id} · {student.class} · Enrolled {student.enrolled_at || 'N/A'}</p>
        </div>
        {risk && <span className={`v-badge v-badge-${risk.risk_level}`} style={{fontSize:'12px',padding:'4px 12px'}}>{risk.risk_level} risk</span>}
        <button className="v-btn v-btn-secondary" style={{marginLeft:'auto',fontSize:'12px'}} onClick={downloadReport}>📄 Download Report</button>
      </div>

      {/* KPI Strip */}
      <div className="sp-kpis">
        <div className="sp-kpi-item">
          <span className="sp-kpi-num">{attendPct}%</span>
          <span className="sp-kpi-lbl">Attendance</span>
        </div>
        <div className="sp-kpi-item">
          <span className="sp-kpi-num">{avgScore}%</span>
          <span className="sp-kpi-lbl">Avg Score</span>
        </div>
        <div className="sp-kpi-item">
          <span className="sp-kpi-num">{risk?.risk_level || '—'}</span>
          <span className="sp-kpi-lbl">Risk Level</span>
        </div>
        <div className="sp-kpi-item">
          <span className="sp-kpi-num">{scores.length}</span>
          <span className="sp-kpi-lbl">Assessments</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="sp-tabs">
        {tabs.map(t => (
          <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="sp-body">
        {tab === 'overview' && (
          <>
            {risk && risk.reasons && risk.reasons.length > 0 && (
              <div className="sp-alert">
                <strong>⚠ Risk Factors</strong>
                <ul>{risk.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
              </div>
            )}
            <div className="sp-section">
              <h4>Attendance (Last 14 Days)</h4>
              <div className="sp-heatmap">
                {attendance.slice(0, 14).map((a, i) => (
                  <div key={i} className={`sp-dot ${a.status}`} title={`${a.date}: ${a.status}`} />
                ))}
              </div>
              <p className="sp-legend">🟢 Present · 🔴 Absent · ⚪ No session</p>
            </div>
            <div className="sp-section">
              <h4>Recent Scores</h4>
              {scores.length === 0 ? <p className="sp-muted">No scores recorded</p> : (
                <div className="sp-scores">
                  {scores.slice(0, 5).map((s, i) => (
                    <div key={i} className="sp-score-row">
                      <span className="sp-score-subj">{s.subject}</span>
                      <span className={`sp-score-pct ${(s.score/s.max_score*100)>=60?'good':(s.score/s.max_score*100)>=40?'mid':'bad'}`}>
                        {(s.score/s.max_score*100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {tab === 'attendance' && (
          <>
            {/* Per-subject breakdown */}
            {subjectAtt && subjectAtt.by_subject && subjectAtt.by_subject.length > 0 && (
              <div className="sp-section">
                <h4>Per-Subject Attendance</h4>
                <div className="sp-subject-grid">
                  {subjectAtt.by_subject.map((s, i) => (
                    <div key={i} className="sp-subject-card">
                      <div className="sp-subject-name">{s.subject_code}</div>
                      <div className="sp-subject-full">{s.subject_name}</div>
                      <div className={`sp-subject-pct ${s.attendance_pct === null ? '' : s.attendance_pct >= 75 ? 'good' : s.attendance_pct >= 60 ? 'mid' : 'bad'}`}>
                        {s.attendance_pct !== null ? `${s.attendance_pct}%` : '—'}
                      </div>
                      <div className="sp-subject-detail">{s.sessions_attended}/{s.total_sessions} sessions</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Overall Table */}
            <div className="sp-section">
              <h4>Daily Attendance Log</h4>
              <div className="v-table-container">
                <table className="v-table">
                  <thead><tr><th>Date</th><th>Status</th><th>Confidence</th></tr></thead>
                  <tbody>
                    {attendance.filter(a => a.status !== 'no_session').map((a, i) => (
                      <tr key={i}>
                        <td>{a.date}</td>
                        <td><span className={`v-badge v-badge-${a.status==='present'?'low':'high'}`}>{a.status}</span></td>
                        <td>{a.confidence ? `${(a.confidence*100).toFixed(0)}%` : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {tab === 'academics' && (
          <div className="v-table-container">
            <table className="v-table">
              <thead><tr><th>Subject</th><th>Score</th><th>Max</th><th>%</th><th>Date</th></tr></thead>
              <tbody>
                {scores.length === 0 ? <tr><td colSpan="5" className="sp-muted">No records</td></tr> :
                  scores.map((s, i) => (
                    <tr key={i}>
                      <td style={{fontWeight:500}}>{s.subject}</td>
                      <td>{s.score}</td>
                      <td>{s.max_score}</td>
                      <td><span className={`v-badge v-badge-${(s.score/s.max_score*100)>=60?'low':(s.score/s.max_score*100)>=40?'medium':'high'}`}>{(s.score/s.max_score*100).toFixed(0)}%</span></td>
                      <td style={{color:'var(--text-muted)'}}>{s.date}</td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
          </div>
        )}

        {tab === 'risk & ai' && (
          <>
            {risk ? (
              <div className={`sp-risk-card ${risk.risk_level}`}>
                <div className="sp-risk-meta">
                  <span>Level: <strong>{risk.risk_level.toUpperCase()}</strong></span>
                  <span>Confidence: {risk.confidence}</span>
                  <span>Computed: {risk.computed_at ? new Date(risk.computed_at).toLocaleDateString() : '—'}</span>
                </div>
                {risk.reasons?.length > 0 && (
                  <ul className="sp-reasons">{risk.reasons.map((r,i) => <li key={i}>{r}</li>)}</ul>
                )}
              </div>
            ) : <p className="sp-muted">No risk assessment computed yet.</p>}

            {/* SHAP */}
            {shap && shap.explainability?.shap_values && (
              <div className="sp-section">
                <h4>SHAP Feature Importance</h4>
                <p className="sp-muted" style={{marginBottom:'var(--s3)'}}>How each feature contributes to the {shap.risk_level} prediction</p>
                <div className="sp-shap">
                  {Object.entries(shap.explainability.shap_values)
                    .sort((a,b) => Math.abs(b[1]) - Math.abs(a[1]))
                    .map(([feat, val]) => {
                      const maxAbs = Math.max(...Object.values(shap.explainability.shap_values).map(Math.abs), 0.1);
                      const width = (Math.abs(val) / maxAbs) * 100;
                      const positive = val > 0;
                      return (
                        <div key={feat} className="sp-shap-row">
                          <span className="sp-shap-label">{feat.replace(/_/g,' ')}</span>
                          <div className="sp-shap-bar-wrap">
                            <div className={`sp-shap-bar ${positive?'risk':'safe'}`} style={{width:`${width}%`}} />
                          </div>
                          <span className={`sp-shap-val ${positive?'risk':'safe'}`}>{positive?'+':''}{val.toFixed(3)}</span>
                        </div>
                      );
                    })
                  }
                </div>
                <div className="sp-shap-legend">
                  <span className="safe">← Reduces risk</span>
                  <span className="risk">Increases risk →</span>
                </div>
              </div>
            )}

            {['admin','hos','hop'].includes(auth.role) && (
              <button className="v-btn v-btn-primary" style={{marginTop:'var(--s4)'}} onClick={handleRecompute}>Recompute Risk</button>
            )}
          </>
        )}
      </div>

      <style>{`
        .sp { max-width: 800px; }
        .sp-back { font-size: 13px; color: var(--text-muted); margin-bottom: var(--s4); display: inline-block; }
        .sp-back:hover { color: var(--primary); }
        .sp-header { display: flex; align-items: center; gap: var(--s4); margin-bottom: var(--s6); }
        .sp-avatar {
          width: 48px; height: 48px; border-radius: var(--r-full);
          background: linear-gradient(135deg, var(--primary), var(--accent));
          display: flex; align-items: center; justify-content: center;
          font-size: 18px; font-weight: 700; color: white;
        }
        .sp-info h2 { font-size: 18px; font-weight: 700; letter-spacing: -0.02em; }
        .sp-info p { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
        .sp-kpis {
          display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--s3);
          margin-bottom: var(--s5);
        }
        .sp-kpi-item {
          background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md);
          padding: var(--s4); text-align: center;
        }
        .sp-kpi-num { display: block; font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: var(--text); }
        .sp-kpi-lbl { display: block; font-size: 11px; color: var(--text-muted); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.03em; font-weight: 500; }
        .sp-tabs {
          display: flex; gap: 0; border-bottom: 1px solid var(--border); margin-bottom: var(--s5);
        }
        .sp-tabs button {
          padding: var(--s3) var(--s4); font-size: 13px; font-weight: 500;
          color: var(--text-muted); border-bottom: 2px solid transparent;
          transition: all var(--duration) var(--ease);
        }
        .sp-tabs button:hover { color: var(--text); }
        .sp-tabs button.active { color: var(--primary); border-bottom-color: var(--primary); }
        .sp-body { animation: fadeIn 0.3s var(--ease); }
        .sp-alert {
          background: var(--warning-light); border: 1px solid rgba(217,119,6,0.2);
          border-radius: var(--r-md); padding: var(--s4); margin-bottom: var(--s5);
        }
        .sp-alert strong { display: block; font-size: 13px; color: var(--warning); margin-bottom: var(--s2); }
        .sp-alert ul { padding-left: var(--s5); font-size: 12px; color: var(--text-secondary); }
        .sp-alert li { margin-bottom: 2px; }
        .sp-section { margin-bottom: var(--s5); }
        .sp-section h4 { font-size: 13px; font-weight: 600; margin-bottom: var(--s3); }
        .sp-heatmap { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: var(--s2); }
        .sp-dot { width: 20px; height: 20px; border-radius: 4px; }
        .sp-dot.present { background: var(--success); }
        .sp-dot.absent { background: var(--danger); }
        .sp-dot.no_session { background: var(--gray-200); }
        .sp-dot.liveness_failed { background: var(--warning); }
        .sp-legend { font-size: 10px; color: var(--text-muted); }
        .sp-scores { display: flex; flex-direction: column; gap: 6px; }
        .sp-score-row { display: flex; justify-content: space-between; align-items: center; padding: var(--s2) var(--s3); background: var(--bg-secondary); border-radius: var(--r-sm); }
        .sp-score-subj { font-size: 13px; font-weight: 500; }
        .sp-score-pct { font-size: 13px; font-weight: 700; }
        .sp-score-pct.good { color: var(--success); }
        .sp-score-pct.mid { color: var(--warning); }
        .sp-score-pct.bad { color: var(--danger); }
        .sp-muted { font-size: 13px; color: var(--text-muted); }
        .sp-risk-card { border: 1px solid var(--border); border-radius: var(--r-md); padding: var(--s4); margin-bottom: var(--s5); border-left: 3px solid var(--gray-300); }
        .sp-risk-card.high { border-left-color: var(--danger); }
        .sp-risk-card.medium { border-left-color: var(--warning); }
        .sp-risk-card.low { border-left-color: var(--success); }
        .sp-risk-meta { display: flex; gap: var(--s4); font-size: 12px; color: var(--text-muted); margin-bottom: var(--s3); }
        .sp-reasons { padding-left: var(--s5); font-size: 13px; }
        .sp-reasons li { margin-bottom: 3px; }
        .sp-shap { display: flex; flex-direction: column; gap: 8px; }
        .sp-shap-row { display: grid; grid-template-columns: 120px 1fr 60px; align-items: center; gap: var(--s3); }
        .sp-shap-label { font-size: 11px; color: var(--text-secondary); text-align: right; text-transform: capitalize; }
        .sp-shap-bar-wrap { height: 14px; background: var(--gray-100); border-radius: 3px; overflow: hidden; }
        .sp-shap-bar { height: 100%; border-radius: 3px; transition: width 0.6s var(--ease); }
        .sp-shap-bar.risk { background: var(--danger); }
        .sp-shap-bar.safe { background: var(--success); }
        .sp-shap-val { font-size: 11px; font-weight: 600; font-family: var(--mono); }
        .sp-shap-val.risk { color: var(--danger); }
        .sp-shap-val.safe { color: var(--success); }
        .sp-shap-legend { display: flex; justify-content: space-between; font-size: 10px; margin-top: var(--s2); }
        .sp-shap-legend .safe { color: var(--success); }
        .sp-shap-legend .risk { color: var(--danger); }
        .sp-subject-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: var(--s3); margin-bottom: var(--s4); }
        .sp-subject-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-md); padding: var(--s3); text-align: center; }
        .sp-subject-name { font-size: 14px; font-weight: 700; color: var(--primary); }
        .sp-subject-full { font-size: 10px; color: var(--text-muted); margin: 2px 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .sp-subject-pct { font-size: 20px; font-weight: 700; }
        .sp-subject-pct.good { color: var(--success); }
        .sp-subject-pct.mid { color: var(--warning); }
        .sp-subject-pct.bad { color: var(--danger); }
        .sp-subject-detail { font-size: 10px; color: var(--text-muted); margin-top: 2px; }
      `}</style>
    </div>
  );
}

export default StudentProfile;
