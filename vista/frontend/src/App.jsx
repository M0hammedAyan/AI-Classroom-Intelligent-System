import { useEffect, useMemo, useRef, useState } from 'react';
import {
  login,
  getStudents,
  getStudentAcademicRecord,
  getStudentImages,
  getTeacherSubjects,
  getAdminUsers,
  createAdminUser,
  updateAdminUser,
  deleteAdminUser,
  updateStudent,
  deleteStudent,
  createStudent,
  getAdminSubjects,
  createSubject,
  updateSubject,
  deleteSubject,
  assignTeacher,
  enrollStudent,
  getAdminClasses,
  createAdminClass,
  getStudentDashboard,
  getStudentAttendance,
  getStudentScores,
  getStudentSubjectDetail,
  getStudentMarks,
  getStudentAttendanceHistory,
  markAttendanceBatch,
  getAttendanceLog,
  patchAttendance,
  createManualAttendance,
  addScore,
  getNotifications,
  getUnreadNotificationsCount,
  createNotification,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
  coachChat,
  getCoachHistory,
  clearCoachHistory,
  getCoachSummary,
} from './api/client';

const SUBJECTS = [
  ['Deep Learning', '22AIU701', 'Mrs. Rajeshwari'],
  ['Generative AI', '22AIU702', 'Dr. Ajay Prakash B V'],
  ['Data Engineering and Analytics', '22AIT703', 'Mr. Ganesh H J'],
  ['Data Security and Privacy', '22AIT704C', 'Mr. Bharath V S'],
  ['Major Project Phase-II', '22AIP706', 'Mr. Ganesh H J'],
];

const ROSTER = `
SHRUJAN P|1DA22AI044
ABHAY B SUVARNA|1DA23AI001
AKARSH KIRAN GOWDA|1DA23AI002
AKASH KUMAR SINGH|1DA23AI003
ANUJ PATEL|1DA23AI004
ANUJ KUMAR|1DA23AI005
ANUSHKA M R|1DA23AI006
ANVESH B R|1DA23AI007
APPAJIGOUDA|1DA23AI008
ARYAN RAJ SINGH|1DA23AI009
ATHISH SRINIVAS|1DA23AI010
AYUSH A WASTER|1DA23AI011
BABU|1DA23AI012
DEEKSHTHA S GOWDA|1DA23AI013
DHANA LAKSHMI D S|1DA23AI014
DHRUV SINGH BISHT|1DA23AI015
DIVYA N|1DA23AI016
GAURAV H M|1DA23AI017
HARSH SINGH|1DA23AI018
HARSHAVARDHAN K|1DA23AI019
HARSHITH H V|1DA23AI020
JAVERIA FATHIMA|1DA23AI021
JEEVAN D|1DA23AI022
KUNAL RAJ|1DA23AI024
MALLIKARJUNA C|1DA23AI025
MAYUR A|1DA23AI026
MOUNESH S D|1DA23AI027
MUKESH N A|1DA23AI029
NAGARJUN|1DA23AI030
NAVANEETH K S|1DA23AI031
NISARGA D S|1DA23AI032
PALLAVI DEVI Y|1DA23AI033
POOJA G|1DA23AI034
PRAVINA GOWDA H N|1DA23AI035
PRAVEEN KUMAR N R|1DA23AI036
PRIYANSHU YADAV|1DA23AI037
RISHABH IRANNA PATTANSHET|1DA23AI038
SAGAR B R|1DA23AI039
SAGAR H M|1DA23AI040
SAHAJ DUBEY|1DA23AI041
SAHEEL PRADHAN|1DA23AI042
SANJANA C H|1DA23AI043
SANJANA K U|1DA23AI044
SHREYAS G R|1DA23AI046
SHREYAS K T|1DA23AI047
SNEHA KUMARI|1DA23AI048
SUCHITH CHANDRA|1DA23AI049
SUJAL AGRAHARI|1DA23AI050
SUMA|1DA23AI051
SUMIT KUMAR|1DA23AI052
TARUN G|1DA23AI054
TEJAS M NAIDU|1DA23AI055
THEJAS A G|1DA23AI056
VARSHINI K T|1DA23AI057
VEDA K VAJAYALAD|1DA23AI058
VEMUGANTI SRIRAG|1DA23AI059
YASHWANTH R|1DA23AI060
AVSHUMALEE BHAT MARAKINI|1DA23AI061
NAMITHA L|1DA23AI062
AKSHITHA G R|1DA24AI400
MAHESH REDDY GODEPALLY|1DA24AI401
MC CHETHAN PATIL|1DA24AI402
MOHAMMED AYAN|1DA24AI403
VIGNESH V|1DA24AI404
VINAY V S|1DA24AI405
`
  .split('\n')
  .map((row) => {
    const [name, usn] = row.split('|');
    return { name, usn, student_id: usn };
  });

const today = () => new Date().toISOString().slice(0, 10);

function Login({ onLogin }) {
  const [email, setEmail] = useState('rajeshwari@vista.local');
  const [password, setPassword] = useState('rajeshwari123');
  const [error, setError] = useState('');
  const submit = async (event) => {
    event.preventDefault();
    setError('');
    try {
      const session = await login(email, password);
      localStorage.setItem('vista_auth', JSON.stringify(session));
      onLogin(session);
    } catch (err) { setError(err.message); }
  };
  return <main className="login-screen">
    <section className="login-panel"><div className="brand-mark">V</div><p className="eyebrow">VISTA / ATTENDANCE</p>
      <h1>Attendance,<br /><em>without the guesswork.</em></h1>
      <p className="login-copy">Recognise the room in seconds, then keep the teacher in control when AI needs a human correction.</p>
      <div className="login-points"><span>● Live camera capture</span><span>● Upload fallback</span><span>● Manual overrides</span></div>
    </section>
    <form className="login-card" onSubmit={submit}><p className="eyebrow">Teacher workspace</p><h2>Sign in to continue</h2>
      <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required /></label>
      <label>Password<input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required /></label>
      {error && <p className="error">{error}</p>}<button className="primary wide">Open workspace</button>
      <small>Demo: rajeshwari@vista.local / rajeshwari123</small>
    </form>
  </main>;
}


function NotificationCenter({ user, onOpenCompose }) {
  const [open, setOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchUnread = () => {
    getUnreadNotificationsCount()
      .then((data) => setUnreadCount(data.unread_count || 0))
      .catch(() => {});
  };

  const fetchList = () => {
    setLoading(true);
    getNotifications(1, 20)
      .then((data) => {
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchUnread();
    const interval = setInterval(fetchUnread, 45000);
    return () => clearInterval(interval);
  }, []);

  const handleToggle = () => {
    if (!open) {
      fetchList();
    }
    setOpen(!open);
  };

  const handleMarkRead = async (id, e) => {
    e.stopPropagation();
    try {
      await markNotificationRead(id);
      setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {}
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      fetchUnread();
    } catch {}
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        type="button"
        className="notification-bell-btn"
        onClick={handleToggle}
        title="Notifications"
        aria-label="Notifications"
      >
        🔔
        {unreadCount > 0 && <span className="unread-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>}
      </button>

      {open && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>Notifications {unreadCount > 0 && `(${unreadCount} unread)`}</h3>
            <div style={{ display: 'flex', gap: 6 }}>
              {unreadCount > 0 && (
                <button type="button" className="ghost" style={{ fontSize: 11, padding: '3px 6px' }} onClick={handleMarkAllRead}>
                  Mark all read
                </button>
              )}
              {user?.role !== 'student' && onOpenCompose && (
                <button type="button" className="primary" style={{ fontSize: 11, padding: '3px 8px' }} onClick={() => { setOpen(false); onOpenCompose(); }}>
                  + Post
                </button>
              )}
              <button type="button" className="ghost" style={{ fontSize: 11, padding: '3px 6px' }} onClick={() => setOpen(false)}>
                ✕
              </button>
            </div>
          </div>
          <div className="notification-list">
            {loading && <p style={{ padding: 14, fontSize: 12, color: '#6d827e', margin: 0 }}>Loading notifications...</p>}
            {!loading && notifications.length === 0 && (
              <p style={{ padding: 20, fontSize: 12, color: '#8ca19a', textAlign: 'center', margin: 0 }}>
                No notifications yet.
              </p>
            )}
            {notifications.map((item) => (
              <div
                key={item.id}
                className={`notification-item ${!item.is_read ? 'unread' : ''}`}
                onClick={(e) => !item.is_read && handleMarkRead(item.id, e)}
              >
                <div className="notif-title">
                  <span>{item.title}</span>
                  {item.priority === 'important' && <span className="badge important">Urgent</span>}
                </div>
                <div className="notif-body">{item.body}</div>
                <div className="notif-meta">
                  <span>
                    By {item.sender_role} · {new Date(item.created_at).toLocaleDateString()}
                    {item.subject_id && ` · ${item.subject_id}`}
                  </span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    {!item.is_read && (
                      <span style={{ color: '#389260', cursor: 'pointer', fontWeight: 600 }} onClick={(e) => handleMarkRead(item.id, e)}>
                        Mark read
                      </span>
                    )}
                    {(user?.role === 'admin' || user?.id === item.sender_id) && (
                      <span style={{ color: '#dc2626', cursor: 'pointer' }} onClick={(e) => handleDelete(item.id, e)}>
                        Delete
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ComposeNotificationModal({ isOpen, onClose, user, assignedSubjects, onPosted }) {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [audienceType, setAudienceType] = useState(user?.role === 'admin' ? 'all' : 'subject');
  const [targetSubject, setTargetSubject] = useState(assignedSubjects?.[0]?.code || assignedSubjects?.[0]?.[1] || '');
  const [priority, setPriority] = useState('normal');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !body.trim()) {
      setError('Title and body are required.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      await createNotification({
        title: title.trim(),
        body: body.trim(),
        audience_type: audienceType,
        subject_id: audienceType === 'subject' ? targetSubject : null,
        class_id: audienceType === 'class' ? 'class-aiml-4a' : null,
        priority: priority,
      });
      onClose();
      if (onPosted) onPosted();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="editor-overlay" role="presentation">
      <div className="card editor-form">
        <div className="card-title">
          <div>
            <p className="eyebrow">Announcements / {user?.role?.toUpperCase()}</p>
            <h2>Create Notification</h2>
            <p>{user?.role === 'admin' ? 'Broadcast to institution or target class/subject.' : 'Send notification to your assigned class or subject.'}</p>
          </div>
          <button type="button" className="ghost" onClick={onClose}>Close</button>
        </div>

        {error && <p className="error">{error}</p>}

        <form onSubmit={handleSubmit}>
          <label>
            Audience
            <select value={audienceType} onChange={(e) => setAudienceType(e.target.value)}>
              {user?.role === 'admin' && <option value="all">Everyone (All Teachers & Students)</option>}
              <option value="subject">Specific Subject</option>
              <option value="class">Class (4th Year AIML)</option>
            </select>
          </label>

          {audienceType === 'subject' && (
            <label>
              Subject
              <select value={targetSubject} onChange={(e) => setTargetSubject(e.target.value)}>
                {(assignedSubjects || []).map((s) => (
                  <option key={s.code || s[1]} value={s.code || s[1]}>
                    {s.name || s[0]} ({s.code || s[1]})
                  </option>
                ))}
              </select>
            </label>
          )}

          <label>
            Priority
            <select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="normal">Normal</option>
              <option value="important">Important / Urgent</option>
            </select>
          </label>

          <label>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} placeholder="e.g. CIE 2 Schedule Update" required />
          </label>

          <label>
            Message Body
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={4}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid #d5e2dc', fontFamily: 'inherit', fontSize: 13 }}
              placeholder="Enter announcement details..."
              required
            />
          </label>

          <div className="editor-actions">
            <button type="button" className="secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="primary" disabled={busy}>
              {busy ? 'Posting...' : 'Send Notification'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function CoachTipCard({ onOpenCoach }) {
  const [tip, setTip] = useState(null);

  useEffect(() => {
    getCoachSummary()
      .then((data) => setTip(data.tip))
      .catch(() => {});
  }, []);

  if (!tip) return null;

  return (
    <div className="coach-tip-card">
      <div className="coach-tip-content">
        <span className="coach-tip-icon">🤖</span>
        <div className="coach-tip-text">
          <strong>AI Study Coach Tip</strong>
          <p>{tip}</p>
        </div>
      </div>
      <button type="button" className="primary" style={{ whiteSpace: 'nowrap', fontSize: 12, padding: '8px 14px' }} onClick={onOpenCoach}>
        Ask Coach →
      </button>
    </div>
  );
}

function CoachChatDrawer({ isOpen, onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const quickPrompts = [
    'Can I miss next class?',
    'How many classes to reach 85%?',
    'What do I need in CIE 2 to avoid CIE 3?',
    'Am I eligible for CIE 3?',
    'What is my risk level?',
  ];

  useEffect(() => {
    if (isOpen) {
      getCoachHistory(20)
        .then((data) => {
          if (data.messages && data.messages.length > 0) {
            setMessages(data.messages);
          } else {
            setMessages([
              {
                role: 'assistant',
                content: "Hello! I am your AI Study Coach. I can help you calculate class attendance buffers, CIE requirements, and track academic risk based on your official college records. How can I help you today?",
              },
            ]);
          }
        })
        .catch(() => {});
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, busy]);

  if (!isOpen) return null;

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || busy) return;

    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setBusy(true);
    setError('');

    try {
      const res = await coachChat(text);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }]);
    } catch (err) {
      setError(err.message || 'Failed to get response from coach.');
    } finally {
      setBusy(false);
    }
  };

  const handleClear = async () => {
    try {
      await clearCoachHistory();
      setMessages([
        {
          role: 'assistant',
          content: "Chat history cleared. What would you like to ask?",
        },
      ]);
    } catch {}
  };

  return (
    <div className="coach-drawer">
      <div className="coach-header">
        <div>
          <h3>🤖 AI Study Coach</h3>
          <small>Grounded in your official records</small>
        </div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <button type="button" className="ghost" style={{ color: '#9cb8ac', fontSize: 11 }} onClick={handleClear} title="Clear history">
            Clear
          </button>
          <button type="button" className="ghost" style={{ color: '#e7f3ed', fontSize: 16 }} onClick={onClose}>
            ✕
          </button>
        </div>
      </div>

      <div className="coach-pills">
        {quickPrompts.map((p, idx) => (
          <button key={idx} type="button" className="coach-pill" onClick={() => handleSend(p)}>
            {p}
          </button>
        ))}
      </div>

      <div className="coach-messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`coach-bubble-msg ${m.role}`}>
            {m.content}
          </div>
        ))}
        {busy && (
          <div className="coach-bubble-msg assistant" style={{ fontStyle: 'italic', color: '#6d827e' }}>
            Thinking...
          </div>
        )}
        {error && <div className="error" style={{ fontSize: 11, padding: '6px 10px' }}>{error}</div>}
        <div ref={messagesEndRef} />
      </div>

      <form
        className="coach-input-bar"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your attendance or CIE..."
          disabled={busy}
        />
        <button type="submit" className="primary" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

function StudentSubjectModal({ subjectId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!subjectId) return;
    setLoading(true);
    getStudentSubjectDetail(subjectId)
      .then(setDetail)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [subjectId]);

  return (
    <div className="editor-overlay" role="presentation">
      <div className="card editor-form modal-large">
        <div className="card-title">
          <div>
            <p className="eyebrow">Subject Detail / Read-Only</p>
            <h2>{detail ? detail.subject.name : 'Loading subject...'}</h2>
            {detail && <p>{detail.subject.code} · {detail.subject.credits} Credits · Faculty: {detail.subject.faculty}</p>}
          </div>
          <button type="button" className="ghost" onClick={onClose}>Close</button>
        </div>

        {loading && <p className="notice">Loading subject details...</p>}
        {error && <p className="error">{error}</p>}

        {detail && (
          <>
            <div className="marks-summary-box" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
              <div>
                <span>CIE 1 (Max 25)</span>
                <strong>{detail.marks.cie1 !== null ? `${detail.marks.cie1} / 25` : '—'}</strong>
                <span className={`badge ${detail.marks.cie1_status === 'absent' ? 'cie-absent' : 'cie-scored'}`}>
                  {detail.marks.cie1_status === 'absent' ? 'Absent' : detail.marks.cie1 !== null ? 'Scored' : 'Pending'}
                </span>
              </div>
              <div>
                <span>CIE 2 (Max 25)</span>
                <strong>{detail.marks.cie2 !== null ? `${detail.marks.cie2} / 25` : '—'}</strong>
                <span className={`badge ${detail.marks.cie2_status === 'absent' ? 'cie-absent' : 'cie-scored'}`}>
                  {detail.marks.cie2_status === 'absent' ? 'Absent' : detail.marks.cie2 !== null ? 'Scored' : 'Pending'}
                </span>
              </div>
              <div>
                <span>CIE 3 (Re-attempt)</span>
                <strong>{detail.marks.cie3 !== null ? `${detail.marks.cie3} / 25` : '—'}</strong>
                <span className={`badge ${
                  detail.marks.cie3_status === 'scored' ? 'cie-scored' :
                  detail.marks.cie3_status === 'absent' ? 'cie-absent' :
                  detail.marks.cie3_status === 'eligible_not_taken' ? 'cie-eligible' : 'cie-ineligible'
                }`}>
                  {detail.marks.cie3_status === 'scored' ? 'Scored' :
                   detail.marks.cie3_status === 'absent' ? 'Absent' :
                   detail.marks.cie3_status === 'eligible_not_taken' ? 'Eligible (Not Written)' : 'Not Eligible'}
                </span>
              </div>
              <div>
                <span>Final CIE</span>
                <strong className={detail.marks.final_cie_50 !== null && detail.marks.final_cie_50 >= 40 ? 'green' : ''}>
                  {detail.marks.final_cie_25 !== null ? `${detail.marks.final_cie_25}/25` : '—'}
                </strong>
                <small style={{ display: 'block', fontSize: 11, color: '#6d827e' }}>
                  {detail.marks.final_cie_50 !== null ? `(${detail.marks.final_cie_50} / 50)` : ''}
                </small>
              </div>
            </div>

            {detail.marks.cie3_reason && (
              <p className="notice" style={{ fontSize: 12, margin: '8px 0 16px', padding: '8px 12px' }}>
                💡 {detail.marks.cie3_reason}
              </p>
            )}

            <div className="detail-chart" style={{ borderTop: 'none', paddingTop: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <p className="eyebrow" style={{ margin: 0 }}>Attendance Record</p>
                <span className="mono" style={{ fontSize: 12 }}>
                  <b>{detail.summary.sessions_attended}</b> of <b>{detail.summary.total_sessions}</b> sessions ({detail.summary.attendance_pct ?? 0}%)
                </span>
              </div>
              <div className="history-list" style={{ maxHeight: 240 }}>
                {detail.attendance.length ? (
                  detail.attendance.map((item, idx) => (
                    <div className="history-row" key={`${item.date}-${idx}`}>
                      <span>
                        {item.date}
                        <span className={`badge ${item.source || 'seed'}`}>
                          {item.source === 'face' ? 'Face' : item.source === 'manual' ? 'Manual' : 'Seed'}
                        </span>
                        {item.confidence && item.source === 'face' && (
                          <small style={{ display: 'inline', marginLeft: 6 }}>
                            ({Math.round(item.confidence * 100)}% match)
                          </small>
                        )}
                        {item.note && <small style={{ display: 'block', color: '#8ca19a' }}>{item.note}</small>}
                      </span>
                      <b className={`status ${item.status}`}>{item.status}</b>
                    </div>
                  ))
                ) : (
                  <p className="muted">No attendance recorded for this subject.</p>
                )}
              </div>
            </div>

            <p className="muted" style={{ fontSize: 11, marginTop: 14, textAlign: 'center' }}>
              The student portal is strictly read-only. For attendance corrections or marks queries, please contact your faculty.
            </p>
          </>
        )}
      </div>
    </div>
  );
}

function StudentWorkspace({ auth, onLogout }) {
  const [dashboard, setDashboard] = useState(null);
  const [attendance, setAttendance] = useState(null);
  const [scores, setScores] = useState(null);
  const [error, setError] = useState('');
  const [selectedSubjectId, setSelectedSubjectId] = useState(null);
  const [showCoach, setShowCoach] = useState(false);

  useEffect(() => {
    Promise.all([getStudentDashboard(), getStudentAttendance(), getStudentScores()])
      .then(([overview, attendanceData, scoresData]) => {
        setDashboard(overview);
        setAttendance(attendanceData);
        setScores(scoresData);
      })
      .catch((err) => setError(err.message));
  }, []);

  const attendanceDisplay =
    dashboard?.attendance_pct !== null && dashboard?.attendance_pct !== undefined
      ? `${dashboard.attendance_pct}%`
      : 'No sessions yet';

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark small">V</span>
          <span>VISTA <b>Student portal</b></span>
        </div>
        <div className="top-actions">
          <NotificationCenter user={auth} />
          <span>{auth.name}</span>
          <button className="ghost" onClick={onLogout}>Sign out</button>
        </div>
      </header>
      <main className="workspace">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Student portal / read only</p>
            <h1>My academic view</h1>
            <p>View your attendance and marks across all 4th Year AIML subjects. Click any subject for complete history.</p>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
        <CoachTipCard onOpenCoach={() => setShowCoach(true)} />
        <section className="stats">
          <div>
            <span>Attendance</span>
            <strong className="green">{attendanceDisplay}</strong>
            <small>personal attendance</small>
          </div>
          <div>
            <span>Average marks</span>
            <strong>{dashboard?.avg_score ?? '—'}%</strong>
            <small>across CIE assessments</small>
          </div>
          <div>
            <span>Class</span>
            <strong className="class-value">{dashboard?.class || '4th Year AIML'}</strong>
            <small>{dashboard?.usn || ''}</small>
          </div>
        </section>
        <div className="content-grid">
          <section className="card">
            <div className="card-title">
              <div>
                <p className="eyebrow">Attendance</p>
                <h2>By subject</h2>
                <p>Click any subject for date-wise attendance and CIE marks drill-down</p>
              </div>
              <span className="read-only">Read only</span>
            </div>
            <div className="subject-list">
              {(attendance?.by_subject || []).map((item) => (
                <div
                  className="subject-row clickable-row"
                  key={item.subject_id}
                  onClick={() => setSelectedSubjectId(item.subject_id)}
                  title="Click to view full attendance history & CIE marks"
                >
                  <span>
                    {item.subject_name}
                    <small>{item.subject_code} · Click to view →</small>
                  </span>
                  <b>
                    {item.attendance_pct !== null ? `${item.attendance_pct}%` : 'No sessions'} · {item.sessions_attended}/{item.total_sessions}
                  </b>
                </div>
              ))}
            </div>
          </section>
          <section className="card">
            <div className="card-title">
              <div>
                <p className="eyebrow">Marks</p>
                <h2>My results</h2>
                <p>CIE 1 and CIE 2 results (each out of 25)</p>
              </div>
              <span className="read-only">Read only</span>
            </div>
            <div className="subject-list">
              {(scores?.by_subject || []).map((item) => (
                <div
                  className="subject-row clickable-row"
                  key={item.subject}
                  onClick={() => {
                    const match = (attendance?.by_subject || []).find((s) => s.subject_name === item.subject || s.subject_code === item.subject);
                    if (match) setSelectedSubjectId(match.subject_id);
                  }}
                  title="Click to view marks detail"
                >
                  <span>
                    {item.subject}
                    <small>{item.assessments} CIE assessments</small>
                  </span>
                  <b>{item.average_pct}%</b>
                </div>
              ))}
            </div>
          </section>
        </div>

        {selectedSubjectId && (
          <StudentSubjectModal
            subjectId={selectedSubjectId}
            onClose={() => setSelectedSubjectId(null)}
          />
        )}

        <button
          type="button"
          className="coach-floating-btn"
          onClick={() => setShowCoach(true)}
          title="Open AI Study Coach"
        >
          💬 AI Study Coach
        </button>

        <CoachChatDrawer isOpen={showCoach} onClose={() => setShowCoach(false)} />
      </main>
    </div>
  );
}

function ManualEntryModal({ isOpen, onClose, userRole, assignedSubjects, allStudents, onDone }) {
  const [tab, setTab] = useState('attendance');
  const [search, setSearch] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [subject, setSubject] = useState(assignedSubjects[0]?.code || assignedSubjects[0]?.[1] || '22AIU701');
  const [attDate, setAttDate] = useState(today());
  const [status, setStatus] = useState('present');
  const [attReason, setAttReason] = useState('');
  const [assessmentType, setAssessmentType] = useState('CIE 1');
  const [marksStatus, setMarksStatus] = useState('scored');
  const [scoreVal, setScoreVal] = useState('');
  const [marksDate, setMarksDate] = useState(today());
  const [marksReason, setMarksReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [studentHistory, setStudentHistory] = useState({ attendance: [], marks: [] });

  const studentList = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return allStudents.slice(0, 8);
    return allStudents.filter(
      (s) =>
        (s.name || '').toLowerCase().includes(q) ||
        (s.usn || s.student_id || '').toLowerCase().includes(q)
    ).slice(0, 15);
  }, [allStudents, search]);

  const loadStudentRecords = (stud, subj) => {
    if (!stud) return;
    Promise.all([
      getStudentAttendanceHistory(stud.student_id, subj).catch(() => ({ records: [] })),
      getStudentMarks(stud.student_id, subj).catch(() => ({ scores: [] })),
    ]).then(([attRes, marksRes]) => {
      setStudentHistory({
        attendance: attRes.records || [],
        marks: marksRes.scores || [],
      });
    });
  };

  const handleSelectStudent = (s) => {
    setSelectedStudent(s);
    setError('');
    setNotice('');
    loadStudentRecords(s, subject);
  };

  const handleSubjectChange = (sCode) => {
    setSubject(sCode);
    if (selectedStudent) {
      loadStudentRecords(selectedStudent, sCode);
    }
  };

  const submitAttendance = async (e) => {
    e.preventDefault();
    if (!selectedStudent) {
      setError('Please select a student first.');
      return;
    }
    if (!attReason.trim()) {
      setError('A mandatory reason is required for manual attendance entry.');
      return;
    }
    if (attDate > today()) {
      setError('Cannot record attendance for future dates.');
      return;
    }
    if (userRole !== 'admin' && attDate < '2026-08-03') {
      setError('Teachers cannot record attendance before semester start (03-Aug-2026).');
      return;
    }

    setBusy(true);
    setError('');
    setNotice('');
    try {
      await createManualAttendance(
        selectedStudent.student_id,
        'class-aiml-4a',
        attDate,
        subject,
        status,
        attReason.trim()
      );
      setNotice(`Attendance recorded for ${selectedStudent.name} (${status.toUpperCase()}) with source='manual'.`);
      setAttReason('');
      loadStudentRecords(selectedStudent, subject);
      if (onDone) onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const submitMarks = async (e) => {
    e.preventDefault();
    if (!selectedStudent) {
      setError('Please select a student first.');
      return;
    }
    if (!marksReason.trim()) {
      setError('A mandatory reason is required for marks entry.');
      return;
    }
    let numScore = null;
    if (marksStatus === 'scored') {
      numScore = parseFloat(scoreVal);
      if (isNaN(numScore) || numScore < 0 || numScore > 25) {
        setError('CIE score must be a number between 0 and 25.');
        return;
      }
    }
    if (marksDate > today()) {
      setError('Cannot record marks for future dates.');
      return;
    }
    if (userRole !== 'admin' && marksDate < '2026-08-03') {
      setError('Teachers cannot record marks before semester start (03-Aug-2026).');
      return;
    }

    setBusy(true);
    setError('');
    setNotice('');
    try {
      await addScore(
        selectedStudent.student_id,
        subject,
        numScore,
        25,
        marksDate,
        assessmentType,
        marksReason.trim(),
        marksStatus
      );
      setNotice(`Recorded ${assessmentType} marks (${numScore}/25) for ${selectedStudent.name} with source='manual'.`);
      setScoreVal('');
      setMarksReason('');
      loadStudentRecords(selectedStudent, subject);
      if (onDone) onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="editor-overlay" role="presentation">
      <div className="card editor-form modal-large">
        <div className="card-title">
          <div>
            <p className="eyebrow">Search & Manual Entry / {userRole.toUpperCase()}</p>
            <h2>Find Student & Record Data</h2>
            <p>Search student by name or USN, then enter attendance or CIE marks with audit reason.</p>
          </div>
          <button type="button" className="ghost" onClick={onClose}>Close</button>
        </div>

        <div className="tabs-nav">
          <button type="button" className={tab === 'attendance' ? 'active' : ''} onClick={() => setTab('attendance')}>
            1. Attendance Entry
          </button>
          <button type="button" className={tab === 'marks' ? 'active' : ''} onClick={() => setTab('marks')}>
            2. CIE Marks Entry
          </button>
        </div>

        {error && <p className="error">{error}</p>}
        {notice && <p className="notice">{notice}</p>}

        <label className="search-field">
          Find student (Name or USN)
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search USN (e.g. 1DA24AI403) or Name (e.g. Mohammed Ayyan)..."
          />
        </label>

        {(!selectedStudent || search) && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14, maxHeight: 110, overflowY: 'auto' }}>
            {studentList.map((s) => (
              <button
                key={s.student_id}
                type="button"
                className={`class-chip ${selectedStudent?.student_id === s.student_id ? 'selected' : ''}`}
                style={{ padding: '6px 10px', fontSize: 12 }}
                onClick={() => handleSelectStudent(s)}
              >
                {s.name} <small>{s.usn || s.student_id}</small>
              </button>
            ))}
          </div>
        )}

        {selectedStudent && (
          <div style={{ padding: '10px 14px', background: '#f4f8f5', borderRadius: 8, marginBottom: 14 }}>
            <b>Selected:</b> {selectedStudent.name} <span className="mono">({selectedStudent.usn || selectedStudent.student_id})</span>
            <small style={{ display: 'block', color: '#6d827e' }}>Class: 4th Year AIML</small>
          </div>
        )}

        <label>
          Subject
          <select value={subject} onChange={(e) => handleSubjectChange(e.target.value)}>
            {assignedSubjects.map((s) => {
              const code = s.code || s.subject_code || s[1];
              const name = s.name || s.subject_name || s[0];
              return <option key={code} value={code}>{name} · {code}</option>;
            })}
          </select>
        </label>

        {tab === 'attendance' ? (
          <form onSubmit={submitAttendance}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <label>
                Session Date
                <input
                  type="date"
                  required
                  max={today()}
                  min={userRole === 'admin' ? undefined : '2026-08-03'}
                  value={attDate}
                  onChange={(e) => setAttDate(e.target.value)}
                />
              </label>
              <label>
                Status
                <select value={status} onChange={(e) => setStatus(e.target.value)}>
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                </select>
              </label>
            </div>
            <label>
              Reason / Justification <small style={{ color: '#c6534b' }}>* Mandatory</small>
              <input
                required
                value={attReason}
                onChange={(e) => setAttReason(e.target.value)}
                placeholder="e.g. Approved medical leave, OD event, Face camera missed"
              />
            </label>
            <button className="primary wide" type="submit" disabled={busy || !selectedStudent}>
              {busy ? 'Saving...' : 'Record Attendance (Manual Override)'}
            </button>
          </form>
        ) : (
          <form onSubmit={submitMarks}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 10 }}>
              <label>
                Assessment
                <select value={assessmentType} onChange={(e) => setAssessmentType(e.target.value)}>
                  <option value="CIE 1">CIE 1</option>
                  <option value="CIE 2">CIE 2</option>
                  <option value="CIE 3">CIE 3 (Re-attempt)</option>
                </select>
              </label>
              <label>
                Status
                <select value={marksStatus} onChange={(e) => setMarksStatus(e.target.value)}>
                  <option value="scored">Scored</option>
                  <option value="absent">Absent</option>
                </select>
              </label>
              <label>
                Marks (Max 25)
                <input
                  type="number"
                  required={marksStatus === 'scored'}
                  disabled={marksStatus === 'absent'}
                  min="0"
                  max="25"
                  step="0.5"
                  value={marksStatus === 'absent' ? '' : scoreVal}
                  onChange={(e) => setScoreVal(e.target.value)}
                  placeholder={marksStatus === 'absent' ? 'Absent (No mark)' : '0 to 25'}
                />
              </label>
              <label>
                Date
                <input
                  type="date"
                  required
                  max={today()}
                  min={userRole === 'admin' ? undefined : '2026-08-03'}
                  value={marksDate}
                  onChange={(e) => setMarksDate(e.target.value)}
                />
              </label>
            </div>
            <label>
              Reason / Note <small style={{ color: '#c6534b' }}>* Mandatory</small>
              <input
                required
                value={marksReason}
                onChange={(e) => setMarksReason(e.target.value)}
                placeholder="e.g. Retest score, Verified Bluebook entry, Revaluation"
              />
            </label>
            <button className="primary wide" type="submit" disabled={busy || !selectedStudent}>
              {busy ? 'Saving...' : 'Record Marks (Manual)'}
            </button>
          </form>
        )}

        {selectedStudent && (
          <div style={{ marginTop: 20, paddingTop: 14, borderTop: '1px solid #e4ece8' }}>
            <p className="eyebrow">Existing Records for {subject}</p>
            {tab === 'attendance' ? (
              <div className="history-list" style={{ maxHeight: 150 }}>
                {studentHistory.attendance.length ? (
                  studentHistory.attendance.slice(0, 10).map((r, i) => (
                    <div className="history-row" key={`${r.date}-${i}`}>
                      <span>
                        {r.date}
                        <span className={`badge ${r.source || 'seed'}`}>{r.source || 'seed'}</span>
                        {r.note && <small style={{ display: 'inline', marginLeft: 6 }}>{r.note}</small>}
                      </span>
                      <b className={`status ${r.status}`}>{r.status}</b>
                    </div>
                  ))
                ) : (
                  <p className="muted" style={{ fontSize: 12 }}>No prior attendance records found for this subject.</p>
                )}
              </div>
            ) : (
              <div className="history-list" style={{ maxHeight: 150 }}>
                {studentHistory.marks.length ? (
                  studentHistory.marks.map((m, i) => (
                    <div className="history-row" key={`${m.date}-${i}`}>
                      <span>
                        {m.assessment_type || 'CIE'} · {m.date}
                        <span className={`badge ${m.source || 'seed'}`}>{m.source || 'seed'}</span>
                      </span>
                      <b>{m.score} / {m.max_score}</b>
                    </div>
                  ))
                ) : (
                  <p className="muted" style={{ fontSize: 12 }}>No prior marks recorded for this subject.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StudentDetail({ studentId, onBack, auth }) {
  const [record, setRecord] = useState(null);
  const [subjectId, setSubjectId] = useState('all');
  const [showMarks, setShowMarks] = useState(false);
  const [faceImages, setFaceImages] = useState(null);
  const [form, setForm] = useState({ subject: '', score: '', maxScore: '25', assessmentType: 'CIE 1', reason: '', date: today() });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => getStudentAcademicRecord(studentId).then(setRecord).catch((err) => setError(err.message));
  useEffect(() => { load(); }, [studentId]);

  useEffect(() => {
    getStudentImages(studentId)
      .then((data) => setFaceImages(data))
      .catch(() => setFaceImages(null));
  }, [studentId]);

  if (!record) return <div className="app-shell"><main className="workspace"><p className="notice">Loading student profile...</p>{error && <p className="error">{error}</p>}</main></div>;

  const selectedSubject = record.subjects.find((s) => s.id === subjectId);
  const attendance = subjectId === 'all' ? record.attendance : record.attendance.filter((item) => item.subject_id === subjectId);
  const subjectMarks = selectedSubject
    ? record.marks.filter((item) => item.subject === selectedSubject.name || item.subject === selectedSubject.code || item.subject === selectedSubject.id)
    : record.marks;
  const present = attendance.filter((item) => item.status === 'present').length;
  const attendanceRate = attendance.length ? Math.round((present / attendance.length) * 100) : 0;
  const chartAttendance = attendance.slice(0, 12).reverse();
  const chartMarks = subjectMarks.slice(0, 8).reverse();

  const saveMark = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      await addScore(studentId, form.subject, parseFloat(form.score), parseFloat(form.maxScore), form.date, form.assessmentType, form.reason || 'Manual entry by staff');
      setForm({ ...form, score: '', reason: '' });
      setShowMarks(false);
      await load();
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  };

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><span className="brand-mark small">V</span><span>VISTA <b>Student profile</b></span></div>
      <div className="top-actions"><span>{auth.name}</span><button className="ghost" onClick={onBack}>Back</button></div>
    </header>
    <main className="workspace">
      <div className="page-heading">
        <div>
          <p className="eyebrow">{record.scope} / academic record</p>
          <h1>{record.student.name}</h1>
          <p>{record.student.student_id} · {record.student.class || '4th Year AIML'}</p>
        </div>
        {auth.role !== 'student' && <button className="primary" onClick={() => setShowMarks(true)}>Add marks</button>}
      </div>
      {error && <p className="error">{error}</p>}
      <section className="stats">
        <div>
          <span>Attendance</span>
          <strong className="green">{record.student.attendance_pct ?? attendanceRate}%</strong>
          <small>{present} present sessions in this view</small>
        </div>
        <div>
          <span>Average marks</span>
          <strong>{record.student.average_score ?? '—'}%</strong>
          <small>{record.marks.length} assessments</small>
        </div>
        <div>
          <span>Average risk</span>
          <strong className={`risk-value ${record.risk?.level || 'unknown'}`}>{record.risk?.level || 'Not computed'}</strong>
          <small>{record.risk?.confidence || 'No risk assessment'}</small>
        </div>
      </section>
      {faceImages && faceImages.total > 0 && (
        <section className="card" style={{ marginBottom: '1rem' }}>
          <div className="card-title"><div><p className="eyebrow">Face enrollment</p><h2>Enrollment photos</h2></div></div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            {faceImages.images.map((img, i) => (
              <div key={i} style={{ width: '120px', textAlign: 'center' }}>
                <img
                  src={`data:image/jpeg;base64,${img.data}`}
                  alt={`Enrollment ${i + 1}`}
                  style={{ width: '100%', borderRadius: '8px', border: '1px solid var(--border, #333)' }}
                />
                <small style={{ display: 'block', marginTop: '0.25rem', opacity: 0.6 }}>{img.source}</small>
              </div>
            ))}
          </div>
          <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.7 }}>
            {faceImages.has_embedding ? `✅ Face embedding active (enrolled ${faceImages.enrolled_at ? faceImages.enrolled_at.slice(0, 10) : 'previously'})` : '⚠️ No face embedding — not enrolled for face recognition.'}
          </p>
        </section>
      )}
      {faceImages && faceImages.total === 0 && (
        <section className="card" style={{ marginBottom: '1rem' }}>
          <div className="card-title"><div><p className="eyebrow">Face enrollment</p><h2>No enrollment photos</h2></div></div>
          <p style={{ opacity: 0.6 }}>No face images found on disk for {studentId}. Upload enrollment photos via the Admin → Students → Enrol face button.</p>
        </section>
      )}
      <section className="detail-grid">
        <div className="card">
          <div className="card-title"><div><p className="eyebrow">Subject view</p><h2>{selectedSubject ? selectedSubject.name : 'All subjects'}</h2></div></div>
          <div className="subject-tabs">
            <button className={subjectId === 'all' ? 'active' : ''} onClick={() => setSubjectId('all')}>All subjects</button>
            {record.subjects.map((s) => <button key={s.id} className={subjectId === s.id ? 'active' : ''} onClick={() => setSubjectId(s.id)}>{s.code}</button>)}
          </div>
          <div className="detail-chart">
            <p className="eyebrow">Attendance history</p>
            {chartAttendance.length ? <div className="bar-chart">{chartAttendance.map((item) => <div className={`bar ${item.status}`} key={item.id} title={`${item.date}: ${item.status}`}><span /></div>)}</div> : <p className="muted">No attendance history for this subject yet.</p>}
          </div>
          <div className="history-list">
            {attendance.map((item) => (
              <div className="history-row" key={item.id}>
                <span>
                  {item.date}
                  <span className={`badge ${item.source || 'seed'}`}>{item.source || 'seed'}</span>
                  <small>{item.subject_name}{item.is_manual_override ? ' · manual override' : ''}</small>
                </span>
                <b className={`status ${item.status}`}>{item.status}</b>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="card-title"><div><p className="eyebrow">Marks trend</p><h2>{selectedSubject ? selectedSubject.code : 'All assessments'}</h2></div></div>
          {chartMarks.length ? <div className="bar-chart marks-chart">{chartMarks.map((item) => <div className="bar mark" key={item.id} style={{ height: `${Math.max(8, item.percentage)}%` }} title={`${item.date}: ${item.percentage}%`}><span /></div>)}</div> : <p className="muted">No marks entered yet.</p>}
          <div className="history-list">
            {subjectMarks.map((item) => (
              <div className="history-row" key={item.id}>
                <span>
                  {item.subject}
                  <span className={`badge ${item.source || 'seed'}`}>{item.source || 'seed'}</span>
                  <small>{item.date} · {item.assessment_type || 'CIE'}</small>
                </span>
                <b>{item.score}/{item.max_score} · {item.percentage}%</b>
              </div>
            ))}
          </div>
        </div>
      </section>
      {showMarks && auth.role !== 'student' && (
        <div className="editor-overlay" role="presentation">
          <form className="card editor-form" onSubmit={saveMark}>
            <div className="card-title">
              <div><p className="eyebrow">Academic entry</p><h2>Add marks</h2></div>
              <button type="button" className="ghost" onClick={() => setShowMarks(false)}>Cancel</button>
            </div>
            <label>Subject
              <select required value={form.subject} onChange={(event) => setForm({ ...form, subject: event.target.value })}>
                <option value="">Select subject</option>
                {record.subjects.map((s) => <option key={s.id} value={s.code}>{s.name} · {s.code}</option>)}
              </select>
            </label>
            <label>Assessment
              <select value={form.assessmentType} onChange={(e) => setForm({ ...form, assessmentType: e.target.value })}>
                <option value="CIE 1">CIE 1</option>
                <option value="CIE 2">CIE 2</option>
              </select>
            </label>
            <label>Marks obtained (Max 25)
              <input required type="number" min="0" max="25" step="0.5" value={form.score} onChange={(event) => setForm({ ...form, score: event.target.value })} />
            </label>
            <label>Date
              <input required type="date" max={today()} value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} />
            </label>
            <label>Reason / Note
              <input required value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} placeholder="e.g. Regular CIE evaluation" />
            </label>
            <button className="primary wide" disabled={saving}>{saving ? 'Saving...' : 'Save marks'}</button>
          </form>
        </div>
      )}
    </main>
  </div>;
}

function AdminWorkspace({ auth, onLogout }) {
  const [users, setUsers] = useState([]);
  const [showComposeNotif, setShowComposeNotif] = useState(false);
  const [students, setStudents] = useState(ROSTER);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [error, setError] = useState('');
  const [editor, setEditor] = useState(null);
  const [editorError, setEditorError] = useState('');
  const [teacherSearch, setTeacherSearch] = useState('');
  const [subjectSearch, setSubjectSearch] = useState('');
  const [studentSearch, setStudentSearch] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showManualModal, setShowManualModal] = useState(false);

  const reload = () =>
    Promise.all([getAdminUsers(), getStudents(1, 100), getAdminSubjects(), getAdminClasses()])
      .then(([userData, studentData, subjectData, classData]) => {
        setUsers(userData.users || []);
        if (studentData.students?.length) setStudents(studentData.students);
        setSubjects(subjectData.subjects || []);
        setClasses(classData.class_sections || []);
      })
      .catch((err) => setError(err.message));

  useEffect(() => { reload(); }, []);

  useEffect(() => {
    const openProfile = (event) => {
      const cell = event.target.closest('.roster-card tbody tr td:first-child');
      if (!cell) return;
      const student = students.find((item) => item.name === cell.innerText.trim());
      if (student) setSelectedStudent(student.student_id);
    };
    document.addEventListener('click', openProfile);
    return () => document.removeEventListener('click', openProfile);
  }, [students]);

  const openEditor = (type, item = {}) => {
    setEditorError('');
    setEditor({
      type,
      id: item.id || item.student_id || null,
      name: item.name || '',
      email: item.email || '',
      password: '',
      code: item.code || '',
      usn: item.usn || item.student_id || '',
      teacherId: '',
      year: item.year || '',
      division: item.division || '',
    });
  };

  const saveStudent = async (enrollAfterSave) => {
    try {
      const student = editor.id
        ? await updateStudent(editor.id, { name: editor.name, usn: editor.usn })
        : await createStudent({ name: editor.name, usn: editor.usn, class_code: 'AIML-4A' });
      setEditor(null);
      setEditorError('');
      setError('');
      await reload();
      if (enrollAfterSave) await enroll(student);
    } catch (err) { setEditorError(err.message); }
  };

  const saveEditor = async (event) => {
    event.preventDefault();
    try {
      if (editor.type === 'teacher') {
        if (editor.id) await updateAdminUser(editor.id, { name: editor.name, email: editor.email, ...(editor.password ? { password: editor.password } : {}) });
        else await createAdminUser({ name: editor.name, email: editor.email, password: editor.password, role: 'teacher' });
      } else if (editor.type === 'student') {
        await saveStudent(false);
        return;
      } else if (editor.type === 'class') {
        await createAdminClass({
          department_id: 'dept-aiml',
          name: `AIML ${editor.year} Year ${editor.division}`,
          code: `AIML-${editor.year[0]}${editor.division}`,
          semester: editor.year === '1st' ? '2' : editor.year === '2nd' ? '4' : editor.year === '3rd' ? '6' : '7',
        });
      } else {
        let subjectItem = editor.id
          ? await updateSubject(editor.id, { name: editor.name, code: editor.code })
          : await createSubject({ name: editor.name, code: editor.code, department_id: 'dept-aiml', semester: '7' });
        if (editor.teacherId) await assignTeacher(editor.teacherId, subjectItem.id, 'class-aiml-4a');
      }
      setEditor(null);
      setEditorError('');
      setError('');
      await reload();
    } catch (err) { setEditorError(err.message); }
  };

  const removeTeacher = async (user) => {
    if (!window.confirm(`Delete ${user.name}?`)) return;
    try { await deleteAdminUser(user.id); reload(); } catch (err) { setError(err.message); }
  };

  const removeSubject = async (subj) => {
    if (!window.confirm(`Delete ${subj.name}?`)) return;
    try { await deleteSubject(subj.id); reload(); } catch (err) { setError(err.message); }
  };

  const enroll = async (student) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/png';
    input.multiple = true;
    input.onchange = async () => {
      const files = Array.from(input.files || []).slice(0, 5);
      if (!files.length) return;
      try {
        const images = await Promise.all(
          files.map((file) =>
            new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result.split(',')[1]);
              reader.onerror = reject;
              reader.readAsDataURL(file);
            })
          )
        );
        await enrollStudent(student.student_id, images);
        setError('');
        window.alert(`${student.name} face enrollment completed.`);
        reload();
      } catch (err) { setError(err.message); }
    };
    input.click();
  };

  const removeStudent = async (student) => {
    if (!window.confirm(`Delete ${student.name}? Face enrollment/embedding will be retained for this USN.`)) return;
    try { await deleteStudent(student.student_id); reload(); } catch (err) { setError(err.message); }
  };

  const teachers = users.filter((u) => u.role === 'teacher' && `${u.name} ${u.email} ${u.id}`.toLowerCase().includes(teacherSearch.trim().toLowerCase()));
  const filteredSubjects = subjects.filter((s) => `${s.name} ${s.code} ${s.id}`.toLowerCase().includes(subjectSearch.trim().toLowerCase()));
  const filteredStudents = students.filter(
    (s) =>
      (!selectedClass || s.class === selectedClass || s.class_code === selectedClass || s.classroom_id === selectedClass) &&
      `${s.name} ${s.usn || s.student_id} ${s.student_id}`.toLowerCase().includes(studentSearch.trim().toLowerCase())
  );

  if (selectedStudent) return <StudentDetail auth={auth} studentId={selectedStudent} onBack={() => setSelectedStudent(null)} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark small">V</span>
          <span>VISTA <b>Admin / HOD</b></span>
        </div>
        <div className="top-actions">
          <NotificationCenter user={auth} onOpenCompose={() => setShowComposeNotif(true)} />
          <span>{auth.name}</span>
          <button type="button" className="ghost" onClick={onLogout}>Sign out</button>
        </div>
      </header>
      <main className="workspace">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Administrator / full access</p>
            <h1>Academic control centre</h1>
            <p>Manage teachers, students, attendance, marks, subjects, and face enrollment.</p>
          </div>
          <button className="secondary" onClick={() => setShowManualModal(true)}>
            Manual Entry / Find Student
          </button>
        </div>

        {error && !editor && <p className="error">{error}</p>}

        {editor && (
          <div className="editor-overlay" role="presentation">
            <form className="card editor-form" onSubmit={saveEditor}>
              <div className="card-title">
                <div><p className="eyebrow">Edit workspace</p><h2>{editor.id ? 'Edit' : 'Add'} {editor.type}</h2></div>
                <button type="button" className="ghost" onClick={() => { setEditor(null); setEditorError(''); }}>Cancel</button>
              </div>
              {editorError && <p className="error editor-error">{editorError}</p>}
              <label>Name<input required value={editor.name} onChange={(e) => setEditor({ ...editor, name: e.target.value })} /></label>
              {editor.type === 'teacher' && (
                <>
                  <label>Email<input required type="email" value={editor.email} onChange={(e) => setEditor({ ...editor, email: e.target.value })} /></label>
                  <label>{editor.id ? 'New password (optional)' : 'Password'}
                    <input required={!editor.id} type="password" value={editor.password} onChange={(e) => setEditor({ ...editor, password: e.target.value })} />
                  </label>
                </>
              )}
              {editor.type === 'student' && <label>USN<input required value={editor.usn} onChange={(e) => setEditor({ ...editor, usn: e.target.value })} /></label>}
              {editor.type === 'subject' && (
                <>
                  <label>Subject code<input required value={editor.code} onChange={(e) => setEditor({ ...editor, code: e.target.value })} /></label>
                  <label>Assign teacher
                    <select value={editor.teacherId} onChange={(e) => setEditor({ ...editor, teacherId: e.target.value })}>
                      <option value="">Select a teacher</option>
                      {users.filter((u) => u.role === 'teacher').map((u) => <option key={u.id} value={u.id}>{u.name} · {u.email}</option>)}
                    </select>
                  </label>
                </>
              )}
              {editor.type === 'class' && (
                <>
                  <label>Year
                    <select required value={editor.year} onChange={(e) => setEditor({ ...editor, year: e.target.value })}>
                      <option value="">Select year</option>
                      <option value="1st">1st</option>
                      <option value="2nd">2nd</option>
                      <option value="3rd">3rd</option>
                      <option value="4th">4th</option>
                    </select>
                  </label>
                  <label>Division
                    <select required value={editor.division} onChange={(e) => setEditor({ ...editor, division: e.target.value })}>
                      <option value="">Select division</option>
                      {['A', 'B', 'C', 'D', 'E', 'F'].map((div) => <option key={div} value={div}>{div}</option>)}
                    </select>
                  </label>
                </>
              )}
              {editor.type === 'student' && !editor.id ? (
                <div className="editor-actions">
                  <button type="button" className="secondary" onClick={() => saveStudent(true)}>Enroll face</button>
                  <button className="primary" type="submit">Skip / Save</button>
                </div>
              ) : (
                <button className="primary" type="submit">Save {editor.type}</button>
              )}
            </form>
          </div>
        )}

        <section className="stats">
          <div><span>Students</span><strong>{students.length}</strong><small>view and manage roster</small></div>
          <div><span>Teachers</span><strong>{users.filter((u) => u.role === 'teacher').length}</strong><small>subject instructors</small></div>
          <div><span>Subjects</span><strong>{subjects.length || SUBJECTS.length}</strong><small>configured curriculum</small></div>
        </section>

        <section className="card class-manager">
          <div className="card-title">
            <div><p className="eyebrow">Class organization</p><h2>Classes and divisions</h2></div>
            <button className="primary" onClick={() => openEditor('class')}>Add class</button>
          </div>
          <div className="class-list">
            {classes.map((cs) => (
              <button
                type="button"
                className={`class-chip ${selectedClass === cs.code ? 'selected' : ''}`}
                key={cs.id}
                onClick={() => setSelectedClass(selectedClass === cs.code ? '' : cs.code)}
              >
                {cs.name}<small>{cs.code}</small>
              </button>
            ))}
          </div>
        </section>

        <div className="content-grid">
          <section className="card">
            <div className="card-title">
              <div><p className="eyebrow">People</p><h2>Teachers</h2></div>
              <button className="primary" onClick={() => openEditor('teacher')}>Add teacher</button>
            </div>
            <label className="search-field">
              Search teacher by name, email, or ID
              <input value={teacherSearch} onChange={(e) => setTeacherSearch(e.target.value)} placeholder="e.g. Rajeshwari or teacher ID" />
            </label>
            <div className="subject-list">
              {teachers.map((u) => (
                <div className="subject-row" key={u.id}>
                  <span>{u.name}<small>{u.email}</small></span>
                  <b>
                    <button className="edit-button" onClick={() => openEditor('teacher', u)}>Edit</button>
                    <button className="edit-button" onClick={() => removeTeacher(u)}>Delete</button>
                  </b>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-title">
              <div><p className="eyebrow">Curriculum</p><h2>Subjects</h2></div>
              <button className="primary" onClick={() => openEditor('subject')}>Add subject</button>
            </div>
            <label className="search-field">
              Search subject by name, code, or ID
              <input value={subjectSearch} onChange={(e) => setSubjectSearch(e.target.value)} placeholder="e.g. Deep Learning or 22AIU701" />
            </label>
            <div className="subject-list">
              {filteredSubjects.map((s) => (
                <div className="subject-row" key={s.id}>
                  <span>{s.name}<small>{s.code}</small></span>
                  <b>
                    <button className="edit-button" onClick={() => openEditor('subject', s)}>Edit</button>
                    <button className="edit-button" onClick={() => removeSubject(s)}>Delete</button>
                  </b>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="card roster-card">
          <div className="card-title">
            <div><p className="eyebrow">Students</p><h2>All students</h2></div>
            <button className="primary" onClick={() => openEditor('student')}>Add student</button>
          </div>
          <label className="class-filter">
            Show students from
            <select value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)}>
              <option value="">All classes</option>
              {classes.map((cs) => <option key={cs.id} value={cs.code}>{cs.name}</option>)}
            </select>
          </label>
          <label className="search-field">
            Search student by name or USN
            <input value={studentSearch} onChange={(e) => setStudentSearch(e.target.value)} placeholder="e.g. Aditya or 1DA22AI002" />
          </label>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>USN</th><th>Class</th><th>Face enrollment</th><th>Actions</th></tr></thead>
              <tbody>
                {filteredStudents.map((s) => (
                  <tr key={s.student_id}>
                    <td><b>{s.name}</b></td>
                    <td className="mono">{s.usn || s.student_id}</td>
                    <td>{s.class || '4th Year AIML'}</td>
                    <td><button className="edit-button" onClick={() => enroll(s)}>{s.enrolled_at ? 'Re-enrol face' : 'Enrol face'}</button></td>
                    <td>
                      <button className="edit-button" onClick={() => openEditor('student', s)}>Edit</button>
                      <button className="edit-button" onClick={() => removeStudent(s)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <ManualEntryModal
          isOpen={showManualModal}
          onClose={() => setShowManualModal(false)}
          userRole="admin"
          assignedSubjects={subjects.length ? subjects : SUBJECTS.map((s) => ({ name: s[0], code: s[1] }))}
          allStudents={students}
          onDone={reload}
        />

        <ComposeNotificationModal
          isOpen={showComposeNotif}
          onClose={() => setShowComposeNotif(false)}
          user={auth}
          assignedSubjects={subjects.length ? subjects : SUBJECTS.map((s) => ({ name: s[0], code: s[1] }))}
        />
      </main>
    </div>
  );
}

function AttendanceWorkspace({ auth, onLogout }) {
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents] = useState(ROSTER);
  const [subject, setSubject] = useState(SUBJECTS[0][1]);
  const [classroom, setClassroom] = useState('class-aiml-4a');
  const [date, setDate] = useState(today());
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState('');
  const [records, setRecords] = useState([]);
  const [detectionResults, setDetectionResults] = useState([]);
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showManualModal, setShowManualModal] = useState(false);
  const [showComposeNotif, setShowComposeNotif] = useState(false);

  useEffect(() => {
    if (auth.role === 'teacher') {
      getTeacherSubjects()
        .then((data) => {
          const assigned = data.subjects || [];
          setAssignments(assigned);
          if (assigned.length) {
            setSubject(assigned[0].subject_code);
            setClassroom(assigned[0].class_code);
            if (assigned[0].students?.length) {
              setStudents(assigned[0].students.map((s) => ({ ...s, usn: s.student_id })));
            }
          } else {
            setStudents([]);
            setNotice('No subject/class assignments are configured for this teacher.');
          }
        })
        .catch((err) => { setStudents([]); setNotice(err.message); });
    }
    if (auth.role !== 'teacher') {
      getStudents(1, 100)
        .then((data) => {
          if (data.students?.length) setStudents(data.students);
        })
        .catch(() => {});
    }
    return () => streamRef.current?.getTracks().forEach((track) => track.stop());
  }, [auth.role]);

  useEffect(() => {
    const openProfile = (event) => {
      const cell = event.target.closest('.roster-card tbody tr td:first-child');
      if (!cell) return;
      const student = students.find((item) => (item.name || item.student_name) === cell.innerText.trim());
      if (student) setSelectedStudent(student.student_id);
    };
    document.addEventListener('click', openProfile);
    return () => document.removeEventListener('click', openProfile);
  }, [students]);

  useEffect(() => {
    const selected = assignments.find((item) => item.subject_code === subject);
    if (selected && selected.students?.length) {
      setStudents(selected.students.map((s) => ({ ...s, usn: s.student_id })));
    }
  }, [assignments, subject]);

  const present = records.filter((record) => record.status === 'present').length;
  const total = students.length || records.length;
  const absent = Math.max(total - present, 0);
  const selectedSubject = SUBJECTS.find((item) => item[1] === subject);
  const roster = useMemo(() => {
    const byId = new Map(records.map((record) => [record.student_id, record]));
    return students.map((student) => byId.get(student.student_id) || {
      student_id: student.student_id,
      student_name: student.name,
      status: 'absent',
      attendance_id: null,
      is_manual_override: false,
      source: 'face',
    });
  }, [students, records]);

  if (selectedStudent) return <StudentDetail auth={auth} studentId={selectedStudent} onBack={() => setSelectedStudent(null)} />;

  const setImageFile = (file) => {
    if (!file) return;
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setNotice('');
    setDetectionResults([]);
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      streamRef.current = stream;
      setPreview('');
      setCameraOn(true);
      requestAnimationFrame(async () => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
      });
    } catch (err) { setNotice(`Camera unavailable: ${err.message}`); }
  };

  const capture = () => {
    if (!videoRef.current?.videoWidth) return setNotice('Camera is still starting. Try capture again.');
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext('2d').drawImage(videoRef.current, 0, 0);
    canvas.toBlob((blob) => {
      setImageFile(new File([blob], 'live-class.jpg', { type: 'image/jpeg' }));
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setCameraOn(false);
    }, 'image/jpeg', 0.92);
  };

  const submitImage = async () => {
    if (!image) return setNotice('Choose an image or capture the class first.');
    setBusy(true);
    setNotice('');
    try {
      const encoded = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(image);
      });
      const result = await markAttendanceBatch(encoded, classroom, date, subject);
      const log = await getAttendanceLog(classroom, date);
      setRecords(log.records || result.results || []);
      const results = result.results || [];
      setDetectionResults(results);
      const markedNames = results.filter((item) => item.status === 'present' && item.student_name).map((item) => item.student_name);
      const unknownCount = results.filter((item) => item.status === 'unrecognized').length;
      if (markedNames.length) {
        setNotice(`${markedNames.length} attendance record(s) marked: ${markedNames.join(', ')}.`);
      } else if (unknownCount) {
        setNotice(`${result.faces_detected || 0} face(s) detected, but none matched an enrolled student. No attendance was marked. Enrol this student's face, then try again.`);
      } else {
        setNotice(`${result.faces_detected || 0} face(s) detected. No new attendance record was created.`);
      }
    } catch (err) { setNotice(err.message); } finally { setBusy(false); }
  };

  const toggle = async (record) => {
    const next = record.status === 'present' ? 'absent' : 'present';
    try {
      if (record.attendance_id) {
        await patchAttendance(record.attendance_id, next, 'Teacher manual roster correction');
      } else {
        await createManualAttendance(record.student_id, classroom, date, subject, next, 'Teacher manual roster correction');
      }
      setRecords((current) =>
        current.map((item) =>
          item.student_id === record.student_id ? { ...item, status: next, is_manual_override: true, source: 'manual' } : item
        )
      );
    } catch (err) { setNotice(err.message); }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark small">V</span>
          <span>VISTA <b>Attendance</b></span>
        </div>
        <div className="top-actions">
          <NotificationCenter user={auth} onOpenCompose={() => setShowComposeNotif(true)} />
          <span>{auth?.name || auth?.email || 'Teacher'}</span>
          <button className="ghost" onClick={onLogout}>Sign out</button>
        </div>
      </header>
      <main className="workspace">
        <div className="page-heading">
          <div>
            <p className="eyebrow">Teacher console / {date}</p>
            <h1>Mark attendance</h1>
            <p>Only classes and subjects assigned to you are shown.</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button className="secondary" onClick={() => setShowManualModal(true)}>
              Manual Entry / Find Student
            </button>
            <div className="subject-chip">{selectedSubject?.[0]} <span>{selectedSubject?.[1]}</span></div>
          </div>
        </div>

        <section className="stats">
          <div><span>Present</span><strong className="green">{present}</strong><small>of {total} students</small></div>
          <div><span>Absent</span><strong className="red">{absent}</strong><small>can be edited below</small></div>
          <div><span>Attendance rate</span><strong>{total ? Math.round((present / total) * 100) : 0}%</strong><small>for this session</small></div>
        </section>

        <div className="content-grid">
          <section className="card capture-card">
            <div className="card-title"><div><p className="eyebrow">01 / Capture</p><h2>Class image</h2></div><span className="live-dot">● Ready</span></div>
            <div className={`camera-frame ${preview ? 'has-preview' : ''}`}>
              {preview ? (
                <img src={preview} alt="Class capture preview" />
              ) : (
                <>
                  <video ref={videoRef} className="camera-video" muted playsInline />
                  <div className={`camera-empty ${cameraOn ? 'camera-empty-hidden' : ''}`}>
                    <span className="camera-icon">◎</span>
                    <b>Use the live camera or upload a photo</b>
                    <small>JPEG or PNG · max 5 MB</small>
                  </div>
                </>
              )}
            </div>
            <div className="capture-actions">
              <button className="secondary" onClick={cameraOn ? capture : startCamera}>{cameraOn ? 'Capture frame' : 'Open camera'}</button>
              <label className="secondary file-button">Upload image<input type="file" accept="image/jpeg,image/png" onChange={(e) => setImageFile(e.target.files[0])} /></label>
            </div>
            {cameraOn && <button className="text-button" onClick={() => { streamRef.current?.getTracks().forEach((track) => track.stop()); setCameraOn(false); }}>Close camera</button>}
            <button className="primary wide" onClick={submitImage} disabled={busy}>{busy ? 'Detecting faces…' : 'Detect and mark attendance'}</button>
            {notice && <p className="notice">{notice}</p>}
            {detectionResults.length > 0 && (
              <div className="detection-results">
                <p className="eyebrow">Recognition result</p>
                {detectionResults.map((item, index) => (
                  <div className="detection-result" key={`${item.student_id || 'unknown'}-${index}`}>
                    <span>{item.student_name || 'Unknown face'}</span>
                    <small>
                      {item.student_name
                        ? `${item.status} · ${Math.round((item.confidence || 0) * 100)}% confidence`
                        : `Not enrolled · ${Math.round((item.confidence || 0) * 100)}% similarity`}
                    </small>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="card session-card">
            <div className="card-title"><div><p className="eyebrow">Session details</p><h2>What are we marking?</h2></div></div>
            <label>Class
              <select value={classroom} onChange={(e) => setClassroom(e.target.value)}>
                {(assignments.length ? assignments : [{ class_code: 'class-aiml-4a', class_section: '4th Year AIML', subject_code: SUBJECTS[0][1], subject_name: SUBJECTS[0][0], student_count: students.length }]).map((item) => (
                  <option key={`${item.class_code}-${item.subject_code}`} value={item.class_code}>
                    {item.class_section} · {item.student_count ?? students.length} students
                  </option>
                ))}
              </select>
            </label>
            <label>Subject
              <select value={subject} onChange={(e) => setSubject(e.target.value)}>
                {(assignments.length ? assignments : SUBJECTS.map(([name, code, teacher]) => ({ subject_name: name, subject_code: code, class_code: classroom }))).map((item) => (
                  <option key={item.subject_code} value={item.subject_code}>
                    {item.subject_name} · {item.subject_code}
                  </option>
                ))}
              </select>
            </label>
            <label>Session date<input type="date" value={date} onChange={(e) => setDate(e.target.value)} /></label>
            <div className="subject-list">
              <p className="eyebrow">Your assigned classes</p>
              {(assignments.length ? assignments : SUBJECTS.map(([name, code, teacher]) => ({ subject_name: name, subject_code: code, class_section: '4th Year AIML', class_code: classroom, teacher }))).map((item) => (
                <div className="subject-row" key={`${item.class_code}-${item.subject_code}`}>
                  <span>{item.subject_name}<small>{item.subject_code} · {item.class_section}</small></span>
                  <b>{item.student_count ?? students.length} students</b>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="card roster-card">
          <div className="card-title">
            <div>
              <p className="eyebrow">02 / Review</p>
              <h2>Student roster</h2>
              <p>Click a status to manually correct attendance when the model misses a face.</p>
            </div>
            <input
              className="search"
              placeholder="Search name or USN"
              onChange={(e) => {
                const value = e.target.value.toLowerCase();
                setStudents(value ? students.filter((s) => `${s.name} ${s.usn || s.student_id}`.toLowerCase().includes(value)) : ROSTER);
              }}
            />
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>USN</th>
                  <th>Confidence</th>
                  <th>Source</th>
                  <th>Status</th>
                  <th>Manual edit</th>
                </tr>
              </thead>
              <tbody>
                {roster.map((record) => (
                  <tr key={record.student_id}>
                    <td><b>{record.student_name}</b></td>
                    <td className="mono">{record.student_id}</td>
                    <td>{record.confidence ? `${Math.round(record.confidence * 100)}%` : '—'}</td>
                    <td>
                      <span className={`badge ${record.source || (record.is_manual_override ? 'manual' : 'face')}`}>
                        {record.source || (record.is_manual_override ? 'manual' : 'face')}
                      </span>
                    </td>
                    <td><span className={`status ${record.status}`}>{record.status === 'present' ? 'Present' : 'Absent'}</span></td>
                    <td>
                      <button className="edit-button" onClick={() => toggle(record)}>
                        {record.status === 'present' ? 'Mark absent' : 'Mark present'} {record.is_manual_override && '· edited'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <ManualEntryModal
          isOpen={showManualModal}
          onClose={() => setShowManualModal(false)}
          userRole="teacher"
          assignedSubjects={assignments.length ? assignments : SUBJECTS.map((s) => ({ name: s[0], code: s[1] }))}
          allStudents={students}
          onDone={() => getAttendanceLog(classroom, date).then((log) => setRecords(log.records || []))}
        />

        <ComposeNotificationModal
          isOpen={showComposeNotif}
          onClose={() => setShowComposeNotif(false)}
          user={auth}
          assignedSubjects={assignments.length ? assignments : SUBJECTS.map((s) => ({ name: s[0], code: s[1] }))}
        />
      </main>
    </div>
  );
}

export default function App() {
  const [auth, setAuth] = useState(() => {
    try { return JSON.parse(localStorage.getItem('vista_auth')); } catch { return null; }
  });
  useEffect(() => {
    if (auth) localStorage.setItem('vista_auth', JSON.stringify(auth));
    else localStorage.removeItem('vista_auth');
  }, [auth]);

  if (!auth) return <Login onLogin={setAuth} />;
  if (auth.role === 'student') return <StudentWorkspace auth={auth} onLogout={() => setAuth(null)} />;
  if (auth.role === 'admin') return <AdminWorkspace auth={auth} onLogout={() => setAuth(null)} />;
  return <AttendanceWorkspace auth={auth} onLogout={() => setAuth(null)} />;
}
