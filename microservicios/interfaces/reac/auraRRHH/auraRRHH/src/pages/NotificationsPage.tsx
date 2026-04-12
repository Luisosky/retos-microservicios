import { notifications } from '../data/mockData'

export function NotificationsPage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h3>Centro de Notificaciones</h3>
        <p>
          Vista diseniada para consumir eventos del sistema y administrar
          plantillas de correo/in-app por tipo de evento.
        </p>
      </article>

      <article className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Evento</th>
              <th>Canal</th>
              <th>Destino</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {notifications.map((notification) => (
              <tr key={notification.id}>
                <td>{notification.id}</td>
                <td>{notification.evento}</td>
                <td>{notification.canal}</td>
                <td>{notification.destino}</td>
                <td>
                  <span className={`status status--${notification.estado.toLowerCase()}`}>
                    {notification.estado}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  )
}
