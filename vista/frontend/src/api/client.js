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
    throw new Error(error.detail?.message || error.error?.message || response.statusText);
  }
  return response.json();
}

export const login = (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
export const getStudents = (page = 1, pageSize = 100) => request(`/students?page=${page}&page_size=${pageSize}`);
export const getStudentAcademicRecord = (studentId) => request(`/students/${encodeURIComponent(studentId)}/academic-record`);
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
export const addScore = (studentId, subject, score, maxScore = 25, date = '', assessmentType = 'CIE 1', reason = '') => request('/lms/add-score', { method: 'POST', body: JSON.stringify({ student_id: studentId, subject, score, max_score: maxScore, date, assessment_type: assessmentType, reason }) });
