import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const BASE_URL = '/api/v1';

function SchoolsPage() {
  const navigate = useNavigate();
  const [schools, setSchools] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetch(`${BASE_URL}/admin/schools`, { headers })
      .then(r => r.json())
      .then(data => setSchools(data.schools || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="v-loading">Loading...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Schools</h2>
          <p className="v-page-subtitle">All schools in the institution</p>
        </div>
      </div>

      {schools.length === 0 ? (
        <div className="v-empty">No schools created yet.</div>
      ) : (
        <div className="v-table-container">
          <table className="v-table">
            <thead>
              <tr><th>Code</th><th>Name</th><th>Action</th></tr>
            </thead>
            <tbody>
              {schools.map(s => (
                <tr key={s.id} onClick={() => navigate(`/admin/school/${s.id}`)}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{s.code}</td>
                  <td>{s.name}</td>
                  <td><button className="v-btn v-btn-sm v-btn-secondary">View Departments →</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default SchoolsPage;
