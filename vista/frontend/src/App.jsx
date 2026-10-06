import { useEffect, useMemo, useRef, useState } from 'react';
import { login, getStudents, getTeacherSubjects, getAdminUsers, createAdminUser, updateAdminUser, deleteAdminUser, updateStudent, deleteStudent, createStudent, getAdminSubjects, createSubject, updateSubject, deleteSubject, assignTeacher, enrollStudent, getStudentDashboard, getStudentAttendance, getStudentScores, markAttendanceBatch, getAttendanceLog, patchAttendance, createManualAttendance } from './api/client';

const SUBJECTS = [
  ['Deep Learning', '22AIU701', 'Mrs Rajeshwari'],
  ['Generative AI', '22AIU702', 'Dr Ajayprakash B V'],
  ['Data Engineering & Analytics', '22AIT703', 'Mr Ganesh H J'],
  ['Data Security and Privacy', '22AIT704C', 'Dr Bharat V S'],
  ['Major Project Phase 2', '22AIP706', 'Mr Ganesh H J'],
];

const ROSTER = `ADITYA|1DA22AI002
CHETHAN KUMAR R|1DA22AI010
DHANVANTHA JANARDHANA|1DA22AI013
SHRUTI P|1DA22AI044
VISHWAS K|1DA22AI050
ABHAY B SUVARNА|1DA23AI001
AKASH KIRAN GOWDA|1DA23AI002
AKASH KUMAR SINGH|1DA23AI003
ANUJ PATEL|1DA23AI004
ANUUJ KUMAR|1DA23AI005
ANUSHKA M R|1DA23AI006
ANVESH B R|1DA23AI007
APPATIGOUDA|1DA23AI008
ARYAN RAJ SINGH|1DA23AI009
ATHISH SRINIVAS|1DA23AI010
AYUSH A VASTER|1DA23AI011
BABU|1DA23AI012
DEEKSHITHA S GOWDA|1DA23AI013
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
RISHABH RANNA PATTANSHETTI|1DA23AI038
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
SUJALA AGRAHARI|1DA23AI050
SUJMA|1DA23AI051
SUMIT KUMAR|1DA23AI052
TARUN G|1DA23AI054
TEJAS M NAIDU|1DA23AI055
THEJAS A G|1DA23AI056
VARSHINIK T|1DA23AI057
VEDA K VIJAYALAD|1DA23AI058
VEMUGANTI SRIRAG|1DA23AI059
YASHWANTH R|1DA23AI060
AVSHUMALEE BHAT MARAKAN|1DA23AI061
NAVMITH L|1DA23AI062
AKSHITHA G R|1DA24AI400
MAHESH REDDY GODEPALLY|1DA24AI401
MC CHETHAN PATIL|1DA24AI402
MOHAMMED AYYAN|1DA24AI403
VIGNESH V|1DA24AI404
VINAY V S|1DA24AI405`
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

function StudentWorkspace({ auth, onLogout }) {
  const [dashboard, setDashboard] = useState(null);
  const [attendance, setAttendance] = useState(null);
  const [scores, setScores] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    Promise.all([getStudentDashboard(), getStudentAttendance(), getStudentScores()])
      .then(([overview, attendanceData, scoresData]) => { setDashboard(overview); setAttendance(attendanceData); setScores(scoresData); })
      .catch((err) => setError(err.message));
  }, []);
  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark small">V</span><span>VISTA <b>Student portal</b></span></div><div className="top-actions"><span>{auth.name}</span><button className="ghost" onClick={onLogout}>Sign out</button></div></header>
    <main className="workspace"><div className="page-heading"><div><p className="eyebrow">Student portal / read only</p><h1>My academic view</h1><p>View your attendance and marks. Editing is disabled for student accounts.</p></div></div>
      {error && <p className="error">{error}</p>}
      <section className="stats"><div><span>Attendance</span><strong className="green">{dashboard?.attendance_pct ?? '—'}%</strong><small>personal attendance</small></div><div><span>Average marks</span><strong>{dashboard?.avg_score ?? '—'}%</strong><small>across assessments</small></div><div><span>Class</span><strong className="class-value">{dashboard?.class || '—'}</strong><small>{dashboard?.usn || ''}</small></div></section>
      <div className="content-grid"><section className="card"><div className="card-title"><div><p className="eyebrow">Attendance</p><h2>By subject</h2></div><span className="read-only">Read only</span></div><div className="subject-list">{(attendance?.by_subject || []).map((item) => <div className="subject-row" key={item.subject_id}><span>{item.subject_name}<small>{item.subject_code}</small></span><b>{item.attendance_pct ?? 0}% · {item.sessions_attended}/{item.total_sessions}</b></div>)}</div></section><section className="card"><div className="card-title"><div><p className="eyebrow">Marks</p><h2>My results</h2></div><span className="read-only">Read only</span></div><div className="subject-list">{(scores?.by_subject || []).map((item) => <div className="subject-row" key={item.subject}><span>{item.subject}<small>{item.assessments} assessments</small></span><b>{item.average_pct}%</b></div>)}</div></section></div>
    </main>
  </div>;
}

function AdminWorkspace({ auth, onLogout }) {
  const [users, setUsers] = useState([]);
  const [students, setStudents] = useState(ROSTER);
  const [subjects, setSubjects] = useState([]);
  const [error, setError] = useState('');
  const [editor, setEditor] = useState(null);
  const [editorError, setEditorError] = useState('');
  const [teacherSearch, setTeacherSearch] = useState('');
  const [subjectSearch, setSubjectSearch] = useState('');
  const [studentSearch, setStudentSearch] = useState('');
  const [teacherQuery, setTeacherQuery] = useState('');
  const [subjectQuery, setSubjectQuery] = useState('');
  const [studentQuery, setStudentQuery] = useState('');
  const reload = () => Promise.all([getAdminUsers(), getStudents(1, 100), getAdminSubjects()]).then(([userData, studentData, subjectData]) => { setUsers(userData.users || []); if (studentData.students?.length) setStudents(studentData.students); setSubjects(subjectData.subjects || []); }).catch((err) => setError(err.message));
  useEffect(() => { reload(); }, []);
  const openEditor = (type, item = {}) => { setEditorError(''); setEditor({ type, id: item.id || item.student_id || null, name: item.name || '', email: item.email || '', password: '', code: item.code || '', usn: item.usn || item.student_id || '', teacherId: '' }); };
  const saveEditor = async (event) => {
    event.preventDefault();
    try {
      if (editor.type === 'teacher') {
        if (editor.id) await updateAdminUser(editor.id, { name: editor.name, email: editor.email, ...(editor.password ? { password: editor.password } : {}) });
        else await createAdminUser({ name: editor.name, email: editor.email, password: editor.password, role: 'teacher' });
      } else if (editor.type === 'student') {
        if (editor.id) await updateStudent(editor.id, { name: editor.name, usn: editor.usn });
        else {
          const createdStudent = await createStudent({ name: editor.name, usn: editor.usn, class_code: 'AIML-3A' });
          setEditor(null);
          setEditorError('');
          await reload();
          if (window.confirm(`Student ${createdStudent.name || editor.name} was added. Enrol this student's face now?`)) {
            await enroll(createdStudent);
          }
          return;
        }
      } else {
        let subject = editor.id ? await updateSubject(editor.id, { name: editor.name, code: editor.code }) : await createSubject({ name: editor.name, code: editor.code, department_id: 'dept-aiml', semester: '6' });
        if (editor.teacherId) await assignTeacher(editor.teacherId, subject.id, 'class-aiml-4a');
      }
      setEditor(null); setEditorError(''); setError(''); await reload();
    } catch (err) { setEditorError(err.message); }
  };
  const removeTeacher = async (user) => {
    if (!window.confirm(`Delete ${user.name}?`)) return;
    try { await deleteAdminUser(user.id); reload(); } catch (err) { setError(err.message); }
  };
  const removeSubject = async (subject) => {
    if (!window.confirm(`Delete ${subject.name}?`)) return;
    try { await deleteSubject(subject.id); reload(); } catch (err) { setError(err.message); }
  };
  const enroll = async (student) => {
    const input = document.createElement('input'); input.type = 'file'; input.accept = 'image/jpeg,image/png'; input.multiple = true;
    input.onchange = async () => {
      const files = Array.from(input.files || []).slice(0, 5);
      if (!files.length) return;
      try {
        const images = await Promise.all(files.map((file) => new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(',')[1]); reader.onerror = reject; reader.readAsDataURL(file); })));
        await enrollStudent(student.student_id, images); setError(''); window.alert(`${student.name} face enrollment completed.`); reload();
      } catch (err) { setError(err.message); }
    };
    input.click();
  };
  const removeStudent = async (student) => {
    if (!window.confirm(`Delete ${student.name}? Face enrollment/embedding will be retained for this USN.`)) return;
    try { await deleteStudent(student.student_id); reload(); } catch (err) { setError(err.message); }
  };
  const teachers = users.filter((user) => user.role === 'teacher' && `${user.name} ${user.email} ${user.id}`.toLowerCase().includes(teacherSearch.toLowerCase()));
  const filteredSubjects = subjects.filter((subject) => `${subject.name} ${subject.code} ${subject.id}`.toLowerCase().includes(subjectSearch.toLowerCase()));
  const filteredStudents = students.filter((student) => `${student.name} ${student.usn || student.student_id} ${student.student_id}`.toLowerCase().includes(studentSearch.toLowerCase()));
  return <div className="app-shell"><header className="topbar"><div className="brand"><span className="brand-mark small">V</span><span>VISTA <b>Admin / HOD</b></span></div><div className="top-actions"><span>{auth.name}</span><button type="button" className="ghost" onClick={onLogout}>Sign out</button></div></header><main className="workspace"><div className="page-heading"><div><p className="eyebrow">Administrator / full access</p><h1>Academic control centre</h1><p>Manage teachers, students, attendance, marks, subjects, and face enrollment.</p></div></div>{error && !editor && <p className="error">{error}</p>}{editor && <div className="editor-overlay" role="presentation"><form className="card editor-form" onSubmit={saveEditor}><div className="card-title"><div><p className="eyebrow">Edit workspace</p><h2>{editor.id ? 'Edit' : 'Add'} {editor.type}</h2></div><button type="button" className="ghost" onClick={() => { setEditor(null); setEditorError(''); }}>Cancel</button></div>{editorError && <p className="error editor-error">{editorError}</p>}<label>Name<input required value={editor.name} onChange={(e) => setEditor({ ...editor, name: e.target.value })} /></label>{editor.type === 'teacher' && <><label>Email<input required type="email" value={editor.email} onChange={(e) => setEditor({ ...editor, email: e.target.value })} /></label><label>{editor.id ? 'New password (optional)' : 'Password'}<input required={!editor.id} type="password" value={editor.password} onChange={(e) => setEditor({ ...editor, password: e.target.value })} /></label></>}{editor.type === 'student' && <label>USN<input required value={editor.usn} onChange={(e) => setEditor({ ...editor, usn: e.target.value })} /></label>  }{editor.type === 'subject' && <><label>Subject code<input required value={editor.code} onChange={(e) => setEditor({ ...editor, code: e.target.value })} /></label><label>Assign teacher<select value={editor.teacherId} onChange={(e) => setEditor({ ...editor, teacherId: e.target.value })}><option value="">Select a teacher</option>{users.filter((user) => user.role === 'teacher').map((user) => <option key={user.id} value={user.id}>{user.name} · {user.email}</option>)}</select></label></>}<button className="primary" type="submit">Save {editor.type}</button>  </form></div>}<section className="stats"><div><span>Students</span><strong>{students.length}</strong><small>view and manage roster</small></div><div><span>Teachers</span><strong>{users.filter((user) => user.role === 'teacher').length}</strong><small>subject instructors</small></div><div><span>Subjects</span><strong>{subjects.length || SUBJECTS.length}</strong><small>configured curriculum</small></div></section><div className="content-grid"><section className="card"><div className="card-title"><div><p className="eyebrow">People</p><h2>Teachers</h2></div><button className="primary" onClick={() => openEditor('teacher')}>Add teacher</button></div><label className="search-field">Search teacher by name, email, or ID<input value={teacherQuery} onChange={(e) => setTeacherQuery(e.target.value)} placeholder="e.g. Rajeshwari or teacher ID" /><button type="button" className="secondary" onClick={() => setTeacherSearch(teacherQuery)}>Search teachers</button></label><div className="subject-list">{teachers.map((user) => <div className="subject-row" key={user.id}><span>{user.name}<small>{user.email}</small></span><b><button className="edit-button" onClick={() => openEditor('teacher', user)}>Edit</button><button className="edit-button" onClick={() => removeTeacher(user)}>Delete</button></b></div>)}</div></section><section className="card"><div className="card-title"><div><p className="eyebrow">Curriculum</p><h2>Subjects</h2></div><button className="primary" onClick={() => openEditor('subject')}>Add subject</button></div><label className="search-field">Search subject by name, code, or ID<input value={subjectQuery} onChange={(e) => setSubjectQuery(e.target.value)} placeholder="e.g. Deep Learning or 22AIU701" /><button type="button" className="secondary" onClick={() => setSubjectSearch(subjectQuery)}>Search subjects</button></label><div className="subject-list">{filteredSubjects.map((subject) => <div className="subject-row" key={subject.id}><span>{subject.name}<small>{subject.code}</small></span><b><button className="edit-button" onClick={() => openEditor('subject', subject)}>Edit</button><button className="edit-button" onClick={() => removeSubject(subject)}>Delete</button></b></div>)}</div></section></div><section className="card roster-card"><div className="card-title"><div><p className="eyebrow">Students</p><h2>All students</h2></div><button className="primary" onClick={() => openEditor('student')}>Add student</button></div><label className="search-field">Search student by name or USN<input value={studentQuery} onChange={(e) => setStudentQuery(e.target.value)} placeholder="e.g. Aditya or 1DA22AI002" /><button type="button" className="secondary" onClick={() => setStudentSearch(studentQuery)}>Search students</button></label><div className="table-wrap"><table><thead><tr><th>Name</th><th>USN</th><th>Class</th><th>Face enrollment</th><th>Actions</th></tr></thead><tbody>{filteredStudents.map((student) => <tr key={student.student_id}><td><b>{student.name}</b></td><td className="mono">{student.usn || student.student_id}</td><td>{student.class || '—'}</td><td><button className="edit-button" onClick={() => enroll(student)}>{student.enrolled_at ? 'Re-enrol face' : 'Enrol face'}</button></td><td><button className="edit-button" onClick={() => openEditor('student', student)}>Edit</button><button className="edit-button" onClick={() => removeStudent(student)}>Delete</button></td></tr>)}</tbody></table></div></section></main></div>;
}

function AttendanceWorkspace({ auth, onLogout }) {
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents] = useState(ROSTER);
  const [subject, setSubject] = useState(SUBJECTS[0][1]);
  const [classroom, setClassroom] = useState('class-ai-2022');
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

  useEffect(() => {
    if (auth.role === 'teacher') getTeacherSubjects().then((data) => {
      const assigned = data.subjects || [];
      setAssignments(assigned);
      if (assigned.length) {
        setSubject(assigned[0].subject_code);
        setClassroom(assigned[0].class_code);
      } else {
        setStudents([]);
        setNotice('No subject/class assignments are configured for this teacher.');
      }
    }).catch((err) => { setStudents([]); setNotice(err.message); });
    if (auth.role !== 'teacher') {
      getStudents(1, 100).then((data) => {
        if (data.students?.length) setStudents(data.students);
      }).catch(() => {});
    }
    return () => streamRef.current?.getTracks().forEach((track) => track.stop());
  }, [auth.role]);

  useEffect(() => {
    const selected = assignments.find((item) => item.subject_code === subject && item.class_code === classroom);
    if (selected) setStudents(selected.students.map((student) => ({ ...student, name: student.name, usn: student.student_id })));
  }, [assignments, classroom, subject]);

  const present = records.filter((record) => record.status === 'present').length;
  const total = students.length || records.length;
  const absent = Math.max(total - present, 0);
  const selectedSubject = SUBJECTS.find((item) => item[1] === subject);
  const roster = useMemo(() => {
    const byId = new Map(records.map((record) => [record.student_id, record]));
    return students.map((student) => byId.get(student.student_id) || {
      student_id: student.student_id, student_name: student.name, status: 'absent',
      attendance_id: null, is_manual_override: false,
    });
  }, [students, records]);

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
    canvas.width = videoRef.current.videoWidth; canvas.height = videoRef.current.videoHeight;
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
    setBusy(true); setNotice('');
    try {
      const encoded = await new Promise((resolve, reject) => {
        const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(',')[1]); reader.onerror = reject; reader.readAsDataURL(image);
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
      if (record.attendance_id) await patchAttendance(record.attendance_id, next, 'Teacher manual correction');
      else await createManualAttendance(record.student_id, classroom, date, subject, next, 'Teacher manual correction');
      setRecords((current) => current.map((item) => item.student_id === record.student_id ? { ...item, status: next, is_manual_override: true } : item));
    } catch (err) { setNotice(err.message); }
  };

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark small">V</span><span>VISTA <b>Attendance</b></span></div><div className="top-actions"><span>{auth?.name || auth?.email || 'Teacher'}</span><button className="ghost" onClick={onLogout}>Sign out</button></div></header>
    <main className="workspace">
      <div className="page-heading"><div><p className="eyebrow">Teacher console / {date}</p><h1>Mark attendance</h1><p>Only classes and subjects assigned to you are shown.</p></div><div className="subject-chip">{selectedSubject?.[0]} <span>{selectedSubject?.[1]}</span></div></div>
      <section className="stats"><div><span>Present</span><strong className="green">{present}</strong><small>of {total} students</small></div><div><span>Absent</span><strong className="red">{absent}</strong><small>can be edited below</small></div><div><span>Attendance rate</span><strong>{total ? Math.round((present / total) * 100) : 0}%</strong><small>for this session</small></div></section>
      <div className="content-grid">
        <section className="card capture-card"><div className="card-title"><div><p className="eyebrow">01 / Capture</p><h2>Class image</h2></div><span className="live-dot">● Ready</span></div>
          <div className={`camera-frame ${preview ? 'has-preview' : ''}`}>{preview ? <img src={preview} alt="Class capture preview" /> : <><video ref={videoRef} className="camera-video" muted playsInline /><div className={`camera-empty ${cameraOn ? 'camera-empty-hidden' : ''}`}><span className="camera-icon">◎</span><b>Use the live camera or upload a photo</b><small>JPEG or PNG · max 5 MB</small></div></>}</div>
          <div className="capture-actions"><button className="secondary" onClick={cameraOn ? capture : startCamera}>{cameraOn ? 'Capture frame' : 'Open camera'}</button><label className="secondary file-button">Upload image<input type="file" accept="image/jpeg,image/png" onChange={(e) => setImageFile(e.target.files[0])} /></label></div>
          {cameraOn && <button className="text-button" onClick={() => { streamRef.current?.getTracks().forEach((track) => track.stop()); setCameraOn(false); }}>Close camera</button>}
          <button className="primary wide" onClick={submitImage} disabled={busy}>{busy ? 'Detecting faces…' : 'Detect and mark attendance'}</button>
          {notice && <p className="notice">{notice}</p>}
          {detectionResults.length > 0 && <div className="detection-results">
            <p className="eyebrow">Recognition result</p>
            {detectionResults.map((item, index) => <div className="detection-result" key={`${item.student_id || 'unknown'}-${index}`}>
              <span>{item.student_name || 'Unknown face'}</span>
              <small>{item.student_name ? `${item.status} · ${Math.round((item.confidence || 0) * 100)}% confidence` : `Not enrolled · ${Math.round((item.confidence || 0) * 100)}% similarity`}</small>
            </div>)}
          </div>}
        </section>
        <section className="card session-card"><div className="card-title"><div><p className="eyebrow">Session details</p><h2>What are we marking?</h2></div></div><label>Class<select value={classroom} onChange={(e) => setClassroom(e.target.value)}>{(assignments.length ? assignments : [{ class_code: 'class-ai-2022', class_section: 'AIML 3rd Year', subject_code: SUBJECTS[0][1], subject_name: SUBJECTS[0][0], student_count: students.length }]).map((item) => <option key={`${item.class_code}-${item.subject_code}`} value={item.class_code}>{item.class_section} · {item.student_count} students</option>)}</select></label><label>Subject<select value={subject} onChange={(e) => setSubject(e.target.value)}>{(assignments.length ? assignments : SUBJECTS.map(([name, code, teacher]) => ({ subject_name: name, subject_code: code, class_code: classroom }))).filter((item) => !assignments.length || item.class_code === classroom).map((item) => <option key={item.subject_code} value={item.subject_code}>{item.subject_name} · {item.subject_code}</option>)}</select></label><label>Session date<input type="date" value={date} onChange={(e) => setDate(e.target.value)} /></label><div className="subject-list"><p className="eyebrow">Your assigned classes</p>{(assignments.length ? assignments : SUBJECTS.map(([name, code, teacher]) => ({ subject_name: name, subject_code: code, class_section: 'AIML 3rd Year', class_code: classroom, teacher }))).map((item) => <div className="subject-row" key={`${item.class_code}-${item.subject_code}`}><span>{item.subject_name}<small>{item.subject_code} · {item.class_section}</small></span><b>{item.student_count ?? students.length} students</b></div>)}</div></section>
      </div>
      <section className="card roster-card"><div className="card-title"><div><p className="eyebrow">02 / Review</p><h2>Student roster</h2><p>Click a status to manually correct attendance when the model misses a face.</p></div><input className="search" placeholder="Search name or USN" onChange={(e) => { const value = e.target.value.toLowerCase(); setStudents(value ? students.filter((s) => `${s.name} ${s.usn}`.toLowerCase().includes(value)) : ROSTER); }} /></div><div className="table-wrap"><table><thead><tr><th>Student</th><th>USN</th><th>Confidence</th><th>Status</th><th>Manual edit</th></tr></thead><tbody>{roster.map((record) => <tr key={record.student_id}><td><b>{record.student_name}</b></td><td className="mono">{record.student_id}</td><td>{record.confidence ? `${Math.round(record.confidence * 100)}%` : '—'}</td><td><span className={`status ${record.status}`}>{record.status === 'present' ? 'Present' : 'Absent'}</span></td><td><button className="edit-button" onClick={() => toggle(record)}>{record.status === 'present' ? 'Mark absent' : 'Mark present'} {record.is_manual_override && '· edited'}</button></td></tr>)}</tbody></table></div></section>
    </main>
  </div>;
}

export default function App() {
  const [auth, setAuth] = useState(() => { try { return JSON.parse(localStorage.getItem('vista_auth')); } catch { return null; } });
  useEffect(() => { if (auth) localStorage.setItem('vista_auth', JSON.stringify(auth)); else localStorage.removeItem('vista_auth'); }, [auth]);
  if (!auth) return <Login onLogin={setAuth} />;
  if (auth.role === 'student') return <StudentWorkspace auth={auth} onLogout={() => setAuth(null)} />;
  if (auth.role === 'admin') return <AdminWorkspace auth={auth} onLogout={() => setAuth(null)} />;
  return <AttendanceWorkspace auth={auth} onLogout={() => setAuth(null)} />;
}
