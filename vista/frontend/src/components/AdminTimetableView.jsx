import React, { useEffect, useState } from 'react';
import {
  getAdminTimetable,
  getClassTimetable,
  createTimetableSlot,
  updateTimetableSlot,
  deleteTimetableSlot,
  assignStudentBatch,
  getStudents,
  getAdminSubjects,
  getAdminUsers,
  getAdminClasses,
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

export default function AdminTimetableView({ selectedClassId: propClassId = '' }) {
  const [subTab, setSubTab] = useState('grid'); // 'grid' | 'slots' | 'batches'
  const [selectedClassId, setSelectedClassId] = useState(propClassId || 'class-aiml-4a');
  const [selectedDay, setSelectedDay] = useState('');

  const [classes, setClasses] = useState([]);
  const [slots, setSlots] = useState([]);
  const [students, setStudents] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  // Editing / adding slot
  const [editingSlot, setEditingSlot] = useState(null);
  const [isNewSlot, setIsNewSlot] = useState(false);
  const [form, setForm] = useState({
    class_section_id: 'class-aiml-4a',
    subject_id: '',
    teacher_id: '',
    day_of_week: 0,
    start_time: '09:00',
    end_time: '10:00',
    room: 'A-302',
    period_label: 'S1',
    slot_type: 'teaching',
    batch: '',
    is_unconfirmed: false,
  });

  // Keep in sync with parent prop if it changes
  useEffect(() => {
    if (propClassId) {
      setSelectedClassId(propClassId);
    }
  }, [propClassId]);

  const loadAll = () => {
    setLoading(true);
    setError('');
    const slotPromise = selectedClassId
      ? getClassTimetable(selectedClassId).then((res) => res.slots || [])
      : getAdminTimetable().then((res) => res.slots || []);

    Promise.all([
      slotPromise,
      getStudents(1, 100),
      getAdminSubjects(),
      getAdminUsers(),
      getAdminClasses(),
    ])
      .then(([slotList, studRes, subjRes, userRes, classRes]) => {
        setSlots(slotList);
        setStudents(studRes.students || []);
        setSubjects(subjRes.subjects || []);
        setTeachers((userRes.users || []).filter((u) => u.role === 'teacher'));
        const clList = classRes.class_sections || [];
        setClasses(clList);
        if (!selectedClassId && clList.length) {
          setSelectedClassId(clList[0].id);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadAll();
  }, [selectedClassId]);

  const handleOpenEdit = (slot) => {
    setIsNewSlot(false);
    setEditingSlot(slot);
    setForm({
      id: slot.id,
      class_section_id: slot.class_section_id || selectedClassId,
      subject_id: slot.subject_id || '',
      teacher_id: slot.teacher_id || '',
      day_of_week: slot.day_of_week,
      start_time: slot.start_time,
      end_time: slot.end_time,
      room: slot.room || 'A-302',
      period_label: slot.period_label || 'S1',
      slot_type: slot.slot_type || 'teaching',
      batch: slot.batch || '',
      is_unconfirmed: Boolean(slot.is_unconfirmed),
    });
  };

  const handleOpenAdd = () => {
    setIsNewSlot(true);
    setEditingSlot({});
    setForm({
      class_section_id: selectedClassId || (classes[0]?.id || 'class-aiml-4a'),
      subject_id: subjects[0]?.id || '',
      teacher_id: teachers[0]?.id || '',
      day_of_week: 0,
      start_time: '09:00',
      end_time: '10:00',
      room: 'A-302',
      period_label: 'S1',
      slot_type: 'teaching',
      batch: '',
      is_unconfirmed: false,
    });
  };

  const handleSaveSlot = async (e) => {
    e.preventDefault();
    setError('');
    setNotice('');
    try {
      const payload = {
        ...form,
        day_of_week: parseInt(form.day_of_week, 10),
        subject_id: form.subject_id || null,
        teacher_id: form.teacher_id || null,
        batch: form.batch || null,
      };

      if (isNewSlot) {
        await createTimetableSlot(payload);
        setNotice('Timetable slot created successfully!');
      } else {
        await updateTimetableSlot(editingSlot.id, payload);
        setNotice('Timetable slot updated successfully!');
      }

      setEditingSlot(null);
      loadAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteSlot = async (slotId) => {
    if (!window.confirm('Are you sure you want to delete/deactivate this timetable slot?')) return;
    setError('');
    setNotice('');
    try {
      await deleteTimetableSlot(slotId);
      setNotice('Slot removed successfully.');
      setEditingSlot(null);
      loadAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAssignBatch = async (studentId, batchValue) => {
    setError('');
    setNotice('');
    try {
      const newBatch = batchValue === '' ? null : batchValue;
      await assignStudentBatch(studentId, newBatch);
      setStudents((prev) =>
        prev.map((s) => (s.student_id === studentId ? { ...s, batch: newBatch } : s))
      );
      setNotice(`Updated batch for ${studentId} to ${newBatch || 'None'}`);
    } catch (err) {
      setError(err.message);
    }
  };

  const currentClassObj = classes.find((c) => c.id === selectedClassId || c.code === selectedClassId);
  const classStudents = students.filter(
    (s) => !selectedClassId || s.classroom_id === selectedClassId || s.class === currentClassObj?.name || s.class_code === currentClassObj?.code
  );

  // Build grid map: day -> period -> slots
  const slotMap = {};
  for (const s of slots) {
    const d = s.day_of_week;
    const p = s.period_label || 'S1';
    if (!slotMap[d]) slotMap[d] = {};
    if (!slotMap[d][p]) slotMap[d][p] = [];
    slotMap[d][p].push(s);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {notice && <p className="notice">{notice}</p>}
      {error && <p className="error">{error}</p>}

      {/* Class Selector & Sub Tab Nav Bar */}
      <div className="card" style={{ padding: '16px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 14 }}>
          <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, margin: 0, fontSize: 13, fontWeight: 700, color: '#102b2b' }}>
              Class Timetable:
              <select
                value={selectedClassId}
                onChange={(e) => setSelectedClassId(e.target.value)}
                style={{ width: 'auto', padding: '6px 14px', fontSize: 13, fontWeight: 600 }}
              >
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
                ))}
              </select>
            </label>

            <div className="tabs-nav" style={{ margin: 0, border: 'none' }}>
              <button
                className={subTab === 'grid' ? 'active' : ''}
                onClick={() => setSubTab('grid')}
                style={{ padding: '6px 12px', fontSize: 12 }}
              >
                📅 Weekly Class Grid
              </button>
              <button
                className={subTab === 'slots' ? 'active' : ''}
                onClick={() => setSubTab('slots')}
                style={{ padding: '6px 12px', fontSize: 12 }}
              >
                📋 Slot List ({slots.length})
              </button>
              <button
                className={subTab === 'batches' ? 'active' : ''}
                onClick={() => setSubTab('batches')}
                style={{ padding: '6px 12px', fontSize: 12 }}
              >
                🧪 Lab Batches ({classStudents.length})
              </button>
            </div>
          </div>

          <button className="primary" onClick={handleOpenAdd} style={{ fontSize: 13, padding: '8px 16px' }}>
            + Add Slot to {currentClassObj?.code || 'Class'}
          </button>
        </div>
      </div>

      {/* TAB 1: Weekly Class Grid (Interactive like Student/Teacher Timetable) */}
      {subTab === 'grid' && (
        <div className="card">
          <div className="card-title">
            <div>
              <p className="eyebrow">Interactive Weekly Schedule</p>
              <h2>{currentClassObj?.name || 'Class'} Timetable</h2>
              <p>Visual 5-day grid. Click "✏️ Edit" on any slot to reassign room, time, or faculty.</p>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <span className="slot-badge-pill pill-teaching">Lecture</span>
              <span className="slot-badge-pill pill-lab">Lab (Practical)</span>
              <span className="slot-badge-pill pill-free">Free Period</span>
            </div>
          </div>

          {loading ? (
            <p className="notice">Loading class timetable grid...</p>
          ) : (
            <div className="timetable-wrapper">
              <table className="timetable-grid-table">
                <thead>
                  <tr>
                    <th className="timetable-period-header">Period / Time</th>
                    {DAYS.map((d) => (
                      <th key={d.day}>{d.name}</th>
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
                                          {s.teacher_name ? <span>{s.teacher_name}</span> : <span style={{ color: '#94a3b8' }}>No teacher</span>}
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

                                        {!isFree && (
                                          <button
                                            className="edit-button"
                                            onClick={() => handleOpenEdit(s)}
                                            style={{ fontSize: 11, padding: '2px 6px' }}
                                            title="Edit slot details"
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
          )}
        </div>
      )}

      {/* TAB 2: Slot Master Table View */}
      {subTab === 'slots' && (
        <div className="card">
          <div className="card-title">
            <div>
              <p className="eyebrow">Slot List View</p>
              <h2>All Configured Slots ({slots.length})</h2>
              <p>Filter by day or click edit to modify timings, rooms, and assignments</p>
            </div>
            <select
              value={selectedDay}
              onChange={(e) => setSelectedDay(e.target.value)}
              style={{ width: 'auto', padding: '6px 12px', fontSize: 13 }}
            >
              <option value="">All Days (Mon - Fri)</option>
              {DAYS.map((d) => (
                <option key={d.day} value={d.day}>{d.name}</option>
              ))}
            </select>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Period</th>
                  <th>Time</th>
                  <th>Subject</th>
                  <th>Faculty</th>
                  <th>Room</th>
                  <th>Type</th>
                  <th>Batch</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {slots.map((s) => (
                  <tr key={s.id}>
                    <td><b>{DAYS[s.day_of_week]?.name || `Day ${s.day_of_week}`}</b></td>
                    <td><span className="mono">{s.period_label || '-'}</span></td>
                    <td className="mono">{s.start_time} - {s.end_time}</td>
                    <td>
                      <b>{s.subject_name}</b>
                      <small style={{ display: 'block', color: '#64748b' }}>{s.subject_code}</small>
                    </td>
                    <td>{s.teacher_name || <span style={{ color: '#94a3b8' }}>-</span>}</td>
                    <td>{s.room || '-'}</td>
                    <td>
                      <span className={`slot-badge-pill ${s.slot_type === 'lab' ? 'pill-lab' : s.slot_type === 'free' ? 'pill-free' : 'pill-teaching'}`}>
                        {s.slot_type}
                      </span>
                    </td>
                    <td>
                      {s.batch ? (
                        <span className="slot-badge-pill pill-lab">Batch {s.batch}</span>
                      ) : (
                        <span style={{ color: '#94a3b8' }}>All</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button
                          className="edit-button"
                          onClick={() => handleOpenEdit(s)}
                        >
                          Edit
                        </button>
                        <button
                          className="edit-button"
                          onClick={() => handleDeleteSlot(s.id)}
                          style={{ color: '#c6534b' }}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: Student Lab Batch Assignments */}
      {subTab === 'batches' && (
        <div className="card">
          <div className="card-title">
            <div>
              <p className="eyebrow">Practical Laboratories</p>
              <h2>Lab Batch Assignments: {currentClassObj?.name || 'Selected Class'}</h2>
              <p>Assign students to laboratory batches (B1, B2, B3) for split practical sessions</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>USN</th>
                  <th>Student Name</th>
                  <th>Class</th>
                  <th>Current Batch</th>
                  <th>Assign Batch</th>
                </tr>
              </thead>
              <tbody>
                {classStudents.map((s) => (
                  <tr key={s.student_id}>
                    <td className="mono"><b>{s.student_id}</b></td>
                    <td>{s.name}</td>
                    <td>{s.class || currentClassObj?.name || 'AIML'}</td>
                    <td>
                      {s.batch ? (
                        <span className="slot-badge-pill pill-lab">Batch {s.batch}</span>
                      ) : (
                        <span style={{ color: '#94a3b8', fontSize: 12 }}>Unassigned</span>
                      )}
                    </td>
                    <td>
                      <select
                        value={s.batch || ''}
                        onChange={(e) => handleAssignBatch(s.student_id, e.target.value)}
                        style={{ width: '130px', padding: '4px 8px', fontSize: 12 }}
                      >
                        <option value="">None</option>
                        <option value="B1">Batch B1</option>
                        <option value="B2">Batch B2</option>
                        <option value="B3">Batch B3</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add / Edit Slot Modal */}
      {editingSlot && (
        <div className="editor-overlay" role="presentation">
          <form className="card editor-form modal-large" onSubmit={handleSaveSlot}>
            <div className="card-title">
              <div>
                <p className="eyebrow">{isNewSlot ? 'New Timetable Slot' : 'Modify Slot'}</p>
                <h2>{isNewSlot ? 'Add Slot' : 'Edit Timetable Slot'}</h2>
              </div>
              <button type="button" className="ghost" onClick={() => setEditingSlot(null)}>
                Cancel
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <label>
                Class Section
                <select
                  value={form.class_section_id}
                  onChange={(e) => setForm({ ...form, class_section_id: e.target.value })}
                >
                  {classes.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.code})</option>
                  ))}
                </select>
              </label>

              <label>
                Day of Week
                <select
                  value={form.day_of_week}
                  onChange={(e) => setForm({ ...form, day_of_week: e.target.value })}
                >
                  {DAYS.map((d) => (
                    <option key={d.day} value={d.day}>{d.name}</option>
                  ))}
                </select>
              </label>

              <label>
                Period Label
                <select
                  value={form.period_label}
                  onChange={(e) => {
                    const pl = e.target.value;
                    const matched = PERIODS.find((p) => p.label === pl);
                    let st = '09:00', et = '10:00';
                    if (matched && matched.time) {
                      const parts = matched.time.split(' - ');
                      st = parts[0]; et = parts[1];
                    }
                    setForm({ ...form, period_label: pl, start_time: st, end_time: et });
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
                  placeholder="09:00"
                  value={form.start_time}
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                />
              </label>

              <label>
                End Time (HH:MM)
                <input
                  required
                  type="text"
                  pattern="^\d{2}:\d{2}$"
                  placeholder="10:00"
                  value={form.end_time}
                  onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                />
              </label>

              <label>
                Room
                <input
                  required
                  value={form.room}
                  placeholder="e.g. A-302 or CC-Lab"
                  onChange={(e) => setForm({ ...form, room: e.target.value })}
                />
              </label>

              <label>
                Subject
                <select
                  value={form.subject_id}
                  onChange={(e) => setForm({ ...form, subject_id: e.target.value })}
                >
                  <option value="">None (Free/Break)</option>
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                  ))}
                </select>
              </label>

              <label>
                Faculty
                <select
                  value={form.teacher_id}
                  onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}
                >
                  <option value="">None</option>
                  {teachers.map((t) => (
                    <option key={t.id} value={t.id}>{t.name} ({t.email})</option>
                  ))}
                </select>
              </label>

              <label>
                Slot Type
                <select
                  value={form.slot_type}
                  onChange={(e) => setForm({ ...form, slot_type: e.target.value })}
                >
                  <option value="teaching">Teaching (Lecture)</option>
                  <option value="lab">Lab (Practical)</option>
                  <option value="free">Free Period</option>
                </select>
              </label>

              <label>
                Lab Batch (Optional)
                <select
                  value={form.batch}
                  onChange={(e) => setForm({ ...form, batch: e.target.value })}
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
