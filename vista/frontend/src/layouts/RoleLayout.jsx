import { NavLink, useNavigate } from 'react-router-dom';

/**
 * Enterprise Layout Shell — Dark theme, role-specific accent.
 * Uses VISTA Design System (v-* classes).
 */
function RoleLayout({ auth, onLogout, title, subtitle, navItems, children }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="v-layout">
      <nav className="v-sidebar" aria-label="Main navigation">
        <div className="v-sidebar-brand">
          <h1>VISTA</h1>
          <span className="v-subtitle">{subtitle || title}</span>
        </div>

        <ul className="v-sidebar-nav">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink to={item.path} end={item.exact} className={({ isActive }) => isActive ? 'active' : ''}>
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="v-sidebar-footer">
          <div className="v-user-name">{auth.name}</div>
          <div className="v-user-role">{auth.role}</div>
          <button className="v-logout-btn" onClick={handleLogout}>Sign Out</button>
        </div>
      </nav>

      <main className="v-main">
        {children}
      </main>
    </div>
  );
}

export default RoleLayout;
