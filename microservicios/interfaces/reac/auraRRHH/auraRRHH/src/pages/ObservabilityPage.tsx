export function ObservabilityPage() {
  const metrics = [
    { name: 'Auth Service', status: 'healthy', uptime: '99.97%', latency: '45ms' },
    { name: 'Empleados Service', status: 'healthy', uptime: '99.95%', latency: '78ms' },
    { name: 'Departamentos Service', status: 'healthy', uptime: '99.98%', latency: '52ms' },
    { name: 'Notificaciones Service', status: 'healthy', uptime: '99.92%', latency: '120ms' },
    { name: 'Perfiles Service', status: 'healthy', uptime: '99.93%', latency: '95ms' },
  ]

  const sampleLog = `{
  "timestamp": "2026-04-11T18:21:00.123Z",
  "level": "INFO",
  "service": "autenticacion",
  "correlation_id": "req-5a7d2c9f",
  "message": "Token validado exitosamente",
  "context": {
    "employee_id": "EMP-1021",
    "route": "/auth/login",
    "ip_address": "192.168.1.100",
    "response_time_ms": 45
  }
}`

  return (
    <section className="page-grid">
      <article className="panel">
        <h3>🔍 Observabilidad del sistema</h3>
        <p style={{ marginTop: '12px', marginBottom: '16px' }}>
          Monitoreo completo de todos los microservicios, incluyendo logs centralizados,
          métricas de rendimiento y alertas automáticas ante anomalías.
        </p>
      </article>

      <article className="panel">
        <h3>Salud de microservicios</h3>
        {metrics.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Servicio</th>
                <th>Estado</th>
                <th>Disponibilidad</th>
                <th>Latencia promedio</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric) => (
                <tr key={metric.name}>
                  <td style={{ fontWeight: '500' }}>{metric.name}</td>
                  <td>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '0.9rem',
                    }}>
                      <span style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: metric.status === 'healthy' ? 'var(--success)' : 'var(--warning)',
                        display: 'inline-block',
                      }} />
                      {metric.status === 'healthy' ? 'En línea' : 'Advertencia'}
                    </span>
                  </td>
                  <td style={{ fontWeight: '600' }}>{metric.uptime}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{metric.latency}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </article>

      <article className="panel">
        <h3>📊 Logs centralizados</h3>
        <p style={{ fontSize: '0.9rem', marginBottom: '12px' }}>
          Todos los microservicios envían logs estructurados a un sistema centralizado.
          Búsqueda rápida por servicio, severidad, correlation ID y contexto técnico.
        </p>
        <div className="code-block" style={{ marginTop: '12px' }}>
          <pre>{sampleLog}</pre>
        </div>
      </article>

      <article className="panel">
        <h3>⚠️ Alertas configuradas</h3>
        <ul className="list-clean">
          <li><strong>Error crítico:</strong> Se dispara si algún servicio cae (status 500+)</li>
          <li><strong>Latencia alta:</strong> Alerta si respuesta tarda mayor a 500ms</li>
          <li><strong>Tasa de error:</strong> Notificación si errores superan 5% por minuto</li>
          <li><strong>Disponibilidad:</strong> Alerta si uptime cae bajo 99.5%</li>
          <li><strong>Cuota de API:</strong> Notificación si se alcanza 80% del límite</li>
        </ul>
      </article>
    </section>
  )
}
