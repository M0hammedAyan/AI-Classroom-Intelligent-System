import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function MentorWatchlist() {
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const auth = JSON.parse(localStorage.getItem("vista_auth") || "{}");
    const token = auth.token;
    const headers = { Authorization: `Bearer ${token}` };

    fetch("/api/v1/mentor/watchlist", { headers })
      .then((r) => r.json())
      .then((data) => {
        setStudents(data.students || []);
      })
      .catch((err) => console.error("Watchlist fetch error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="v-loading">Loading...</div>;
  }

  if (students.length === 0) {
    return (
      <div className="v-page">
        <div className="v-page-header">
          <h2>Watchlist</h2>
        </div>
        <p style={{ textAlign: "center", color: "#64748b", marginTop: "2rem" }}>
          No students currently at risk
        </p>
      </div>
    );
  }

  return (
    <div className="v-page">
      <div className="v-page-header">
        <h2>Watchlist</h2>
      </div>

      <div className="v-table-container">
        <table className="v-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Risk Level</th>
              <th>Key Reason</th>
            </tr>
          </thead>
          <tbody>
            {students.map((s) => (
              <tr
                key={s.student_id}
                onClick={() => navigate(`/mentor/student/${s.student_id}`)}
                style={{ cursor: "pointer" }}
              >
                <td>{s.name}</td>
                <td>
                  <span className={`v-badge v-badge-${s.risk_level}`}>
                    {s.risk_level}
                  </span>
                </td>
                <td>{s.risk_reasons?.[0] || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default MentorWatchlist;
