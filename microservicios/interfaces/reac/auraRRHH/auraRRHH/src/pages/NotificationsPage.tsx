import { notifications } from '../data/mockData'

export function NotificationsPage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h3>🔔 Centro de notificaciones</h3>
        <p style={{ marginTop: '12px', marginBottom: '16px' }}>
          Monitor de eventos del sistema y administración de plantillas de comunicación.
          Todos los eventos generados por los microservicios se registran y procesan aquí.
        </p>
        <div style={{ marginTop: '16px', padding: '12px', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
          <strong style={{ fontSize: '0.9rem' }}>Tipos de eventos monitoreados:</strong>
          <p style={{ fontSize: '0.85rem', margin: '8px 0 0', color: 'var(--text-secondary)' }}>
            empleado.creado • empleado.actualizado • empleado.eliminado • vacaciones.programadas •
            cuenta.desactivada • cuenta.reactivada • usuario.recuperacion
          </p>
        </div>
      </article>

      <article className="panel">
        <h3 style={{ marginBottom: '16px' }}>Registro de eventos recientes</h3>
        {notifications.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>ID evento</th>
                <th>Evento</th>
                <th>Canal</th>
                <th>Destinatario</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {notifications.map((notification) => (
                <tr key={notification.id}>
                  <td style={{ fontWeight: '600', color: 'var(--aura-primary)' }}>{notification.id}</td>
                  <td style={{ fontWeight: '500' }}>{notification.evento}</td>
                  <td>
                    <span style={{
                      display: 'inline-block',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      backgroundColor: notification.canal === 'Email' ? '#fef3c7' : '#dbeafe',
                      color: notification.canal === 'Email' ? '#b45309' : '#3b82f6',
                      fontWeight: '600'
                    }}>
                      {notification.canal}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem' }}>{notification.destino}</td>
                  <td>
                    <span className={`status status--${notification.estado.toLowerCase()}`}>
                      {notification.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text-tertiary)' }}>No hay eventos registrados</p>
        )}
      </article>
    </section>
  )
}
