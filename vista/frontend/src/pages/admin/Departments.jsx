import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const BASE_URL = '/api/v1';

function DepartmentsPage() {
  const navigate = useNavigate();
  const { schoolId } = useParams();
  const [departments, setDepartments] = useState([]);
  const [schoolName, setSchoolName] = useState('');
  const [loading, setLoading] = useState(true);

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    const url = schoolId
      ? `${BASE_URL}/admin/departments?school_id=${schoolId}`
      : `${BASE_URL}/admin/departments`;
    fetch(url, { headers })
      .then(r => r.json())
      .then(data => setDepartments(data.departments || []))
      .catch(() => {})
      .finally(() => setLoading(false));

    if (schoolId) {
      fetch(`${BASE_URL}/admin/schools`, { headers })
        .then(r => r.json())
        .then(data => {
          const s = (data.schools || []).find(x => x.id === schoolId);
          if (s) setSchoolName(s.name);
        })
        .catch(() => {});
    }
  }, [schoolId]);

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Departments</h2>
          <p className="v-page-subtitle">{schoolName || 'All departments'}</p>
        </div>
        {schoolId && (
          <button className="v-btn v-btn-secondary" onClick={() => navigate('/admin/schools')}>← Back to Schools</button>
        )}
      </div>

      {departments.length === 0 ? (
        <div className="v-empty">No departments found.</div>
      ) : (
        <div className="v-table-container">
          <table className="v-table">
            <thead>
              <tr><th>Code</th><th>Name</th><th>School</th><th>Action</th></tr>
            </thead>
            <tbody>
              {departments.map(d => (
                <tr key={d.id} onClick={() => navigate(`/admin/department/${d.id}`)}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{d.code}</td>
                  <td>{d.name}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{d.school_id}</td>
                  <td><button className="v-btn v-btn-sm v-btn-secondary">View Staff & Students →</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default DepartmentsPage;
