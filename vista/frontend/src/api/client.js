/**
 * VISTA API Client
 * ================
 * All backend calls go through this file. When the real backend goes live,
 * the only change needed is BASE_URL. See docs/API_CONTRACT.md for schema.
 */

const BASE_URL = '/api/v1';

function getToken() {
  const stored = localStorage.getItem('vista_auth');
  if (!stored) return null;
  return JSON.parse(stored).token;
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    localStorage.removeItem('vista_auth');
    window.location.href = '/login';
    throw new Error('Session expired');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(err.error?.message || err.detail?.message || res.statusText);
  }

  // Handle file downloads (CSV/PDF)
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('text/csv') || contentType.includes('application/pdf')) {
    return res.blob();
  }

  return res.json();
}

// --- Auth ---

export async function login(email, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail?.message || err.error?.message || 'Login failed');
  }
  return res.json();
}

export async function logout() {
  return request('/auth/logout', { method: 'POST' });
}

// --- Students ---

export async function getStudents(page = 1, pageSize = 50) {
  return request(`/students?page=${page}&page_size=${pageSize}`);
}

export async function getStudent(studentId) {
  return request(`/students/${studentId}`);
}

// --- Attendance ---

export async function markAttendance(image, classroomId, sessionDate) {
  return request('/attendance/mark', {
    method: 'POST',
    body: JSON.stringify({ image, classroom_id: classroomId, session_date: sessionDate }),
  });
}

export async function getAttendanceLog(classroomId, date) {
  return request(`/attendance/log?classroom_id=${encodeURIComponent(classroomId)}&date=${date}`);
}

export async function patchAttendance(attendanceId, status, note = null) {
  const body = { status };
  if (note) body.note = note;
  return request(`/attendance/${attendanceId}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

// --- Risk ---

export async function getStudentRisk(studentId) {
  return request(`/students/${studentId}/risk`);
}

export async function listRiskFlags(riskLevel = null, page = 1, pageSize = 50) {
  let path = `/risk?page=${page}&page_size=${pageSize}`;
  if (riskLevel) path += `&risk_level=${riskLevel}`;
  return request(path);
}

export async function recomputeRisk(studentId) {
  return request(`/students/${studentId}/risk/recompute`, { method: 'POST' });
}

// --- Export ---

export async function exportReport(classroomId, fromDate, toDate, format = 'csv') {
  return request(
    `/export/report?classroom_id=${encodeURIComponent(classroomId)}&from_date=${fromDate}&to_date=${toDate}&format=${format}`
  );
}
