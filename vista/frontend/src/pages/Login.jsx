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
    <div className="login-page">
      <div className="login-left">
        <div className="login-brand">
          <div className="login-logo">V</div>
          <h1>VISTA</h1>
          <p>AI Academic Intelligence Platform</p>
        </div>
        <div className="login-features">
          <div className="login-feature">
            <span className="login-feature-icon">📸</span>
            <div>
              <strong>Face Recognition</strong>
              <span>Automated attendance via AI</span>
            </div>
          </div>
          <div className="login-feature">
            <span className="login-feature-icon">⚡</span>
            <div>
              <strong>Risk Prediction</strong>
              <span>Identify at-risk students early</span>
            </div>
          </div>
          <div className="login-feature">
            <span className="login-feature-icon">🧠</span>
            <div>
              <strong>Explainable AI</strong>
              <span>SHAP-powered insights</span>
            </div>
          </div>
        </div>
      </div>

      <div className="login-right">
        <div className="login-form-container">
          <h2>Welcome back</h2>
          <p className="login-form-subtitle">Sign in to your workspace</p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="login-field">
              <label className="v-label" htmlFor="email">Email</label>
              <input
                className="v-input"
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@institution.edu"
                required
                autoComplete="email"
              />
            </div>

            <div className="login-field">
              <label className="v-label" htmlFor="password">Password</label>
              <input
                className="v-input"
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
            </div>

            {error && <div className="login-error">{error}</div>}

            <button className="v-btn v-btn-primary login-submit" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="login-demo">
            <span>Demo accounts</span>
            <div className="login-demo-accounts">
              <code>admin@vista.local</code>
              <code>gowrishankar@vista.local</code>
              <code>kushal@vista.local</code>
              <code>rajeshwari@vista.local</code>
              <span className="login-demo-pw">password: admin123 / hos123 / teacher123 / mentor123</span>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .login-page {
          min-height: 100vh;
          display: grid;
          grid-template-columns: 1fr 1fr;
        }
        .login-left {
          background: var(--gray-900);
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: var(--s16);
          position: relative;
          overflow: hidden;
        }
        .login-left::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle at 30% 50%, rgba(79,70,229,0.12) 0%, transparent 50%),
                      radial-gradient(circle at 70% 80%, rgba(6,182,212,0.08) 0%, transparent 40%);
        }
        .login-brand { position: relative; z-index: 1; margin-bottom: var(--s12); }
        .login-logo {
          width: 48px; height: 48px;
          background: linear-gradient(135deg, var(--primary), var(--accent));
          border-radius: var(--r-lg);
          display: flex; align-items: center; justify-content: center;
          font-size: 20px; font-weight: 700; color: white;
          margin-bottom: var(--s4);
        }
        .login-brand h1 { font-size: 28px; font-weight: 700; color: white; letter-spacing: -0.03em; }
        .login-brand p { font-size: 14px; color: var(--gray-400); margin-top: var(--s1); }
        .login-features { position: relative; z-index: 1; display: flex; flex-direction: column; gap: var(--s5); }
        .login-feature {
          display: flex; align-items: flex-start; gap: var(--s3);
          padding: var(--s4);
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.06);
          border-radius: var(--r-md);
        }
        .login-feature-icon { font-size: 20px; margin-top: 2px; }
        .login-feature strong { display: block; font-size: 13px; color: white; font-weight: 600; }
        .login-feature span { font-size: 12px; color: var(--gray-400); }
        .login-right {
          display: flex; align-items: center; justify-content: center;
          padding: var(--s8);
          background: var(--bg);
        }
        .login-form-container { width: 100%; max-width: 360px; }
        .login-form-container h2 { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }
        .login-form-subtitle { font-size: 13px; color: var(--text-muted); margin-top: var(--s1); margin-bottom: var(--s6); }
        .login-form { display: flex; flex-direction: column; gap: var(--s4); }
        .login-field { display: flex; flex-direction: column; }
        .login-error {
          font-size: 12px; color: var(--danger);
          background: var(--danger-light);
          padding: var(--s2) var(--s3);
          border-radius: var(--r-sm);
        }
        .login-submit { width: 100%; padding: 10px; font-size: 14px; margin-top: var(--s2); }
        .login-demo {
          margin-top: var(--s8);
          padding-top: var(--s5);
          border-top: 1px solid var(--border);
        }
        .login-demo > span { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
        .login-demo-accounts { margin-top: var(--s2); display: flex; flex-direction: column; gap: 3px; }
        .login-demo-accounts code {
          font-size: 11px; color: var(--text-secondary); font-family: var(--mono);
          background: var(--bg-secondary); padding: 2px 6px; border-radius: 3px; width: fit-content;
        }
        .login-demo-pw { font-size: 10px; color: var(--text-muted); margin-top: var(--s1); }
        @media (max-width: 768px) {
          .login-page { grid-template-columns: 1fr; }
          .login-left { display: none; }
        }
      `}</style>
    </div>
  );
}

export default Login;
