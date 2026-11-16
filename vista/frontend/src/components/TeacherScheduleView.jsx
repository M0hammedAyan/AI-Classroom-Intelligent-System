import React, { useEffect, useState } from 'react';
import {
  getTeacherTimetable,
  getClassTimetable,
  getAdminClasses,
  getTeacherSubjects,
  updateTimetableSlot,
  createTimetableSlot,
  deleteTimetableSlot,
} from '../api/client';

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

export default function TeacherScheduleView({ onTakeAttendanceForSlot }) {
  const [viewMode, setViewMode] = useState('mine'); // 'mine' | 'class'
  const [selectedClassId, setSelectedClassId] = useState('class-aiml-4a');
  const [classes, setClasses] = useState([]);
  const [assignedSubjects, setAssignedSubjects] = useState([]);

  const [data, setData] = useState(null);
  const [classData, setClassData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  // Editing state
  const [editingSlot, setEditingSlot] = useState(null);
  const [isNewSlot, setIsNewSlot] = useState(false);
  const [slotForm, setSlotForm] = useState({
    day_of_week: 0,
    period_label: 'S1',
    start_time: '09:00',
    end_time: '10:00',
    room: 'A-302',
    slot_type: 'teaching',
    batch: '',
    subject_id: '',
    class_section_id: 'class-aiml-4a',
  });

  const loadData = () => {
    setLoading(true);
    setError('');
    Promise.all([
      getTeacherTimetable(),
      getAdminClasses(),
      getTeacherSubjects().catch(() => ({ subjects: [] })),
    ])
      .then(([teacherData, classRes, subjRes]) => {
        setData(teacherData);
        const clList = classRes.class_sections || [];
        setClasses(clList);
        if (clList.length && !selectedClassId) {
          setSelectedClassId(clList[0].id);
        }
        setAssignedSubjects(subjRes.subjects || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (viewMode === 'class' && selectedClassId) {
      getClassTimetable(selectedClassId)
        .then((res) => setClassData(res))
        .catch((err) => setError(err.message));
    }
  }, [viewMode, selectedClassId]);

  const handleOpenEdit = (slot) => {
    setIsNewSlot(false);
    setEditingSlot(slot);
    setSlotForm({
      id: slot.id,
      day_of_week: slot.day_of_week,
      period_label: slot.period_label || 'S1',
      start_time: slot.start_time || '09:00',
      end_time: slot.end_time || '10:00',
      room: slot.room || 'A-302',
      slot_type: slot.slot_type || 'teaching',
      batch: slot.batch || '',
      subject_id: slot.subject_id || '',
      class_section_id: slot.class_section_id || 'class-aiml-4a',
    });
  };

  const handleOpenAdd = () => {
    setIsNewSlot(true);
    setEditingSlot({});
    setSlotForm({
      day_of_week: 0,
      period_label: 'S1',
      start_time: '09:00',
      end_time: '10:00',
      room: 'A-302',
      slot_type: 'teaching',
      batch: '',
      subject_id: assignedSubjects[0]?.subject_id || '',
      class_section_id: classes[0]?.id || 'class-aiml-4a',
    });
  };

  const handleSaveSlot = async (e) => {
    e.preventDefault();
    setError('');
    setNotice('');
    try {
      const payload = {
        class_section_id: slotForm.class_section_id,
        subject_id: slotForm.subject_id || null,
        teacher_id: data?.teacher_id,
        day_of_week: parseInt(slotForm.day_of_week, 10),
        start_time: slotForm.start_time,
        end_time: slotForm.end_time,
        room: slotForm.room,
        period_label: slotForm.period_label,
        slot_type: slotForm.slot_type,
        batch: slotForm.batch || null,
      };

      if (isNewSlot) {
        await createTimetableSlot(payload);
        setNotice('New teaching slot added to your schedule!');
      } else {
        await updateTimetableSlot(editingSlot.id, payload);
        setNotice('Timetable slot updated successfully!');
      }

      setEditingSlot(null);
      loadData();
      if (viewMode === 'class' && selectedClassId) {
        getClassTimetable(selectedClassId).then(setClassData);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteSlot = async (slotId) => {
    if (!window.confirm('Are you sure you want to delete this timetable slot?')) return;
    setError('');
    setNotice('');
    try {
      await deleteTimetableSlot(slotId);
      setNotice('Slot removed from schedule.');
      setEditingSlot(null);
      loadData();
      if (viewMode === 'class' && selectedClassId) {
        getClassTimetable(selectedClassId).then(setClassData);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="card"><p className="notice">Loading faculty schedule and timetables...</p></div>;
  }

  const { teacher_name, server_time_ist = {}, today_classes = [], weekly_slots = [] } = data || {};
  const currentDow = server_time_ist.day_of_week;

  // Active slots to display depending on viewMode
  const activeSlots = viewMode === 'mine' ? weekly_slots : (classData?.slots || []);

  // Build grid map: day -> period -> slots
  const slotMap = {};
  for (const s of activeSlots) {
    const d = s.day_of_week;
    const p = s.period_label || 'S1';
    if (!slotMap[d]) slotMap[d] = {};
    if (!slotMap[d][p]) slotMap[d][p] = [];
    slotMap[d][p].push(s);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {notice && <p className="notice">{notice}</p>}
      {error && <p className="error">{error}</p>}

      {/* View Switcher & Action Bar */}
      <div className="card" style={{ padding: '16px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14 }}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#49605b' }}>Timetable View:</span>
            <div className="tabs-nav" style={{ margin: 0, border: 'none' }}>
              <button
                className={viewMode === 'mine' ? 'active' : ''}
                onClick={() => setViewMode('mine')}
                style={{ padding: '6px 14px', fontSize: 13 }}
              >
                👤 My Faculty Timetable
              </button>
              <button
                className={viewMode === 'class' ? 'active' : ''}
                onClick={() => setViewMode('class')}
                style={{ padding: '6px 14px', fontSize: 13 }}
              >
                🏫 Class Timetable View
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            {viewMode === 'class' && (
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, margin: 0, fontSize: 13, fontWeight: 600 }}>
                Select Class:
                <select
                  value={selectedClassId}
                  onChange={(e) => setSelectedClassId(e.target.value)}
                  style={{ width: 'auto', padding: '6px 12px', fontSize: 13 }}
                >
                  {classes.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
                  ))}
                </select>
              </label>
            )}

            <button className="primary" onClick={handleOpenAdd} style={{ fontSize: 13, padding: '8px 16px' }}>
              + Add Teaching Slot
            </button>
          </div>
        </div>
      </div>

      {/* Today's Schedule Card (shown in My Faculty view) */}
      {viewMode === 'mine' && (
        <div className="card">
          <div className="card-title">
            <div>
              <p className="eyebrow">Real-Time Schedule</p>
              <h2>Today's Classes ({DAYS[server_time_ist.day_of_week]?.name || 'Today'})</h2>
              <p>Faculty: <b>{teacher_name}</b>  ·  IST Server Time: <b>{server_time_ist.time}</b> ({server_time_ist.date})</p>
            </div>
            <button className="secondary" onClick={loadData}>Refresh</button>
          </div>

          {today_classes.length === 0 ? (
            <p className="muted" style={{ padding: '16px 0' }}>No classes scheduled for you today.</p>
          ) : (
            <div className="today-schedule-grid">
              {today_classes.map((item, idx) => {
                const s = item.slot || {};
                const status = item.status;
                const isNow = status === 'now';
                const attTaken = item.attendance_taken;

                return (
                  <div key={s.id || idx} className={`today-card ${isNow ? 'card-now' : ''}`}>
                    <div>
                      <div className="today-card-header">
                        <span className="today-card-time">
                          {s.period_label ? `${s.period_label} · ` : ''}{s.start_time} - {s.end_time}
                        </span>
                        <span className={`status-pill ${status}`}>
                          {status === 'now' ? '● Active Now' : status === 'attendance_taken' ? '✓ Completed' : status}
                        </span>
                      </div>

                      <div style={{ fontSize: 16, fontWeight: 700, color: '#102b2b', marginBottom: 4 }}>
                        {s.subject_name}
                      </div>
                      <div style={{ fontSize: 12, color: '#64748b', lineHeight: 1.4 }}>
                        <div>Code: <b>{s.subject_code}</b></div>
                        <div>Class: <b>{s.class_name || s.class_code || '4th Year AIML'}</b></div>
                        {s.room && <div>Room: <b>{s.room}</b></div>}
                        {s.batch && <div>Batch: <b className="slot-badge-pill pill-lab">{s.batch}</b></div>}
                      </div>
                    </div>

                    <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
                      {item.take_attendance_enabled ? (
                        <button
                          className="primary"
                          style={{ flex: 1 }}
                          onClick={() => onTakeAttendanceForSlot && onTakeAttendanceForSlot(s)}
                        >
                          📸 Take Attendance Now
                        </button>
                      ) : attTaken ? (
                        <span style={{ fontSize: 12, color: '#15803d', fontWeight: 600, alignSelf: 'center' }}>
                          ✓ Attendance recorded
                        </span>
                      ) : (
                        <button
                          className="secondary"
                          style={{ flex: 1 }}
                          onClick={() => onTakeAttendanceForSlot && onTakeAttendanceForSlot(s)}
                        >
                          Mark Attendance
                        </button>
                      )}
                      <button
                        className="edit-button"
                        onClick={() => handleOpenEdit(s)}
                        title="Edit slot details"
                      >
                        ✏️ Edit
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Weekly Grid Timetable (Matching the Student Weekly Grid!) */}
      <div className="card">
        <div className="card-title">
          <div>
            <p className="eyebrow">
              {viewMode === 'mine' ? 'Faculty Master Schedule' : `Class Schedule / ${classData?.class_name || selectedClassId}`}
            </p>
            <h2>
              {viewMode === 'mine'
                ? `Weekly Timetable for ${teacher_name}`
                : `Timetable: ${classData?.class_name || 'Selected Class'} (${classData?.class_code || ''})`}
            </h2>
            <p>
              {viewMode === 'mine'
                ? 'Click "✏️ Edit" on any slot to update room, period, or notes.'
                : `All lectures and laboratory sessions scheduled for ${classData?.class_name || 'this class'}.`}
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
                              const isLab = s.slot_type === 'lab';
                              const isFree = s.slot_type === 'free';
                              const isMine = s.teacher_id === data?.teacher_id;

                              return (
                                <div
                                  key={s.id}
                                  className={`slot-cell-card ${isLab ? 'slot-lab' : ''} ${isFree ? 'slot-free' : ''}`}
                                >
                                  <div>
                                    <div className="slot-title">
                                      {s.subject_name || (isFree ? 'Free Period' : 'Class')}
                                    </div>
                                    <div className="slot-meta">
                                      {s.subject_code && <span>{s.subject_code} · </span>}
                                      {s.class_code && <span>{s.class_code} · </span>}
                                      {s.teacher_name && <span>{s.teacher_name}</span>}
                                    </div>
                                    {s.room && (
                                      <div className="slot-meta" style={{ marginTop: 2 }}>
                                        📍 Room: <b>{s.room}</b>
                                      </div>
                                    )}
                                  </div>

                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                                    <div style={{ display: 'flex', gap: 4 }}>
                                      {isLab && (
                                        <span className="slot-badge-pill pill-lab">
                                          LAB {s.batch ? `(${s.batch})` : ''}
                                        </span>
                                      )}
                                      {!isLab && !isFree && (
                                        <span className="slot-badge-pill pill-teaching">
                                          LECTURE
                                        </span>
                                      )}
                                    </div>

                                    {(isMine || data?.role === 'admin') && !isFree && (
                                      <button
                                        className="edit-button"
                                        onClick={() => handleOpenEdit(s)}
                                        style={{ fontSize: 11, padding: '2px 6px' }}
                                        title="Edit this slot"
                                      >
                                        ✏️ Edit
                                      </button>
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

      {/* Edit / Add Slot Modal */}
      {editingSlot && (
        <div className="editor-overlay" role="presentation">
          <form className="card editor-form modal-large" onSubmit={handleSaveSlot}>
            <div className="card-title">
              <div>
                <p className="eyebrow">{isNewSlot ? 'New Slot' : 'Modify Schedule'}</p>
                <h2>{isNewSlot ? 'Add Teaching Slot' : 'Edit Timetable Slot'}</h2>
              </div>
              <button type="button" className="ghost" onClick={() => setEditingSlot(null)}>
                Cancel
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <label>
                Day of Week
                <select
                  value={slotForm.day_of_week}
                  onChange={(e) => setSlotForm({ ...slotForm, day_of_week: e.target.value })}
                >
                  {DAYS.map((d) => (
                    <option key={d.day} value={d.day}>{d.name}</option>
                  ))}
                </select>
              </label>

              <label>
                Period Label
                <select
                  value={slotForm.period_label}
                  onChange={(e) => {
                    const pl = e.target.value;
                    const matched = PERIODS.find((p) => p.label === pl);
                    let st = '09:00', et = '10:00';
                    if (matched && matched.time) {
                      const parts = matched.time.split(' - ');
                      st = parts[0]; et = parts[1];
                    }
                    setSlotForm({ ...slotForm, period_label: pl, start_time: st, end_time: et });
                  }}
                >
                  {['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'].map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </label>

              <label>
                Start Time (HH:MM)
                <input
                  required
                  type="text"
                  pattern="^\d{2}:\d{2}$"
                  value={slotForm.start_time}
                  onChange={(e) => setSlotForm({ ...slotForm, start_time: e.target.value })}
                />
              </label>

              <label>
                End Time (HH:MM)
                <input
                  required
                  type="text"
                  pattern="^\d{2}:\d{2}$"
                  value={slotForm.end_time}
                  onChange={(e) => setSlotForm({ ...slotForm, end_time: e.target.value })}
                />
              </label>

              <label>
                Room
                <input
                  required
                  value={slotForm.room}
                  placeholder="e.g. A-302, CC-Lab 1"
                  onChange={(e) => setSlotForm({ ...slotForm, room: e.target.value })}
                />
              </label>

              <label>
                Slot Type
                <select
                  value={slotForm.slot_type}
                  onChange={(e) => setSlotForm({ ...slotForm, slot_type: e.target.value })}
                >
                  <option value="teaching">Teaching (Lecture)</option>
                  <option value="lab">Laboratory (Practical)</option>
                </select>
              </label>

              <label>
                Class Section
                <select
                  value={slotForm.class_section_id}
                  onChange={(e) => setSlotForm({ ...slotForm, class_section_id: e.target.value })}
                >
                  {classes.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
                  ))}
                </select>
              </label>

              <label>
                Lab Batch (Optional)
                <select
                  value={slotForm.batch}
                  onChange={(e) => setSlotForm({ ...slotForm, batch: e.target.value })}
                >
                  <option value="">All Batches / None</option>
                  <option value="B1">Batch B1</option>
                  <option value="B2">Batch B2</option>
                  <option value="B3">Batch B3</option>
                </select>
              </label>
            </div>

            <div style={{ marginTop: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {!isNewSlot ? (
                <button
                  type="button"
                  className="edit-button"
                  style={{ color: '#c6534b' }}
                  onClick={() => handleDeleteSlot(editingSlot.id)}
                >
                  Delete Slot
                </button>
              ) : <div />}

              <div style={{ display: 'flex', gap: 10 }}>
                <button type="button" className="secondary" onClick={() => setEditingSlot(null)}>
                  Cancel
                </button>
                <button type="submit" className="primary">
                  {isNewSlot ? 'Create Slot' : 'Save Changes'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
