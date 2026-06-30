import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import NotificationBell from '../components/NotificationBell';

/**
 * Enterprise Layout Shell — responsive sidebar, role-specific accent.
 * Uses VISTA Design System (v-* classes).
 */
function RoleLayout({ auth, onLogout, title, subtitle, navItems, children }) {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className={`v-layout ${mobileMenuOpen ? 'v-mobile-menu-open' : ''}`}>
      {/* Mobile menu toggle */}
      <button className="v-mobile-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} aria-label="Toggle menu">
        {mobileMenuOpen ? '✕' : '☰'}
      </button>

      {/* Backdrop for mobile */}
      {mobileMenuOpen && <div className="v-mobile-backdrop" onClick={() => setMobileMenuOpen(false)} />}

      <nav className="v-sidebar" aria-label="Main navigation">
        <div className="v-sidebar-brand">
          <h1>VISTA</h1>
          <span className="v-subtitle">{subtitle || title}</span>
        </div>

        <ul className="v-sidebar-nav">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink to={item.path} end={item.exact} className={({ isActive }) => isActive ? 'active' : ''} onClick={() => setMobileMenuOpen(false)}>
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="v-sidebar-footer">
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
            <div>
              <div className="v-user-name">{auth.name}</div>
              <div className="v-user-role">{auth.role}</div>
            </div>
            <NotificationBell auth={auth} />
          </div>
          <div style={{display:'flex',gap:'var(--s2)',marginTop:'var(--s3)'}}>
            <a href="/settings" className="v-logout-btn" style={{textAlign:'center',textDecoration:'none',flex:1}} onClick={() => setMobileMenuOpen(false)}>⚙️ Settings</a>
            <button className="v-logout-btn" style={{flex:1}} onClick={handleLogout}>Sign Out</button>
          </div>
        </div>
      </nav>

      <main className="v-main">
        {children}
      </main>
    </div>
  );
}

export default RoleLayout;
