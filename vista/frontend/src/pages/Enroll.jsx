import { useState } from 'react';
import { getStudents } from '../api/client';
import './Enroll.css';

const BASE_URL = '/api/v1';

function Enroll({ auth }) {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useState(() => {
    getStudents().then((res) => setStudents(res.students)).catch(() => {});
  }, []);

  async function handleEnroll(e) {
    e.preventDefault();
    if (!selectedStudent) { setError('Select a student'); return; }
    if (files.length === 0) { setError('Upload at least 1 image'); return; }
    if (files.length > 5) { setError('Maximum 5 images'); return; }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Convert files to base64
      const images = await Promise.all(
        Array.from(files).map((file) => {
          return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
              const base64 = reader.result.split(',')[1];
              resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
          });
        })
      );

      const token = JSON.parse(localStorage.getItem('vista_auth'))?.token;
      const res = await fetch(`${BASE_URL}/students/${selectedStudent}/enroll`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ images }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message || 'Enrollment failed');
      }

      const data = await res.json();
      setResult(data);
      setFiles([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="enroll-page">
      <h2>Face Enrollment</h2>
      <p className="enroll-desc">
        Upload 3–5 face photos of a student to register their face for automated attendance.
      </p>

      <form onSubmit={handleEnroll} className="enroll-form">
        <div className="form-group">
          <label htmlFor="student-select">Student</label>
          <select
            id="student-select"
            value={selectedStudent}
            onChange={(e) => setSelectedStudent(e.target.value)}
          >
            <option value="">Select a student...</option>
            {students.map((s) => (
              <option key={s.student_id} value={s.student_id}>
                {s.student_id} — {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="face-images">Face Photos (1–5 images)</label>
          <input
            id="face-images"
            type="file"
            accept="image/jpeg,image/png"
            multiple
            onChange={(e) => setFiles(e.target.files)}
          />
          {files.length > 0 && (
            <p className="file-count">{files.length} file(s) selected</p>
          )}
        </div>

        {error && <div className="error-msg" role="alert">{error}</div>}

        <button type="submit" className="enroll-btn" disabled={loading}>
          {loading ? 'Enrolling...' : 'Enroll Face'}
        </button>
      </form>

      {result && (
        <div className="enroll-result success">
          <h3>✓ Enrollment Successful</h3>
          <p>Student: {result.student_name} ({result.student_id})</p>
          <p>Images processed: {result.images_processed}</p>
          <p>Quality: {result.embedding_quality}</p>
        </div>
      )}
    </div>
  );
}

export default Enroll;
