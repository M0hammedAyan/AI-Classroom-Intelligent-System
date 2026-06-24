import { useState, useEffect } from 'react';
import { explainRisk } from '../api/client';
import './ShapChart.css';

function ShapChart({ studentId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!studentId) return;
    setLoading(true);
    explainRisk(studentId)
      .then((res) => {
        setData(res);
        setError('');
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) return <div className="shap-loading">Loading SHAP analysis...</div>;
  if (error) return <div className="shap-error">SHAP unavailable: {error}</div>;
  if (!data || !data.explainability?.shap_values) return null;

  const shapValues = data.explainability.shap_values;
  const features = Object.entries(shapValues)
    .map(([name, value]) => ({ name: formatFeatureName(name), value, raw: name }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  const maxVal = Math.max(...features.map((f) => Math.abs(f.value)), 0.1);

  return (
    <div className="shap-chart">
      <h4>SHAP Feature Importance</h4>
      <p className="shap-subtitle">
        How each feature contributes to the <strong>{data.risk_level}</strong> prediction
      </p>
      <div className="shap-bars">
        {features.map((f) => {
          const width = (Math.abs(f.value) / maxVal) * 100;
          const isPositive = f.value > 0;
          return (
            <div className="shap-row" key={f.raw}>
              <div className="shap-label">{f.name}</div>
              <div className="shap-bar-container">
                <div className="shap-bar-center" />
                {isPositive ? (
                  <div
                    className="shap-bar positive"
                    style={{ width: `${width / 2}%`, marginLeft: '50%' }}
                  />
                ) : (
                  <div
                    className="shap-bar negative"
                    style={{ width: `${width / 2}%`, marginRight: '50%', marginLeft: `${50 - width / 2}%` }}
                  />
                )}
              </div>
              <div className={`shap-value ${isPositive ? 'pos' : 'neg'}`}>
                {isPositive ? '+' : ''}{f.value.toFixed(3)}
              </div>
            </div>
          );
        })}
      </div>
      <div className="shap-legend">
        <span className="legend-item neg">← Decreases risk</span>
        <span className="legend-item pos">Increases risk →</span>
      </div>
      <div className="shap-meta">
        Method: {data.explainability.method} | Confidence: {(data.explainability.model_confidence * 100).toFixed(1)}%
      </div>
    </div>
  );
}

function formatFeatureName(name) {
  const map = {
    overall_attendance: 'Overall Attendance',
    recent_attendance: 'Recent Attendance',
    avg_score: 'Average Score',
    recent_score: 'Recent Score',
    failed_subjects: 'Failed Subjects',
  };
  return map[name] || name;
}

export default ShapChart;
