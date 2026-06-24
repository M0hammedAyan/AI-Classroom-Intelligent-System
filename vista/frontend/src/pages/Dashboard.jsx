import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getStudents, listRiskFlags, getAttendanceLog } from '../api/client';
import { AttendanceTrend, RiskDistribution } from '../components/Charts';
import './Dashboard.css';

function Dashboard({ auth }) {
  const [students, setStudents] = useState([]);
  const [riskFlags, setRiskFlags] = useState([]);
  const [todayAttendance, setTodayAttendance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError('');
    try {
      const [studentsRes, riskRes] = await Promise.all([
        getStudents(),
        listRiskFlags(),
      ]);
      setStudents(studentsRes.students);
      setRiskFlags(riskRes.flags);

      // Try to load today's attendance
      const today = new Date().toISOString().split('T')[0];
      try {
        const attRes = await getAttendanceLog('CSE-3A', today);
        setTodayAttendance(attRes);
      } catch {
        // No attendance for today — that's fine
        setTodayAttendance(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading-msg">Loading dashboard...</div>;
  }

  const totalStudents = students.length;
  const highRisk = riskFlags.filter((f) => f.risk_level === 'high').length;
  const mediumRisk = riskFlags.filter((f) => f.risk_level === 'medium').length;
  const lowRisk = riskFlags.filter((f) => f.risk_level === 'low').length;

  const presentToday = todayAttendance
    ? todayAttendance.records.filter((r) => r.status === 'present').length
    : '—';
  const totalToday = todayAttendance ? todayAttendance.total : '—';

  // Top at-risk students (high + medium)
  const atRisk = riskFlags
    .filter((f) => f.risk_level === 'high' || f.risk_level === 'medium')
    .sort((a, b) => {
      const order = { high: 0, medium: 1, low: 2 };
      return order[a.risk_level] - order[b.risk_level];
    });

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>

      {error && <div className="error-banner">{error}</div>}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Students</div>
          <div className="stat-value">{totalStudents}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Present Today</div>
          <div className="stat-value">
            {presentToday}{totalToday !== '—' ? `/${totalToday}` : ''}
          </div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">High Risk</div>
          <div className="stat-value">{highRisk}</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-label">Medium Risk</div>
          <div className="stat-value">{mediumRisk}</div>
        </div>
        <div className="stat-card low">
          <div className="stat-label">Low Risk</div>
          <div className="stat-value">{lowRisk}</div>
        </div>
      </div>

      {atRisk.length > 0 && (
        <>
          <div className="charts-row">
            <AttendanceTrend classroomId="CSE-3A" />
            <RiskDistribution flags={riskFlags} />
          </div>

          <h3 className="section-title">Students Requiring Attention</h3>
          <div className="risk-summary">
            {atRisk.map((flag) => (
              <div className="risk-item" key={flag.student_id}>
                <span className={`risk-badge ${flag.risk_level}`}>
                  {flag.risk_level}
                </span>
                <div className="risk-item-info">
                  <Link to={`/student/${flag.student_id}`} className="risk-item-name">
                    {flag.student_name}
                  </Link>
                  <div className="risk-item-reason">
                    {flag.reasons.length > 0 ? flag.reasons[0] : 'No specific reason flagged'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {atRisk.length === 0 && !loading && (
        <>
          <div className="charts-row">
            <AttendanceTrend classroomId="CSE-3A" />
            <RiskDistribution flags={riskFlags} />
          </div>
          <p style={{ color: '#64748b' }}>No students currently flagged. All clear.</p>
        </>
      )}
    </div>
  );
}

export default Dashboard;
