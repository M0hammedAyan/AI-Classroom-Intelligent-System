import React, { useEffect, useState } from 'react';
import { getStudentTimetable } from '../api/client';

const DAYS = [
  { day: 0, name: 'Monday' },
  { day: 1, name: 'Tuesday' },
  { day: 2, name: 'Wednesday' },
  { day: 3, name: 'Thursday' },
  { day: 4, name: 'Friday' },
];

const PERIODS = [
  { label: 'S1', time: '09:00 - 10:00' },
  { label: 'S2', time: '10:00 - 11:00' },
  { label: 'S3', time: '11:15 - 12:15' },
  { label: 'S4', time: '12:15 - 13:15' },
  { label: 'Lunch', time: '13:15 - 14:00', isBreak: true },
  { label: 'S5', time: '14:00 - 15:00' },
  { label: 'S6', time: '15:00 - 16:00' },
  { label: 'S7', time: '16:00 - 17:00' },
];

export default function StudentTimetableView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    getStudentTimetable()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="card"><p className="notice">Loading weekly timetable...</p></div>;
  }

  if (error) {
    return <div className="card"><p className="error">Failed to load timetable: {error}</p></div>;
  }

  const { class_info = {}, server_time_ist = {}, current_slot_id, slots = [] } = data || {};
  const currentDow = server_time_ist.day_of_week;

  // Build a lookup: day_of_week -> period_label -> array of slots
  const slotMap = {};
  for (const s of slots) {
    const d = s.day_of_week;
    const p = s.period_label || 'S1';
    if (!slotMap[d]) slotMap[d] = {};
    if (!slotMap[d][p]) slotMap[d][p] = [];
    slotMap[d][p].push(s);
  }

  return (
    <div className="card">
      <div className="card-title">
        <div>
          <p className="eyebrow">Academic Schedule / 7th Semester</p>
          <h2>Weekly Timetable</h2>
          <p>
            {class_info.class_code || '4th Year AIML'}  ·  Student: <b>{class_info.name}</b> ({class_info.student_id})
            {class_info.batch ? (
              <span className="slot-badge-pill pill-lab" style={{ marginLeft: 8 }}>
                Batch {class_info.batch}
              </span>
            ) : (
              <span className="slot-badge-pill pill-free" style={{ marginLeft: 8 }}>
                No batch assigned
              </span>
            )}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span className="live-dot">● Server Clock (IST)</span>
          <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, marginTop: 4, color: '#526e64' }}>
            {server_time_ist.date}  ·  {server_time_ist.time}
          </div>
        </div>
      </div>

      <div className="timetable-wrapper">
        <table className="timetable-grid-table">
          <thead>
            <tr>
              <th className="timetable-period-header">Period / Time</th>
              {DAYS.map((d) => (
                <th
                  key={d.day}
                  className={d.day === currentDow ? 'today-header' : ''}
                >
                  {d.name} {d.day === currentDow && '● Today'}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PERIODS.map((p) => {
              if (p.isBreak) {
                return (
                  <tr key={p.label}>
                    <td className="timetable-period-header">
                      <b>{p.label}</b>
                      <small style={{ display: 'block', color: '#94a3b8' }}>{p.time}</small>
                    </td>
                    <td colSpan={5} style={{ textAlign: 'center', background: '#f8fafc', color: '#94a3b8', fontStyle: 'italic', padding: 8, borderRadius: 6, fontSize: 11 }}>
                      🍱 Lunch Break (13:15 - 14:00)
                    </td>
                  </tr>
                );
              }

              return (
                <tr key={p.label}>
                  <td className="timetable-period-header">
                    <b>{p.label}</b>
                    <small style={{ display: 'block', color: '#94a3b8' }}>{p.time}</small>
                  </td>
                  {DAYS.map((d) => {
                    const cellSlots = slotMap[d.day]?.[p.label] || [];
                    if (!cellSlots.length) {
                      return (
                        <td key={d.day}>
                          <div className="slot-cell-card slot-free">
                            <span>Free</span>
                          </div>
                        </td>
                      );
                    }

                    return (
                      <td key={d.day}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, height: '100%' }}>
                          {cellSlots.map((s) => {
                            const isCurrent = current_slot_id === s.id;
                            const isLab = s.slot_type === 'lab';
                            const isFree = s.slot_type === 'free';
                            const forOtherBatch = s.batch && class_info.batch && s.batch !== class_info.batch;

                            return (
                              <div
                                key={s.id}
                                className={`slot-cell-card ${isCurrent ? 'slot-active-now' : ''} ${isLab ? 'slot-lab' : ''} ${isFree ? 'slot-free' : ''} ${forOtherBatch ? 'slot-dimmed' : ''}`}
                              >
                                <div>
                                  <div className="slot-title">
                                    {s.subject_name || (isFree ? 'Free Period' : 'Class')}
                                  </div>
                                  <div className="slot-meta">
                                    {s.subject_code && <span>{s.subject_code} · </span>}
                                    {s.teacher_name && <span>{s.teacher_name}</span>}
                                  </div>
                                  {s.room && (
                                    <div className="slot-meta" style={{ marginTop: 2 }}>
                                      📍 Room: {s.room}
                                    </div>
                                  )}
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 6 }}>
                                  {isCurrent && (
                                    <span className="slot-badge-pill pill-active">
                                      NOW ACTIVE
                                    </span>
                                  )}
                                  {isLab && (
                                    <span className="slot-badge-pill pill-lab">
                                      LAB {s.batch ? `(${s.batch})` : ''}
                                    </span>
                                  )}
                                  {!isLab && !isFree && (
                                    <span className="slot-badge-pill pill-teaching">
                                      TEACHING
                                    </span>
                                  )}
                                  {s.is_unconfirmed && (
                                    <span className="slot-badge-pill" style={{ background: '#fef3c7', color: '#92400e' }}>
                                      UNCONFIRMED
                                    </span>
                                  )}
                                  {forOtherBatch && (
                                    <small style={{ color: '#94a3b8', fontSize: 10 }}>Other batch</small>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
