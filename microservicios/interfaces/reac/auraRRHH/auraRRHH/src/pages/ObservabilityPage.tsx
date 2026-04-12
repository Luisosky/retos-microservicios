export function ObservabilityPage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>Logs centralizados</h3>
        <p>
          Preparado para integrar ELK, Loki o Graylog con busqueda por servicio,
          severidad, correlation id y contexto tecnico.
        </p>
        <div className="code-block">
          <pre>
{`{
  "timestamp": "2026-04-11T18:21:00Z",
  "level": "INFO",
  "service": "autenticacion",
  "message": "token validated",
  "context": {
    "employeeId": "EMP-1021",
    "route": "/auth/login"
  }
}`}
          </pre>
        </div>
      </article>

      <article className="panel">
        <h3>Monitoreo y alertas</h3>
        <ul className="list-clean">
          <li>Salud por microservicio (up/down).</li>
          <li>Latencia por endpoint y tasa de errores.</li>
          <li>Metricas de negocio: empleados, vacaciones, notificaciones.</li>
          <li>Alertas de error critico y degradacion de rendimiento.</li>
        </ul>
      </article>
    </section>
  )
}
