import { NavLink, useNavigate } from 'react-router-dom';
import '../components/Layout.css';

/**
 * Shared layout shell for all roles.
 * Each role passes its own title, navigation items, and accent color.
 */
function RoleLayout({ auth, onLogout, title, subtitle, navItems, accentColor, children }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="sidebar" aria-label="Main navigation" style={{ background: accentColor || '#1a1a2e' }}>
        <div className="sidebar-brand">
          <h1>VISTA</h1>
          <span className="sidebar-subtitle">{subtitle || title}</span>
        </div>

        <ul className="sidebar-nav">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink to={item.path} end={item.exact} className={({ isActive }) => isActive ? 'active' : ''}>
                {item.icon} {item.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{auth.name}</span>
            <span className="user-role">{auth.role.toUpperCase()}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </nav>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default RoleLayout;
