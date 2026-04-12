import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Resumen Ejecutivo' },
  { to: '/auth', label: 'Autenticacion' },
  { to: '/empleados', label: 'Empleados' },
  { to: '/perfil', label: 'Perfiles' },
  { to: '/vacaciones', label: 'Vacaciones' },
  { to: '/notificaciones', label: 'Notificaciones' },
  { to: '/gateway', label: 'API Gateway' },
  { to: '/observabilidad', label: 'Observabilidad' },
]

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <p className="brand-eyebrow">Plataforma RRHH</p>
          <h1>AuraRRHH</h1>
          <p className="brand-caption">Arquitectura orientada a microservicios</p>
        </div>

        <nav className="main-nav" aria-label="Navegacion principal">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? 'nav-link nav-link--active' : 'nav-link'
              }
              end={item.to === '/'}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-note">
          <p>Estado del entorno</p>
          <strong>Demo UI sin integracion API</strong>
        </div>
      </aside>

      <main className="content-area">
        <header className="topbar">
          <div>
            <p className="topbar-label">Proyecto Final</p>
            <h2>Gestion integral del ciclo de vida del empleado</h2>
          </div>
          <button className="primary-btn" type="button">
            Conectar microservicios
          </button>
        </header>

        <Outlet />
      </main>
    </div>
  )
}
