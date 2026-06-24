import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function HOPDashboard() {
  const [loading, setLoading] = useState(true);
  const [dash, setDash] = useState(null);
  const [riskData, setRiskData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const auth = JSON.parse(localStorage.getItem("vista_auth") || "{}");
    const token = auth.token;
    const headers = { Authorization: `Bearer ${token}` };

    Promise.all([
      fetch("/api/v1/dashboard/hop", { headers }).then((r) => r.json()),
      fetch("/api/v1/risk", { headers }).then((r) => r.json()),
    ])
      .then(([dashRes, riskRes]) => {
        setDash(dashRes);
        setRiskData(riskRes.flags || []);
      })
      .catch((err) => console.error("Dashboard fetch error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="v-loading">Loading...</div>;
  }

  const highRisk = riskData.filter((f) => f.risk_level === "high");
  const mediumRisk = riskData.filter((f) => f.risk_level === "medium");
  const atRiskStudents = [...highRisk, ...mediumRisk];

  return (
    <div className="v-page">
      <div className="v-page-header">
        <h2>Department Dashboard</h2>
      </div>

      <div className="v-kpi-grid">
        <div className="v-kpi">
          <div className="v-kpi-label">Teachers</div>
          <div className="v-kpi-value">{dash?.teachers ?? 0}</div>
        </div>
        <div className="v-kpi">
          <div className="v-kpi-label">Subjects</div>
          <div className="v-kpi-value">{dash?.subjects ?? 0}</div>
        </div>
        <div className="v-kpi">
          <div className="v-kpi-label">Students</div>
          <div className="v-kpi-value">{dash?.students ?? 0}</div>
        </div>
        <div className="v-kpi v-kpi">
          <div className="v-kpi-label">At Risk</div>
          <div className="v-kpi-value">{atRiskStudents.length}</div>
        </div>
      </div>

      <div className="v-table-container">
        <h3>At-Risk Students</h3>
        <table className="v-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Risk Level</th>
              <th>Reason</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {atRiskStudents.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", color: "#64748b" }}>
                  No at-risk students
                </td>
              </tr>
            ) : (
              atRiskStudents.map((s) => (
                <tr
                  key={s.student_id}
                  onClick={() => navigate(`/hop/student/${s.student_id}`)}
                  style={{ cursor: "pointer" }}
                >
                  <td>{s.student_name}</td>
                  <td>
                    <span className={`v-badge v-badge-${s.risk_level}`}>
                      {s.risk_level}
                    </span>
                  </td>
                  <td>{s.reasons?.[0] || "—"}</td>
                  <td>{s.confidence != null ? `${Math.round(s.confidence * 100)}%` : "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HOPDashboard;
