import { kpiCards, notifications } from '../data/mockData'

export function DashboardPage() {
  return (
    <section className="page-grid">
      <article className="panel panel--hero">
        <p className="panel-kicker">Vision General</p>
        <h3>Operacion de RRHH centralizada y trazable</h3>
        <p>
          Esta interfaz conecta onboarding, autenticacion, perfiles, vacaciones,
          offboarding y observabilidad bajo una sola experiencia operativa.
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
        <h3>Flujo operativo objetivo</h3>
        <ul className="list-clean">
          <li>1. RRHH crea empleado en Gestion de Empleados.</li>
          <li>2. Evento empleado.creado crea credenciales automaticamente.</li>
          <li>3. Notificaciones envian correo de acceso y activacion.</li>
          <li>4. Empleado ingresa y mantiene su perfil actualizado.</li>
          <li>5. Vacaciones activan y desactivan cuenta por fechas.</li>
          <li>6. Offboarding desactiva acceso y deja auditoria.</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Ultimos eventos de notificacion</h3>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Evento</th>
              <th>Estado</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {notifications.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.evento}</td>
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
      </article>
    </section>
  )
}
