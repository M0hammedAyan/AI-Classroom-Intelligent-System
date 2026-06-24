import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getStudent, getStudentRisk, getAttendanceLog } from '../api/client';
import ShapChart from '../components/ShapChart';
import './StudentDetail.css';

function StudentDetail({ auth }) {
  const { studentId } = useParams();
  const [student, setStudent] = useState(null);
  const [risk, setRisk] = useState(null);
  const [recentAttendance, setRecentAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, [studentId]);

  async function loadData() {
    setLoading(true);
    setError('');
    try {
      const studentRes = await getStudent(studentId);
      setStudent(studentRes);

      try {
        const riskRes = await getStudentRisk(studentId);
        setRisk(riskRes);
      } catch {
        setRisk(null);
      }

      // Load last 7 days of attendance
      const days = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        days.push(d.toISOString().split('T')[0]);
      }

      const attRecords = [];
      for (const date of days.slice(0, 5)) {
        try {
          const res = await getAttendanceLog('CSE-3A', date);
          const record = res.records.find((r) => r.student_id === studentId);
          if (record) {
            attRecords.push({ date, ...record });
          } else {
            attRecords.push({ date, status: 'no_session' });
          }
        } catch {
          attRecords.push({ date, status: 'no_data' });
        }
      }
      setRecentAttendance(attRecords);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="loading-msg">Loading student details...</div>;
  if (error) return <div className="error-banner">{error}</div>;
  if (!student) return <div className="error-banner">Student not found</div>;

  return (
    <div className="student-detail">
      <Link to="/" className="back-link">← Back to Dashboard</Link>

      <div className="student-header">
        <div>
          <h2>{student.name}</h2>
          <p className="student-meta">
            {student.student_id} · {student.class} · Enrolled {student.enrolled_at || 'N/A'}
          </p>
        </div>
        {risk && (
          <span className={`risk-badge large ${risk.risk_level}`}>
            {risk.risk_level} risk
          </span>
        )}
      </div>

      {risk && (
        <div className="detail-section">
          <h3>Risk Assessment</h3>
          <div className={`risk-panel ${risk.risk_level}`}>
            <div className="risk-info-row">
              <span>Level: <strong>{risk.risk_level}</strong></span>
              <span>Confidence: {risk.confidence}</span>
              <span>Computed: {risk.computed_at ? new Date(risk.computed_at).toLocaleDateString() : '—'}</span>
            </div>
            {risk.reasons && risk.reasons.length > 0 && (
              <ul className="risk-reasons-detail">
                {risk.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      <div className="detail-section">
        <h3>Recent Attendance (Last 5 Sessions)</h3>
        <div className="attendance-timeline">
          {recentAttendance.map((rec, i) => (
            <div className="timeline-item" key={i}>
              <div className="timeline-date">{rec.date}</div>
              <div className={`timeline-status ${rec.status}`}>
                {rec.status === 'present' ? '✓ Present' :
                 rec.status === 'absent' ? '✗ Absent' :
                 rec.status === 'liveness_failed' ? '⚠ Liveness Failed' :
                 rec.status === 'no_session' ? '— No Session' : '— No Data'}
              </div>
              {rec.confidence != null && (
                <div className="timeline-confidence">
                  {(rec.confidence * 100).toFixed(0)}% confidence
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {!risk && (
        <div className="detail-section">
          <p className="no-risk-msg">No risk assessment computed yet for this student.</p>
        </div>
      )}

      <div className="detail-section">
        <h3>AI Explainability (SHAP Analysis)</h3>
        <ShapChart studentId={studentId} />
      </div>
    </div>
  );
}

export default StudentDetail;
