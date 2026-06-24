import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function DepartmentView({ auth }) {
  const { departmentId } = useParams();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [students, setStudents] = useState([]);
  const [riskFlags, setRiskFlags] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };
  const roleBase = `/${auth.role}`;

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/admin/users`, { headers }).then(r => r.json()),
      fetch(`${BASE_URL}/students`, { headers }).then(r => r.json()),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.json()),
    ]).then(([usersRes, studsRes, riskRes]) => {
      // Filter users by department
      const deptUsers = (usersRes.users || []).filter(u => u.department_id === departmentId);
      setUsers(deptUsers);
      setStudents(studsRes.students || []);
      setRiskFlags(riskRes.flags || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [departmentId]);

  if (loading) return <div className="v-loading">Loading...</div>;

  const mentors = users.filter(u => u.role === 'mentor');
  const teachers = users.filter(u => u.role === 'teacher');
  const hop = users.find(u => u.role === 'hop');

  // Enrich students with risk
  const enriched = students.map(s => {
    const flag = riskFlags.find(f => f.student_id === s.student_id);
    return { ...s, risk_level: flag?.risk_level || 'none' };
  });

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Department: {departmentId}</h2>
          <p className="v-page-subtitle">{hop ? `HOP: ${hop.name}` : 'No HOP assigned'}</p>
        </div>
        <button className="v-btn v-btn-secondary" onClick={() => navigate(-1)}>← Back</button>
      </div>

      {/* Staff */}
      <div className="v-section">
        <div className="v-table-container">
          <div className="v-table-header">
            <span className="v-table-title">Staff ({mentors.length + teachers.length})</span>
          </div>
          <table className="v-table">
            <thead><tr><th>Name</th><th>Role</th><th>Email</th></tr></thead>
            <tbody>
              {[...teachers, ...mentors].map(u => (
                <tr key={u.id}>
                  <td style={{ fontWeight: 500 }}>{u.name}</td>
                  <td><span className={`v-badge v-badge-info`}>{u.role}</span></td>
                  <td style={{ color: 'var(--text-secondary)' }}>{u.email}</td>
                </tr>
              ))}
              {mentors.length + teachers.length === 0 && (
                <tr><td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No staff assigned</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Students */}
      <div className="v-section">
        <div className="v-table-container">
          <div className="v-table-header">
            <span className="v-table-title">Students ({enriched.length})</span>
          </div>
          <table className="v-table">
            <thead><tr><th>ID</th><th>Name</th><th>Class</th><th>Risk</th></tr></thead>
            <tbody>
              {enriched.map(s => (
                <tr key={s.student_id} onClick={() => navigate(`${roleBase}/student/${s.student_id}`)}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{s.student_id}</td>
                  <td style={{ fontWeight: 500 }}>{s.name}</td>
                  <td>{s.class}</td>
                  <td>{s.risk_level !== 'none' ? <span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span> : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DepartmentView;
