import { kpiCards, notifications } from '../data/mockData'

export function DashboardPage() {
  return (
    <section className="page-grid">
      <article className="panel panel--hero">
        <p className="panel-kicker">Bienvenido a Aura</p>
        <h3>Plataforma integral de gestión del ciclo de vida del empleado</h3>
        <p style={{ marginTop: '12px', fontSize: '0.95rem' }}>
          Gestiona el onboarding, autenticación, perfiles, vacaciones y offboarding de tu organización desde
          una única plataforma moderna y escalable.
        </p>
      </article>

      <div className="kpi-grid">
        {kpiCards.map((kpi) => (
          <article key={kpi.title} className="panel kpi-card">
            <p>{kpi.title}</p>
            <strong>{kpi.value}</strong>
            <span>{kpi.delta}</span>
          </article>
        ))}
      </div>

      <article className="panel">
        <h3>Flujo operativo de la plataforma</h3>
        <ul className="list-clean">
          <li>1. RRHH crea nuevo empleado en el sistema de gestión</li>
          <li>2. Evento disparado: se crean credenciales automáticamente</li>
          <li>3. Notificación por correo con instrucciones de acceso</li>
          <li>4. Empleado inicia sesión y actualiza su perfil personal</li>
          <li>5. RRHH programa vacaciones: cuenta se desactiva automáticamente</li>
          <li>6. Al finalizar vacaciones: cuenta se reactiva</li>
          <li>7. Offboarding: desactivación permanente y auditoría registrada</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Actividad reciente del sistema</h3>
        {notifications.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>ID evento</th>
                <th>Tipo de evento</th>
                <th>Estado</th>
                <th>Fecha y hora</th>
              </tr>
            </thead>
            <tbody>
              {notifications.slice(0, 5).map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: '500' }}>
                    {item.evento}
                  </td>
                  <td>
                    <span className={`status status--${item.estado.toLowerCase()}`}>
                      {item.estado}
                    </span>
                  </td>
                  <td>{item.fecha}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ marginTop: '12px', color: 'var(--text-tertiary)' }}>
            No hay eventos registrados en este momento
          </p>
        )}
      </article>
    </section>
  )
}
