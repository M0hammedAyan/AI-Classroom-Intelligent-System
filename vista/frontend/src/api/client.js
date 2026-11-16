const BASE_URL = '/api/v1';

function token() {
  try { return JSON.parse(localStorage.getItem('vista_auth'))?.token; } catch { return null; }
}

async function request(path, options = {}) {
  const headers = { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(token() ? { Authorization: `Bearer ${token()}` } : {}), ...options.headers };
  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (response.status === 401) { localStorage.removeItem('vista_auth'); window.location.reload(); }
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail?.message || error.detail || error.error?.message || response.statusText);
  }
  return response.json();
}

export const login = (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
export const getStudents = (page = 1, pageSize = 100, classCode = '') => request(`/students?page=${page}&page_size=${pageSize}${classCode ? `&class_code=${encodeURIComponent(classCode)}` : ''}`);
export const getStudentAcademicRecord = (studentId) => request(`/students/${encodeURIComponent(studentId)}/academic-record`);
export const getStudentImages = (studentId) => request(`/students/${encodeURIComponent(studentId)}/images`);
export const getTeacherSubjects = () => request('/admin/teacher/my-subjects');
export const getAdminUsers = () => request('/admin/users');
export const createAdminUser = (body) => request('/admin/users', { method: 'POST', body: JSON.stringify(body) });
export const updateAdminUser = (id, body) => request(`/admin/users/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
export const deleteAdminUser = (id) => request(`/admin/users/${id}`, { method: 'DELETE' });
export const updateStudent = (id, body) => request(`/admin/students/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
export const deleteStudent = (id) => request(`/admin/students/${id}`, { method: 'DELETE' });
export const createStudent = (body) => request('/admin/students', { method: 'POST', body: JSON.stringify(body) });
export const getAdminSubjects = () => request('/admin/subjects');
export const getAdminClasses = () => request('/admin/class-sections');
export const createAdminClass = (body) => request('/admin/class-sections', { method: 'POST', body: JSON.stringify(body) });
export const createSubject = (body) => request('/admin/subjects', { method: 'POST', body: JSON.stringify(body) });
export const updateSubject = (id, body) => request(`/admin/subjects/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
export const deleteSubject = (id) => request(`/admin/subjects/${id}`, { method: 'DELETE' });
export const assignTeacher = (teacherId, subjectId, classSectionId = 'class-aiml-4a') => request('/admin/assign-teacher', { method: 'POST', body: JSON.stringify({ teacher_id: teacherId, subject_id: subjectId, class_section_id: classSectionId }) });
export const enrollStudent = (id, images) => request(`/students/${encodeURIComponent(id)}/enroll`, { method: 'POST', body: JSON.stringify({ images }) });
export const getStudentDashboard = () => request('/student-portal/dashboard');
export const getStudentAttendance = () => request('/student-portal/attendance/by-subject');
export const getStudentScores = () => request('/student-portal/scores');
export const getStudentSubjectDetail = (subjectId) => request(`/student-portal/subjects/${encodeURIComponent(subjectId)}/detail`);
export const getStudentMarks = (studentId, subject = '') => request(`/lms/student/${encodeURIComponent(studentId)}/marks${subject ? `?subject=${encodeURIComponent(subject)}` : ''}`);
export const getStudentAttendanceHistory = (studentId, subjectId = '') => request(`/attendance/student/${encodeURIComponent(studentId)}${subjectId ? `?subject_id=${encodeURIComponent(subjectId)}` : ''}`);
export const markAttendanceBatch = (image, classroomId, sessionDate, subjectId) => request('/attendance/mark-batch', { method: 'POST', body: JSON.stringify({ image, classroom_id: classroomId, session_date: sessionDate, subject_id: subjectId }) });
export const getAttendanceLog = (classroomId, date) => request(`/attendance/log?classroom_id=${encodeURIComponent(classroomId)}&date=${date}`);
export const patchAttendance = (id, status, note) => request(`/attendance/${id}`, { method: 'PATCH', body: JSON.stringify({ status, note }) });
export const createManualAttendance = (studentId, classroomId, sessionDate, subjectId, status, note) => request('/attendance/manual', { method: 'POST', body: JSON.stringify({ student_id: studentId, classroom_id: classroomId, session_date: sessionDate, subject_id: subjectId, status, note }) });
export const addScore = (studentId, subject, score, maxScore = 25, date = '', assessmentType = 'CIE 1', reason = '', status = 'scored') => request('/lms/add-score', { method: 'POST', body: JSON.stringify({ student_id: studentId, subject, score, max_score: maxScore, date, assessment_type: assessmentType, reason, status }) });

// Notifications
export const getNotifications = (page = 1, pageSize = 20) => request(`/notifications?page=${page}&page_size=${pageSize}`);
export const getUnreadNotificationsCount = () => request('/notifications/unread-count');
export const createNotification = (body) => request('/notifications', { method: 'POST', body: JSON.stringify(body) });
export const markNotificationRead = (id) => request(`/notifications/${id}/read`, { method: 'POST' });
export const markAllNotificationsRead = () => request('/notifications/read-all', { method: 'POST' });
export const deleteNotification = (id) => request(`/notifications/${id}`, { method: 'DELETE' });

// Coach Chatbot
export const coachChat = (message) => request('/coach/chat', { method: 'POST', body: JSON.stringify({ message }) });
export const getCoachHistory = (limit = 50) => request(`/coach/history?limit=${limit}`);
export const clearCoachHistory = () => request('/coach/history', { method: 'DELETE' });
export const getCoachSummary = () => request('/coach/summary');

// Timetable
export const getStudentTimetable = () => request('/timetable/student');
export const getTeacherTimetable = () => request('/timetable/teacher');
export const getClassTimetable = (classSectionId) => request(`/timetable/class/${encodeURIComponent(classSectionId)}`);
export const getAdminTimetable = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/timetable/admin${query ? `?${query}` : ''}`);
};
export const createTimetableSlot = (body) => request('/timetable/slots', { method: 'POST', body: JSON.stringify(body) });
export const updateTimetableSlot = (id, body) => request(`/timetable/slots/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(body) });
export const deleteTimetableSlot = (id) => request(`/timetable/slots/${encodeURIComponent(id)}`, { method: 'DELETE' });
export const assignStudentBatch = (studentId, batch) => request(`/timetable/admin/students/${encodeURIComponent(studentId)}/batch`, { method: 'PATCH', body: JSON.stringify({ batch }) });

// Reports
export const getMyStudentReport = () => request('/reports/student/me');
export const getStudentReport = (studentId) => request(`/reports/student/${encodeURIComponent(studentId)}`);
export const getMyTeacherReport = () => request('/reports/teacher/me');
export const getTeacherReport = (teacherId) => request(`/reports/teacher/${encodeURIComponent(teacherId)}`);

const _downloadFile = async (url, filename) => {
  const headers = token() ? { Authorization: `Bearer ${token()}` } : {};
  const response = await fetch(url, { headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail?.message || error.detail || 'Download failed');
  }
  const blob = await response.blob();
  const objectUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = objectUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(objectUrl);
};

export const downloadStudentPdf = async (studentId, studentName = 'student') => {
  const safe = studentName.replace(/\s+/g, '_');
  await _downloadFile(
    `${BASE_URL}/reports/student/${encodeURIComponent(studentId)}/pdf`,
    `VISTA_Report_${studentId}_${safe}.pdf`
  );
};

export const downloadStudentCsv = async (studentId, studentName = 'student') => {
  const safe = studentName.replace(/\s+/g, '_');
  await _downloadFile(
    `${BASE_URL}/reports/student/${encodeURIComponent(studentId)}/csv`,
    `VISTA_Report_${studentId}_${safe}.csv`
  );
};

export const downloadTeacherPdf = async (teacherId, teacherName = 'teacher') => {
  const safe = teacherName.replace(/\s+/g, '_');
  await _downloadFile(
    `${BASE_URL}/reports/teacher/${encodeURIComponent(teacherId)}/pdf`,
    `VISTA_Teacher_Report_${safe}.pdf`
  );
};

export const downloadTeacherCsv = async (teacherId, teacherName = 'teacher') => {
  const safe = teacherName.replace(/\s+/g, '_');
  await _downloadFile(
    `${BASE_URL}/reports/teacher/${encodeURIComponent(teacherId)}/csv`,
    `VISTA_Teacher_Report_${safe}.csv`
  );
};

export const downloadMyStudentCsv = async (studentId) => {
  await _downloadFile(
    `${BASE_URL}/reports/student/me/csv`,
    `VISTA_My_Report_${studentId}.csv`
  );
};

export const downloadMyTeacherPdf = async (teacherName = 'teacher') => {
  const safe = teacherName.replace(/\s+/g, '_');
  await _downloadFile(
    `${BASE_URL}/reports/teacher/me/pdf`,
    `VISTA_My_Teaching_Report_${safe}.pdf`
  );
};

export const downloadMyTeacherCsv = async (teacherName = 'teacher') => {
  const safe = teacherName.replace(/\s+/g, '_');
  await _downloadFile(
    `${BASE_URL}/reports/teacher/me/csv`,
    `VISTA_My_Teaching_Report_${safe}.csv`
  );
};

// Capture History
export const getCaptureHistory = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/attendance/capture-history${query ? `?${query}` : ''}`);
};
