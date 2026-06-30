import { useState, useEffect } from 'react';

const BASE_URL = '/api/v1';

function Settings({ auth, onThemeChange }) {
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  // Profile state
  const [name, setName] = useState(auth.name || '');
  const [phone, setPhone] = useState('');
  const [profileMsg, setProfileMsg] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // Theme
  const [theme, setTheme] = useState(auth.theme || 'light');

  // Student-specific
  const [usn, setUsn] = useState('');
  const [usnLocked, setUsnLocked] = useState(false);
  const [extracurricular, setExtracurricular] = useState([]);
  const [newActivity, setNewActivity] = useState('');

  const headers = { Authorization: `Bearer ${auth.token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const endpoint = auth.role === 'student' ? `${BASE_URL}/student-portal/profile` : `${BASE_URL}/auth/profile`;
      const res = await fetch(endpoint, { headers: { Authorization: `Bearer ${auth.token}` } });
      if (res.ok) {
        const data = await res.json();
        setName(data.name || '');
        setPhone(data.phone || '');
        setTheme(data.theme || 'light');
        if (auth.role === 'student') {
          setUsn(data.usn || '');
          setUsnLocked(data.usn_locked || false);
          setExtracurricular(data.extracurricular || []);
        }
      }
    } catch {}
  }

  async function handlePasswordChange(e) {
    e.preventDefault();
    setMessage(null);
    if (newPw !== confirmPw) { setMessage({ type: 'error', text: 'Passwords do not match' }); return; }
    if (newPw.length < 6) { setMessage({ type: 'error', text: 'Password must be at least 6 characters' }); return; }

    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/auth/change-password`, {
        method: 'POST', headers,
        body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({ type: 'success', text: 'Password changed successfully' });
        setCurrentPw(''); setNewPw(''); setConfirmPw('');
      } else {
        setMessage({ type: 'error', text: data.detail?.message || 'Failed' });
      }
    } catch { setMessage({ type: 'error', text: 'Network error' }); }
    setLoading(false);
  }

  async function handleProfileSave() {
    setProfileMsg(null);
    setProfileLoading(true);
    try {
      if (auth.role === 'student') {
        const res = await fetch(`${BASE_URL}/student-portal/profile`, {
          method: 'PATCH', headers,
          body: JSON.stringify({ name: name.trim(), phone: phone.trim(), usn: usnLocked ? undefined : usn.trim() || undefined }),
        });
        const data = await res.json();
        if (res.ok) {
          setProfileMsg({ type: 'success', text: 'Profile updated' });
          if (data.usn_locked) setUsnLocked(true);
        } else {
          setProfileMsg({ type: 'error', text: data.detail?.message || data.detail || 'Failed' });
        }
      } else {
        const res = await fetch(`${BASE_URL}/auth/profile`, {
          method: 'PATCH', headers,
          body: JSON.stringify({ name: name.trim(), phone: phone.trim() }),
        });
        if (res.ok) {
          setProfileMsg({ type: 'success', text: 'Profile updated' });
        } else {
          const data = await res.json();
          setProfileMsg({ type: 'error', text: data.detail?.message || 'Failed' });
        }
      }
    } catch { setProfileMsg({ type: 'error', text: 'Network error' }); }
    setProfileLoading(false);
  }

  async function handleThemeToggle() {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    try {
      await fetch(`${BASE_URL}/auth/theme`, {
        method: 'PATCH', headers,
        body: JSON.stringify({ theme: newTheme }),
      });
      // Update local storage
      const stored = JSON.parse(localStorage.getItem('vista_auth') || '{}');
      stored.theme = newTheme;
      localStorage.setItem('vista_auth', JSON.stringify(stored));
      if (onThemeChange) onThemeChange(newTheme);
    } catch {}
  }

  async function handleAddActivity() {
    if (!newActivity.trim()) return;
    const updated = [...extracurricular, { name: newActivity.trim(), year: new Date().getFullYear().toString() }];
    try {
      const res = await fetch(`${BASE_URL}/student-portal/extracurricular`, {
        method: 'PUT', headers,
        body: JSON.stringify({ activities: updated }),
      });
      if (res.ok) {
        setExtracurricular(updated);
        setNewActivity('');
      }
    } catch {}
  }

  async function handleRemoveActivity(idx) {
    const updated = extracurricular.filter((_, i) => i !== idx);
    try {
      await fetch(`${BASE_URL}/student-portal/extracurricular`, {
        method: 'PUT', headers,
        body: JSON.stringify({ activities: updated }),
      });
      setExtracurricular(updated);
    } catch {}
  }

  return (
    <div>
      <div className="v-page-header">
        <div>
          <h2 className="v-page-title">Settings</h2>
          <p className="v-page-subtitle">Manage your account and preferences</p>
        </div>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s5)',maxWidth:'900px'}}>
        {/* Profile Info — Editable */}
        <div className="v-card">
          <h4 style={{fontSize:'14px',fontWeight:600,marginBottom:'var(--s4)'}}>Profile</h4>
          <div style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
            <div>
              <label className="v-label">Name</label>
              <input className="v-input" value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div>
              <label className="v-label">Email</label>
              <input className="v-input" value={auth.email || ''} disabled style={{opacity:0.6}} />
              <span style={{fontSize:'10px',color:'var(--text-muted)'}}>Email cannot be changed</span>
            </div>
            <div>
              <label className="v-label">Phone</label>
              <input className="v-input" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+91 9876543210" />
            </div>
            {auth.role === 'student' && (
              <div>
                <label className="v-label">USN (University Seat Number) {usnLocked && <span style={{color:'var(--warning)',fontSize:'10px'}}>🔒 Locked</span>}</label>
                <input
                  className="v-input"
                  value={usn}
                  onChange={e => setUsn(e.target.value)}
                  disabled={usnLocked}
                  placeholder="e.g. 1DA23AI043"
                  style={usnLocked ? {opacity:0.6} : {}}
                />
                {!usnLocked && <span style={{fontSize:'10px',color:'var(--warning)'}}>⚠️ USN can only be set once</span>}
              </div>
            )}
            <div style={{display:'grid',gridTemplateColumns:'auto auto',gap:'var(--s2)',fontSize:'12px',color:'var(--text-muted)'}}>
              <span>Role:</span><span style={{textTransform:'uppercase',fontWeight:600}}>{auth.role}</span>
              <span>User ID:</span><span style={{fontFamily:'var(--mono)',fontSize:'11px'}}>{auth.user_id}</span>
            </div>
            {profileMsg && (
              <p style={{fontSize:'12px',color: profileMsg.type === 'error' ? 'var(--danger)' : 'var(--success)'}}>{profileMsg.text}</p>
            )}
            <button className="v-btn v-btn-primary" style={{alignSelf:'flex-start'}} onClick={handleProfileSave} disabled={profileLoading}>
              {profileLoading ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </div>

        {/* Theme + Preferences */}
        <div style={{display:'flex',flexDirection:'column',gap:'var(--s4)'}}>
          <div className="v-card">
            <h4 style={{fontSize:'14px',fontWeight:600,marginBottom:'var(--s4)'}}>Appearance</h4>
            <div style={{display:'flex',alignItems:'center',gap:'var(--s4)'}}>
              <span style={{fontSize:'13px'}}>Theme:</span>
              <button
                className={`v-btn ${theme === 'light' ? 'v-btn-primary' : 'v-btn-secondary'}`}
                style={{fontSize:'12px',padding:'6px 12px'}}
                onClick={handleThemeToggle}
              >
                {theme === 'light' ? '☀️ Light Mode' : '🌙 Dark Mode'}
              </button>
            </div>
            <p style={{fontSize:'11px',color:'var(--text-muted)',marginTop:'var(--s2)'}}>
              Toggle between light and dark visual modes
            </p>
          </div>

          {/* Password Change */}
          <div className="v-card">
            <h4 style={{fontSize:'14px',fontWeight:600,marginBottom:'var(--s4)'}}>Change Password</h4>
            <form onSubmit={handlePasswordChange} style={{display:'flex',flexDirection:'column',gap:'var(--s3)'}}>
              <input className="v-input" type="password" value={currentPw} onChange={e => setCurrentPw(e.target.value)} placeholder="Current password" required />
              <input className="v-input" type="password" value={newPw} onChange={e => setNewPw(e.target.value)} placeholder="New password" required minLength={6} />
              <input className="v-input" type="password" value={confirmPw} onChange={e => setConfirmPw(e.target.value)} placeholder="Confirm new password" required />
              {message && (
                <p style={{fontSize:'12px',color: message.type === 'error' ? 'var(--danger)' : 'var(--success)'}}>{message.text}</p>
              )}
              <button className="v-btn v-btn-primary" style={{alignSelf:'flex-start'}} disabled={loading}>
                {loading ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Extracurricular — Students only */}
      {auth.role === 'student' && (
        <div className="v-card" style={{marginTop:'var(--s5)',maxWidth:'900px'}}>
          <h4 style={{fontSize:'14px',fontWeight:600,marginBottom:'var(--s4)'}}>Extracurricular Activities</h4>
          {extracurricular.length > 0 ? (
            <div style={{display:'flex',flexDirection:'column',gap:'var(--s2)',marginBottom:'var(--s3)'}}>
              {extracurricular.map((act, i) => (
                <div key={i} style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'var(--s2) var(--s3)',background:'var(--bg-secondary)',borderRadius:'var(--r-sm)'}}>
                  <span style={{fontSize:'13px'}}>{act.name} {act.year && <span style={{color:'var(--text-muted)'}}>({act.year})</span>}</span>
                  <button style={{fontSize:'12px',color:'var(--danger)',background:'none',border:'none',cursor:'pointer'}} onClick={() => handleRemoveActivity(i)}>✕</button>
                </div>
              ))}
            </div>
          ) : (
            <p style={{fontSize:'13px',color:'var(--text-muted)',marginBottom:'var(--s3)'}}>No activities added yet</p>
          )}
          <div style={{display:'flex',gap:'var(--s2)'}}>
            <input className="v-input" style={{flex:1}} value={newActivity} onChange={e => setNewActivity(e.target.value)} placeholder="e.g. Basketball Team Captain 2025" onKeyDown={e => e.key === 'Enter' && handleAddActivity()} />
            <button className="v-btn v-btn-secondary" onClick={handleAddActivity}>Add</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Settings;
