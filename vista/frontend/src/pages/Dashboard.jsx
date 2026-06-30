import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, DonutChart, TrendLine } from '../components/Charts';

const BASE_URL = '/api/v1';

function Dashboard({ auth }) {
  const navigate = useNavigate();
  const [tree, setTree] = useState([]);
  const [flags, setFlags] = useState([]);
  const [charts, setCharts] = useState({ trend: [], risk: null, subjects: [] });
  const [loading, setLoading] = useState(true);

  // Modals
  const [modal, setModal] = useState(null); // {type, parentId, ...}
  const [formData, setFormData] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const headers = { Authorization: `Bearer ${auth.token}`, 'Content-Type': 'application/json' };

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [treeRes, riskRes, trendRes, riskDistRes, subjRes] = await Promise.all([
        fetch(`${BASE_URL}/admin/org-tree`, { headers }).then(r => r.ok ? r.json() : { tree: [] }),
        fetch(`${BASE_URL}/risk`, { headers }).then(r => r.ok ? r.json() : { flags: [] }),
        fetch(`${BASE_URL}/dashboard/charts/attendance-trend`, { headers }).then(r => r.ok ? r.json() : { trend: [] }),
        fetch(`${BASE_URL}/dashboard/charts/risk-distribution`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${BASE_URL}/dashboard/charts/subject-performance`, { headers }).then(r => r.ok ? r.json() : { subjects: [] }),
      ]);
      setTree(treeRes.tree || []);
      setFlags(riskRes.flags || []);
      setCharts({ trend: trendRes.trend || [], risk: riskDistRes, subjects: subjRes.subjects || [] });
    } catch {}
    setLoading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      let url, body;
      switch (modal.type) {
        case 'school':
          url = `${BASE_URL}/admin/schools`;
          body = { name: formData.name, code: formData.code };
          break;
        case 'department':
          url = `${BASE_URL}/admin/departments`;
          body = { name: formData.name, code: formData.code, school_id: modal.schoolId };
          break;
        case 'class':
          url = `${BASE_URL}/admin/class-sections`;
          body = { name: formData.name, code: formData.code, department_id: modal.deptId, semester: formData.semester || null };
          break;
        case 'subject':
          url = `${BASE_URL}/admin/subjects`;
          body = { name: formData.name, code: formData.code, department_id: modal.deptId, semester: formData.semester || null };
          break;
        case 'user':
          url = `${BASE_URL}/admin/users`;
          body = {
            name: formData.name, email: formData.email, password: formData.password || 'vista123',
            role: formData.role, school_id: modal.schoolId || null, department_id: modal.deptId || null,
          };
          break;
      }
      const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) });
      if (res.ok) {
        setModal(null); setFormData({});
        loadData();
      } else {
        const err = await res.json();
        alert(err.detail?.message || err.detail || 'Failed');
      }
    } catch { alert('Network error'); }
    setSubmitting(false);
  }

  if (loading) return <div className="v-loading">Loading...</div>;

  const high = flags.filter(f => f.risk_level === 'high');
  const medium = flags.filter(f => f.risk_level === 'medium');

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Dashboard</h2>
          <p className="v-page-subtitle">Welcome, {auth.name} — Organization Management</p>
        </div>
      </div>

      {/* Risk summary strip */}
      {(high.length > 0 || medium.length > 0) && (
        <div style={{display:'flex',gap:'var(--s3)',marginBottom:'var(--s5)'}}>
          {high.length > 0 && (
            <div className="v-card" style={{padding:'var(--s3) var(--s4)',cursor:'pointer',borderLeft:'3px solid var(--danger)'}} onClick={() => navigate('/risk')}>
              <span style={{fontSize:'20px',fontWeight:700,color:'var(--danger)'}}>{high.length}</span>
              <span style={{fontSize:'12px',color:'var(--text-muted)',marginLeft:'var(--s2)'}}>HIGH risk students</span>
            </div>
          )}
          {medium.length > 0 && (
            <div className="v-card" style={{padding:'var(--s3) var(--s4)',cursor:'pointer',borderLeft:'3px solid var(--warning)'}} onClick={() => navigate('/risk')}>
              <span style={{fontSize:'20px',fontWeight:700,color:'var(--warning)'}}>{medium.length}</span>
              <span style={{fontSize:'12px',color:'var(--text-muted)',marginLeft:'var(--s2)'}}>MEDIUM risk students</span>
            </div>
          )}
        </div>
      )}

      {/* Organization Tree */}
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'var(--s4)'}}>
        <h3 style={{fontSize:'15px',fontWeight:600}}>Institution Structure</h3>
        {auth.role === 'admin' && (
          <button className="v-btn v-btn-primary" onClick={() => { setModal({type:'school'}); setFormData({}); }}>
            + Add School
          </button>
        )}
      </div>

      {tree.length === 0 ? (
        <div className="v-card" style={{textAlign:'center',padding:'var(--s8)'}}>
          <p style={{color:'var(--text-muted)'}}>No schools configured yet. Add one to get started.</p>
        </div>
      ) : (
        <div style={{display:'flex',flexDirection:'column',gap:'var(--s4)'}}>
          {tree.map(school => (
            <div key={school.id} className="v-card" style={{padding:0,overflow:'hidden'}}>
              {/* School header */}
              <div style={{padding:'var(--s4) var(--s5)',background:'var(--bg-secondary)',borderBottom:'1px solid var(--border)',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <div>
                  <h4 style={{fontSize:'14px',fontWeight:700}}>🏫 {school.name}</h4>
                  <span style={{fontSize:'11px',color:'var(--text-muted)'}}>Code: {school.code} · {school.departments.length} department(s)</span>
                </div>
                <div style={{display:'flex',gap:'var(--s2)'}}>
                  <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => { setModal({type:'department', schoolId: school.id}); setFormData({}); }}>+ Dept</button>
                  <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => { setModal({type:'user', schoolId: school.id}); setFormData({role:'hos'}); }}>+ User</button>
                </div>
              </div>

              {/* School-level users */}
              {school.users.length > 0 && (
                <div style={{padding:'var(--s3) var(--s5)',borderBottom:'1px solid var(--border)'}}>
                  <div style={{display:'flex',gap:'var(--s2)',flexWrap:'wrap'}}>
                    {school.users.map(u => (
                      <span key={u.id} className="v-badge v-badge-info" style={{fontSize:'11px'}}>{u.role.toUpperCase()}: {u.name}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Departments */}
              {school.departments.map(dept => (
                <div key={dept.id} style={{padding:'var(--s4) var(--s5)',borderBottom:'1px solid var(--border)'}}>
                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'var(--s3)'}}>
                    <div>
                      <h5 style={{fontSize:'13px',fontWeight:600}}>📁 {dept.name} <span style={{color:'var(--text-muted)',fontWeight:400}}>({dept.code})</span></h5>
                    </div>
                    <div style={{display:'flex',gap:'var(--s2)'}}>
                      <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => { setModal({type:'class', deptId: dept.id}); setFormData({}); }}>+ Class</button>
                      <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => { setModal({type:'subject', deptId: dept.id}); setFormData({}); }}>+ Subject</button>
                      <button className="v-btn v-btn-sm v-btn-secondary" onClick={() => { setModal({type:'user', schoolId: school.id, deptId: dept.id}); setFormData({role:'hop'}); }}>+ User</button>
                    </div>
                  </div>

                  {/* Classes */}
                  {dept.classes.length > 0 && (
                    <div style={{marginBottom:'var(--s3)'}}>
                      <span style={{fontSize:'11px',fontWeight:600,color:'var(--text-muted)',textTransform:'uppercase'}}>Classes</span>
                      <div style={{display:'flex',gap:'var(--s2)',flexWrap:'wrap',marginTop:'var(--s1)'}}>
                        {dept.classes.map(c => (
                          <span key={c.id} style={{
                            fontSize:'12px',padding:'4px 10px',borderRadius:'var(--r-sm)',
                            background:'var(--primary-light)',color:'var(--primary)',fontWeight:500,
                          }}>
                            {c.code} {c.semester && <span style={{opacity:0.7}}>· Sem {c.semester}</span>}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Subjects */}
                  {dept.subjects.length > 0 && (
                    <div style={{marginBottom:'var(--s3)'}}>
                      <span style={{fontSize:'11px',fontWeight:600,color:'var(--text-muted)',textTransform:'uppercase'}}>Subjects</span>
                      <div style={{display:'flex',gap:'var(--s2)',flexWrap:'wrap',marginTop:'var(--s1)'}}>
                        {dept.subjects.map(s => (
                          <span key={s.id} style={{
                            fontSize:'11px',padding:'3px 8px',borderRadius:'var(--r-sm)',
                            background:'var(--bg-hover)',color:'var(--text-secondary)',border:'1px solid var(--border)',
                          }}>
                            {s.code}: {s.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Users */}
                  {dept.users.length > 0 && (
                    <div>
                      <span style={{fontSize:'11px',fontWeight:600,color:'var(--text-muted)',textTransform:'uppercase'}}>Faculty</span>
                      <div style={{display:'flex',gap:'var(--s2)',flexWrap:'wrap',marginTop:'var(--s1)'}}>
                        {dept.users.map(u => (
                          <span key={u.id} style={{
                            fontSize:'11px',padding:'3px 8px',borderRadius:'var(--r-sm)',
                            background: u.role === 'hop' ? 'rgba(245,158,11,0.1)' : u.role === 'mentor' ? 'rgba(16,185,129,0.1)' : 'var(--bg-hover)',
                            color: u.role === 'hop' ? 'var(--warning)' : u.role === 'mentor' ? 'var(--success)' : 'var(--text-secondary)',
                            border:'1px solid var(--border)',
                          }}>
                            {u.role.toUpperCase()}: {u.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {school.departments.length === 0 && (
                <div style={{padding:'var(--s5)',textAlign:'center',color:'var(--text-muted)',fontSize:'13px'}}>
                  No departments yet. Click "+ Dept" to add one.
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Analytics Charts */}
      <div style={{marginTop:'var(--s6)',marginBottom:'var(--s5)'}}>
        <h3 style={{fontSize:'15px',fontWeight:600,marginBottom:'var(--s4)'}}>Analytics</h3>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:'var(--s4)'}}>
          {/* Attendance Trend */}
          <div className="v-card">
            <h4 style={{fontSize:'12px',fontWeight:600,color:'var(--text-muted)',marginBottom:'var(--s3)'}}>ATTENDANCE TREND (8 WEEKS)</h4>
            {charts.trend.length > 0 ? (
              <TrendLine data={charts.trend.map(t => ({ label: t.week, value: t.attendance_pct }))} valueKey="value" height={50} />
            ) : <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No data</p>}
          </div>

          {/* Risk Distribution */}
          <div className="v-card">
            <h4 style={{fontSize:'12px',fontWeight:600,color:'var(--text-muted)',marginBottom:'var(--s3)'}}>RISK DISTRIBUTION</h4>
            {charts.risk && charts.risk.distribution ? (
              <DonutChart data={[
                { label: 'High', value: charts.risk.distribution.high },
                { label: 'Medium', value: charts.risk.distribution.medium },
                { label: 'Low', value: charts.risk.distribution.low },
              ]} />
            ) : <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No data</p>}
          </div>

          {/* Subject Performance */}
          <div className="v-card">
            <h4 style={{fontSize:'12px',fontWeight:600,color:'var(--text-muted)',marginBottom:'var(--s3)'}}>SUBJECT PERFORMANCE</h4>
            {charts.subjects.length > 0 ? (
              <BarChart data={charts.subjects.map(s => ({ label: s.subject, value: s.average_pct }))} labelKey="label" valueKey="value" />
            ) : <p style={{fontSize:'12px',color:'var(--text-muted)'}}>No data</p>}
          </div>
        </div>
      </div>

      {/* Modal */}
      {modal && (
        <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.5)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:1000}} onClick={() => setModal(null)}>
          <div className="v-card" style={{width:'400px',maxWidth:'90vw'}} onClick={e => e.stopPropagation()}>
            <h4 style={{fontSize:'15px',fontWeight:700,marginBottom:'var(--s4)'}}>
              {modal.type === 'school' && '🏫 Add New School'}
              {modal.type === 'department' && '📁 Add New Department'}
              {modal.type === 'class' && '🎓 Add New Class Section'}
              {modal.type === 'subject' && '📚 Add New Subject'}
              {modal.type === 'user' && '👤 Add New User'}
            </h4>
            <form onSubmit={handleSubmit} style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
              {modal.type === 'user' ? (
                <>
                  <div>
                    <label className="v-label">Full Name</label>
                    <input className="v-input" required value={formData.name || ''} onChange={e => setFormData({...formData, name: e.target.value})} />
                  </div>
                  <div>
                    <label className="v-label">Email</label>
                    <input className="v-input" type="email" required value={formData.email || ''} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="name@vista.local" />
                  </div>
                  <div>
                    <label className="v-label">Password</label>
                    <input className="v-input" value={formData.password || ''} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="Default: vista123" />
                  </div>
                  <div>
                    <label className="v-label">Role</label>
                    <select className="v-select" value={formData.role || 'teacher'} onChange={e => setFormData({...formData, role: e.target.value})}>
                      {auth.role === 'admin' && <option value="hos">HOS (Head of School)</option>}
                      {['admin','hos'].includes(auth.role) && <option value="hop">HOP (Head of Program)</option>}
                      <option value="mentor">Mentor</option>
                      <option value="teacher">Teacher</option>
                    </select>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="v-label">Name</label>
                    <input className="v-input" required value={formData.name || ''} onChange={e => setFormData({...formData, name: e.target.value})} placeholder={modal.type === 'school' ? 'School of Computer Science' : modal.type === 'department' ? 'Artificial Intelligence & ML' : modal.type === 'class' ? 'AIML 4th Year A' : 'Machine Learning'} />
                  </div>
                  <div>
                    <label className="v-label">Code</label>
                    <input className="v-input" required value={formData.code || ''} onChange={e => setFormData({...formData, code: e.target.value})} placeholder={modal.type === 'school' ? 'CSE' : modal.type === 'department' ? 'AIML' : modal.type === 'class' ? 'AIML-4A' : 'ML101'} />
                  </div>
                  {(modal.type === 'class' || modal.type === 'subject') && (
                    <div>
                      <label className="v-label">Semester (optional)</label>
                      <input className="v-input" value={formData.semester || ''} onChange={e => setFormData({...formData, semester: e.target.value})} placeholder="7" />
                    </div>
                  )}
                </>
              )}
              <div style={{display:'flex',gap:'var(--s3)',marginTop:'var(--s2)'}}>
                <button type="submit" className="v-btn v-btn-primary" disabled={submitting}>
                  {submitting ? 'Creating...' : 'Create'}
                </button>
                <button type="button" className="v-btn v-btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
