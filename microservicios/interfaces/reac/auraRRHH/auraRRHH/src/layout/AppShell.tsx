import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/auth', label: 'Autenticación', icon: '🔐' },
  { to: '/empleados', label: 'Empleados', icon: '👥' },
  { to: '/perfil', label: 'Mi Perfil', icon: '👤' },
  { to: '/vacaciones', label: 'Vacaciones', icon: '🏖️' },
  { to: '/notificaciones', label: 'Notificaciones', icon: '🔔' },
  { to: '/gateway', label: 'API Gateway', icon: '🌐' },
  { to: '/observabilidad', label: 'Observabilidad', icon: '🔍' },
]

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <p className="brand-eyebrow">Plataforma de RRHH</p>
          <h1>Aura</h1>
          <p className="brand-caption">Gestión integral de ciclo de vida del empleado</p>
        </div>

        <nav className="main-nav" aria-label="Navegación principal">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? 'nav-link nav-link--active' : 'nav-link'
              }
              end={item.to === '/'}
              title={item.label}
            >
              <span style={{ marginRight: '8px', fontSize: '1.1em' }}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-note">
          <p>Entorno</p>
          <strong>Demo UI</strong>
        </div>
      </aside>

      <main className="content-area">
        <header className="topbar">
          <div>
            <p className="topbar-label">Plataforma Aura</p>
            <h2>Gestión de recursos humanos moderna</h2>
          </div>
          <button className="primary-btn" type="button">
            Mis configuraciones
          </button>
        </header>

        <Outlet />
      </main>
    </div>
  )
}
