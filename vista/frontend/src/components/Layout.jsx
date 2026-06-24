import { NavLink, useNavigate } from 'react-router-dom';
import { logout } from '../api/client';
import './Layout.css';

function Layout({ auth, onLogout, children }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // Ignore — token may already be invalid
    }
    onLogout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          <h1>VISTA</h1>
          <span className="sidebar-subtitle">Academic Monitor</span>
        </div>

        <ul className="sidebar-nav">
          <li>
            <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
              Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink to="/attendance" className={({ isActive }) => isActive ? 'active' : ''}>
              Attendance Log
            </NavLink>
          </li>
          <li>
            <NavLink to="/risk" className={({ isActive }) => isActive ? 'active' : ''}>
              Risk Flags
            </NavLink>
          </li>
          <li>
            <NavLink to="/enroll" className={({ isActive }) => isActive ? 'active' : ''}>
              Enrollment
            </NavLink>
          </li>
          <li>
            <NavLink to="/test" className={({ isActive }) => isActive ? 'active' : ''}>
              Test Recognition
            </NavLink>
          </li>
        </ul>

        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{auth.name}</span>
            <span className="user-role">{auth.role}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;
