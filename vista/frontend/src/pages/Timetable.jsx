import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function Timetable({ auth }) {
  const [timetable, setTimetable] = useState({});
  const [classSection, setClassSection] = useState('class-aiml-4a');
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${auth.token}` };
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  useEffect(() => { loadTimetable(); }, [classSection]);

  async function loadTimetable() {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/timetable/${classSection}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setTimetable(data.timetable || {});
      }
    } catch {}
    setLoading(false);
  }

  if (loading) return <div className="v-loading">Loading timetable...</div>;

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Timetable</h2>
          <p className="v-page-subtitle">Weekly class schedule</p>
        </div>
        {['admin','hos','hop'].includes(auth.role) && (
          <select className="v-select" style={{width:'200px'}} value={classSection} onChange={e => setClassSection(e.target.value)}>
            <option value="class-aiml-4a">AIML 4A</option>
            <option value="class-aiml-3a">AIML 3A</option>
            <option value="class-cse-3a">CSE 3A</option>
          </select>
        )}
      </div>

      <div className="v-card" style={{overflowX:'auto'}}>
        <table className="v-table" style={{minWidth:'700px'}}>
          <thead>
            <tr>
              <th style={{width:'100px'}}>Day</th>
              <th>Periods</th>
            </tr>
          </thead>
          <tbody>
            {days.map(day => (
              <tr key={day}>
                <td style={{fontWeight:600,fontSize:'13px'}}>{day}</td>
                <td>
                  {(!timetable[day] || timetable[day].length === 0) ? (
                    <span style={{color:'var(--text-muted)',fontSize:'12px'}}>No classes scheduled</span>
                  ) : (
                    <div style={{display:'flex',gap:'var(--s2)',flexWrap:'wrap'}}>
                      {timetable[day].map((slot, i) => (
                        <div key={i} style={{
                          background:'var(--primary-light)',border:'1px solid var(--border)',
                          borderRadius:'var(--r-sm)',padding:'6px 10px',fontSize:'12px',minWidth:'140px',
                        }}>
                          <div style={{fontWeight:600,color:'var(--primary)'}}>{slot.subject_code}</div>
                          <div style={{color:'var(--text-secondary)'}}>{slot.start_time} - {slot.end_time}</div>
                          <div style={{color:'var(--text-muted)',fontSize:'11px'}}>{slot.teacher_name} {slot.room && `· ${slot.room}`}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Timetable;
