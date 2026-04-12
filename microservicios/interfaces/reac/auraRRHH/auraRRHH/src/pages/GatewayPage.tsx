export function GatewayPage() {
  const endpoints = [
    'POST /auth/login',
    'POST /auth/change-password',
    'GET /employees',
    'POST /employees',
    'GET /employees/{id}',
    'PUT /employees/{id}',
    'DELETE /employees/{id}',
    'GET /profile',
    'PUT /profile',
    'POST /vacations',
    'GET /vacations',
  ]

  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>API Gateway</h3>
        <p>
          Este modulo representa el punto de entrada unico del cliente.
          Centraliza autenticacion, enrutamiento y composicion de respuestas.
        </p>
      </article>

      <article className="panel">
        <h3>Operaciones expuestas al frontend</h3>
        <ul className="list-clean">
          {endpoints.map((endpoint) => (
            <li key={endpoint}>{endpoint}</li>
          ))}
        </ul>
      </article>
    </section>
  )
}
