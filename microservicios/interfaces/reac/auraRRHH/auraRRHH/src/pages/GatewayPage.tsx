export function GatewayPage() {
  const endpointGroups = {
    'Autenticación': [
      { method: 'POST', path: '/auth/login', desc: 'Obtener token de acceso' },
      { method: 'POST', path: '/auth/change-password', desc: 'Cambiar contraseña' },
      { method: 'POST', path: '/auth/recover-password', desc: 'Recuperar acceso' },
    ],
    'Empleados': [
      { method: 'GET', path: '/employees', desc: 'Listar todos' },
      { method: 'POST', path: '/employees', desc: 'Crear nuevo' },
      { method: 'GET', path: '/employees/{id}', desc: 'Obtener detalles' },
      { method: 'PUT', path: '/employees/{id}', desc: 'Actualizar' },
      { method: 'DELETE', path: '/employees/{id}', desc: 'Eliminar' },
    ],
    'Perfil': [
      { method: 'GET', path: '/profile', desc: 'Obtener mi perfil' },
      { method: 'PUT', path: '/profile', desc: 'Actualizar mi perfil' },
    ],
    'Vacaciones': [
      { method: 'POST', path: '/vacations', desc: 'Programar nuevo período' },
      { method: 'GET', path: '/vacations', desc: 'Listar en vigencia' },
    ],
  }

  return (
    <section className="page-grid">
      <article className="panel">
        <h3>🌐 API Gateway - Punto de entrada único</h3>
        <p style={{ marginTop: '12px', marginBottom: '16px' }}>
          El API Gateway actúa como punto de entrada único para todas las peticiones del cliente.
          Centraliza autenticación, enrutamiento, composición de respuestas y rate limiting.
        </p>
        <div style={{ marginTop: '16px', padding: '12px', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
          <strong style={{ fontSize: '0.9rem' }}>Características:</strong>
          <ul className="list-clean">
            <li>Validación de JWT en todas las peticiones</li>
            <li>Enrutamiento inteligente a microservicios</li>
            <li>Composición de datos (ej: empleado + perfil)</li>
            <li>Rate limiting y control de concurrencia</li>
            <li>Transformación de respuestas</li>
          </ul>
        </div>
      </article>

      {Object.entries(endpointGroups).map(([group, endpoints]) => (
        <article key={group} className="panel">
          <h4 style={{ marginBottom: '12px', color: 'var(--aura-primary)' }}>{group}</h4>
          <table className="table" style={{ marginTop: 0 }}>
            <thead>
              <tr>
                <th style={{ width: '60px' }}>Método</th>
                <th style={{ width: '200px' }}>Endpoint</th>
                <th>Descripción</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map((endpoint) => (
                <tr key={endpoint.path}>
                  <td>
                    <span style={{
                      display: 'inline-block',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: '700',
                      backgroundColor: endpoint.method === 'GET' ? '#dbeafe' : endpoint.method === 'POST' ? '#d1fae5' : '#fee2e2',
                      color: endpoint.method === 'GET' ? '#3b82f6' : endpoint.method === 'POST' ? '#10b981' : '#ef4444',
                    }}>
                      {endpoint.method}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--text-primary)' }}>{endpoint.path}</td>
                  <td style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{endpoint.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      ))}
    </section>
  )
}
