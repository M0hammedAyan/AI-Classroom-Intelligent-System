import { useState, useEffect } from 'react';
import { getAttendanceStats } from '../api/client';
import './Charts.css';

/**
 * Attendance Trend Chart — simple bar chart showing weekly attendance %
 */
export function AttendanceTrend({ classroomId = 'CSE-3A' }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAttendanceStats(classroomId)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [classroomId]);

  if (loading) return <div className="chart-loading">Loading trend...</div>;
  if (!data || !data.weekly_summary || data.weekly_summary.length === 0) {
    return <div className="chart-empty">No attendance data for trend</div>;
  }

  const weeks = data.weekly_summary;
  const maxPct = 100;

  return (
    <div className="chart-container">
      <h4>Weekly Attendance Trend</h4>
      <div className="bar-chart">
        {weeks.map((w) => (
          <div className="bar-column" key={w.week}>
            <div className="bar-wrapper">
              <div
                className="bar-fill"
                style={{ height: `${(w.avg_attendance_pct / maxPct) * 100}%` }}
                title={`${w.avg_attendance_pct}%`}
              />
            </div>
            <div className="bar-label">{w.week.split('-W')[1] ? `W${w.week.split('-W')[1]}` : w.week}</div>
            <div className="bar-value">{w.avg_attendance_pct}%</div>
          </div>
        ))}
      </div>
      <div className="chart-footer">
        Overall: <strong>{data.overall_attendance_pct}%</strong> · {data.total_sessions} sessions · {data.total_students} students
      </div>
    </div>
  );
}

/**
 * Risk Distribution — pie/donut chart showing LOW/MEDIUM/HIGH counts
 */
export function RiskDistribution({ flags = [] }) {
  const high = flags.filter((f) => f.risk_level === 'high').length;
  const medium = flags.filter((f) => f.risk_level === 'medium').length;
  const low = flags.filter((f) => f.risk_level === 'low').length;
  const total = flags.length || 1;

  const segments = [
    { label: 'High', count: high, color: '#dc2626', pct: (high / total) * 100 },
    { label: 'Medium', count: medium, color: '#d97706', pct: (medium / total) * 100 },
    { label: 'Low', count: low, color: '#16a34a', pct: (low / total) * 100 },
  ];

  // Create conic-gradient for pie chart
  let cumulative = 0;
  const gradientParts = segments.map((s) => {
    const start = cumulative;
    cumulative += s.pct;
    return `${s.color} ${start}% ${cumulative}%`;
  });
  const gradient = `conic-gradient(${gradientParts.join(', ')})`;

  return (
    <div className="chart-container">
      <h4>Risk Distribution</h4>
      <div className="pie-chart-wrapper">
        <div className="pie-chart" style={{ background: total > 0 ? gradient : '#e5e7eb' }}>
          <div className="pie-center">
            <span className="pie-total">{flags.length}</span>
            <span className="pie-label">students</span>
          </div>
        </div>
        <div className="pie-legend">
          {segments.map((s) => (
            <div className="legend-item" key={s.label}>
              <span className="legend-dot" style={{ background: s.color }} />
              <span className="legend-text">{s.label}: {s.count} ({s.pct.toFixed(0)}%)</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
