import { useState } from 'react';
import { login } from '../api/client';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(email, password);
      onLogin(data);
    } catch (err) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f6f8fa' }}>
      <div style={{ width: '100%', maxWidth: '320px' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 600 }}>VISTA</h1>
          <p style={{ fontSize: '13px', color: '#656d76', marginTop: '4px' }}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} style={{ border: '1px solid #d1d5db', borderRadius: '6px', padding: '20px', background: '#fff' }}>
          <div style={{ marginBottom: '12px' }}>
            <label className="v-label">Email address</label>
            <input className="v-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
          </div>
          <div style={{ marginBottom: '16px' }}>
            <label className="v-label">Password</label>
            <input className="v-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
          </div>
          {error && <p style={{ fontSize: '12px', color: '#cf222e', marginBottom: '12px' }}>{error}</p>}
          <button className="v-btn v-btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '8px' }} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: '12px', color: '#8b949e', marginTop: '16px' }}>
          Demo: admin@vista.local / admin123
        </p>
      </div>
    </div>
  );
}

export default Login;
