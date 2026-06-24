import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ShapChart from '../../components/ShapChart';
import './StudentProfile.css';

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

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => { loadAll(); }, [studentId]);

  async function loadAll() {
    setLoading(true);
    try {
      const [sRes, rRes, scRes] = await Promise.all([
        fetch(`${BASE_URL}/students/${studentId}`, { headers }).then(r => r.json()),
        fetch(`${BASE_URL}/students/${studentId}/risk`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${BASE_URL}/lms/scores?student_id=${studentId}`, { headers }).then(r => r.ok ? r.json() : { scores: [] }).catch(() => ({ scores: [] })),
      ]);
      setStudent(sRes);
      setRisk(rRes);
      setScores(scRes.scores || []);

      // Load last 14 days attendance
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

  if (loading) return <div className="sp-loading">Loading student profile...</div>;
  if (!student) return <div className="sp-error">Student not found</div>;

  const presentDays = attendance.filter(a => a.status === 'present').length;
  const totalDays = attendance.filter(a => a.status !== 'no_session').length;
  const attendPct = totalDays > 0 ? ((presentDays / totalDays) * 100).toFixed(0) : '—';
  const avgScore = scores.length > 0 ? (scores.reduce((s, x) => s + (x.score / x.max_score) * 100, 0) / scores.length).toFixed(0) : '—';

  return (
    <div className="student-profile">
      <button className="sp-back" onClick={() => navigate(-1)}>← Back</button>

      <div className="sp-header">
        <div className="sp-info">
          <h2>{student.name}</h2>
          <p>{student.student_id} · {student.class} · Enrolled {student.enrolled_at || 'N/A'}</p>
        </div>
        {risk && <span className={`sp-risk-badge ${risk.risk_level}`}>{risk.risk_level} RISK</span>}
      </div>

      <div className="sp-kpis">
        <div className="sp-kpi"><span className="sp-kpi-val">{attendPct}%</span><span className="sp-kpi-lbl">Attendance</span></div>
        <div className="sp-kpi"><span className="sp-kpi-val">{avgScore}%</span><span className="sp-kpi-lbl">Avg Score</span></div>
        <div className="sp-kpi"><span className="sp-kpi-val">{risk?.risk_level || '—'}</span><span className="sp-kpi-lbl">Risk Level</span></div>
        <div className="sp-kpi"><span className="sp-kpi-val">{scores.length}</span><span className="sp-kpi-lbl">Assessments</span></div>
      </div>

      <div className="sp-tabs">
        {['overview', 'attendance', 'academics', 'risk', 'actions'].map(t => (
          <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="sp-content">
        {tab === 'overview' && <OverviewTab attendance={attendance} scores={scores} risk={risk} />}
        {tab === 'attendance' && <AttendanceTab attendance={attendance} />}
        {tab === 'academics' && <AcademicsTab scores={scores} />}
        {tab === 'risk' && <RiskTab studentId={studentId} risk={risk} onRecompute={handleRecompute} auth={auth} />}
        {tab === 'actions' && <ActionsTab studentId={studentId} student={student} auth={auth} />}
      </div>
    </div>
  );
}

function OverviewTab({ attendance, scores, risk }) {
  return (
    <div className="sp-tab-content">
      {risk && risk.reasons && risk.reasons.length > 0 && (
        <div className="sp-alert-box">
          <h4>⚠️ Risk Factors</h4>
          <ul>{risk.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
        </div>
      )}
      <div className="sp-section">
        <h4>Recent Attendance (14 days)</h4>
        <div className="sp-calendar">
          {attendance.slice(0, 14).map((a, i) => (
            <div key={i} className={`sp-day ${a.status}`} title={`${a.date}: ${a.status}`} />
          ))}
        </div>
        <p className="sp-legend">🟢 Present  🔴 Absent  ⚪ No Session</p>
      </div>
      <div className="sp-section">
        <h4>Recent Scores</h4>
        {scores.slice(0, 5).map((s, i) => (
          <div key={i} className="sp-score-row">
            <span>{s.subject}</span>
            <span className={`sp-score-pct ${(s.score/s.max_score*100) >= 60 ? 'good' : (s.score/s.max_score*100) >= 40 ? 'warn' : 'bad'}`}>
              {(s.score/s.max_score*100).toFixed(0)}%
            </span>
            <span className="sp-score-date">{s.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AttendanceTab({ attendance }) {
  const present = attendance.filter(a => a.status === 'present').length;
  const absent = attendance.filter(a => a.status === 'absent').length;
  const total = attendance.filter(a => a.status !== 'no_session').length;

  return (
    <div className="sp-tab-content">
      <div className="sp-mini-stats">
        <span className="present">Present: {present}</span>
        <span className="absent">Absent: {absent}</span>
        <span>Total Sessions: {total}</span>
        <span>Rate: {total > 0 ? ((present/total)*100).toFixed(0) : 0}%</span>
      </div>
      <table className="sp-table">
        <thead><tr><th>Date</th><th>Status</th><th>Confidence</th></tr></thead>
        <tbody>
          {attendance.filter(a => a.status !== 'no_session').map((a, i) => (
            <tr key={i}>
              <td>{a.date}</td>
              <td><span className={`sp-status ${a.status}`}>{a.status}</span></td>
              <td>{a.confidence ? `${(a.confidence*100).toFixed(0)}%` : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AcademicsTab({ scores }) {
  return (
    <div className="sp-tab-content">
      {scores.length === 0 ? <p>No academic records found.</p> : (
        <table className="sp-table">
          <thead><tr><th>Subject</th><th>Score</th><th>Max</th><th>%</th><th>Date</th></tr></thead>
          <tbody>
            {scores.map((s, i) => (
              <tr key={i}>
                <td>{s.subject}</td>
                <td>{s.score}</td>
                <td>{s.max_score}</td>
                <td className={`${(s.score/s.max_score*100) >= 60 ? 'good' : 'bad'}`}>{(s.score/s.max_score*100).toFixed(0)}%</td>
                <td>{s.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function RiskTab({ studentId, risk, onRecompute, auth }) {
  return (
    <div className="sp-tab-content">
      {risk ? (
        <>
          <div className={`sp-risk-panel ${risk.risk_level}`}>
            <div className="sp-risk-header">
              <span>Level: <strong>{risk.risk_level.toUpperCase()}</strong></span>
              <span>Confidence: {risk.confidence}</span>
              <span>Computed: {risk.computed_at ? new Date(risk.computed_at).toLocaleDateString() : '—'}</span>
            </div>
            {risk.reasons?.length > 0 && (
              <ul className="sp-reasons">{risk.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
            )}
          </div>
          <div className="sp-section">
            <h4>SHAP Feature Importance</h4>
            <ShapChart studentId={studentId} />
          </div>
        </>
      ) : (
        <p>No risk assessment computed yet.</p>
      )}
      {['admin', 'hos', 'hop'].includes(auth.role) && (
        <button className="sp-btn" onClick={onRecompute}>🔄 Recompute Risk</button>
      )}
    </div>
  );
}

function ActionsTab({ studentId, student, auth }) {
  return (
    <div className="sp-tab-content">
      <h4>Available Actions</h4>
      <div className="sp-actions-grid">
        <button className="sp-action-btn">📄 Export Student PDF</button>
        {['admin', 'hos', 'hop'].includes(auth.role) && (
          <button className="sp-action-btn">🔄 Recompute Risk</button>
        )}
        {['admin', 'hos', 'hop', 'mentor'].includes(auth.role) && (
          <button className="sp-action-btn">🤝 Log Intervention</button>
        )}
        {['admin', 'hos', 'hop'].includes(auth.role) && (
          <button className="sp-action-btn">👤 Assign Mentor</button>
        )}
        <button className="sp-action-btn">📧 Notify Teacher</button>
        <button className="sp-action-btn">📊 View Full Analytics</button>
      </div>
    </div>
  );
}

export default StudentProfile;
