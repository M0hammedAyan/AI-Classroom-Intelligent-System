import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function StudentsPage({ auth }) {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [flags, setFlags] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };

  useEffect(() => {
    Promise.all([
      fetch(`${BASE_URL}/students`, { headers }).then(r => r.ok ? r.json() : { students: [] }),
      fetch(`${BASE_URL}/risk`, { headers }).then(r => r.ok ? r.json() : { flags: [] }),
    ]).then(([s, r]) => {
      setStudents(s.students || []);
      setFlags(r.flags || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  const enriched = students.map(s => {
    const flag = flags.find(f => f.student_id === s.student_id);
    return { ...s, risk_level: flag?.risk_level || 'none', reasons: flag?.reasons || [] };
  });

  const filtered = enriched.filter(s =>
    !filter || s.name.toLowerCase().includes(filter.toLowerCase()) ||
    s.student_id.toLowerCase().includes(filter.toLowerCase()) ||
    s.class.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Students ({students.length})</h2>
          <p className="v-page-subtitle">Click any student to view full profile</p>
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <input className="v-input" placeholder="Search by name, ID, or class..." value={filter} onChange={e => setFilter(e.target.value)} style={{ maxWidth: '400px' }} />
      </div>

      <div className="v-table-container">
        <table className="v-table">
          <thead>
            <tr><th>ID</th><th>Name</th><th>Class</th><th>Risk</th><th>Status</th></tr>
          </thead>
          <tbody>
            {filtered.map(s => (
              <tr key={s.student_id} onClick={() => navigate(`/student/${s.student_id}`)}>
                <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{s.student_id}</td>
                <td style={{ fontWeight: 500 }}>{s.name}</td>
                <td>{s.class}</td>
                <td>{s.risk_level !== 'none' ? <span className={`v-badge v-badge-${s.risk_level}`}>{s.risk_level}</span> : '—'}</td>
                <td>{s.is_active ? <span className="v-badge v-badge-low">Active</span> : 'Inactive'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StudentsPage;
