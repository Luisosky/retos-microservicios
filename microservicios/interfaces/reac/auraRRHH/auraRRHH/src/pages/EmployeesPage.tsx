import { employees } from '../data/mockData'

export function EmployeesPage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3>👥 Directorio de empleados</h3>
            <p style={{ marginTop: '8px', fontSize: '0.9rem' }}>
              Gestión completa del ciclo de vida de los colaboradores: onboarding, actualización de datos y offboarding.
            </p>
          </div>
          <button className="primary-btn">+ Agregar empleado</button>
        </div>
      </article>

      <article className="panel">
        {employees.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>ID empleado</th>
                <th>Nombre completo</th>
                <th>Correo corporativo</th>
                <th>Posición</th>
                <th>Departamento</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr key={employee.id} style={{ cursor: 'pointer' }} title="Haz clic para ver detalles">
                  <td style={{ fontWeight: '600', color: 'var(--aura-primary)' }}>{employee.id}</td>
                  <td style={{ fontWeight: '500' }}>{employee.nombre} {employee.apellido}</td>
                  <td>{employee.email}</td>
                  <td>{employee.cargo}</td>
                  <td>{employee.area}</td>
                  <td>
                    <span className={`status status--${employee.estado.toLowerCase()}`}>
                      {employee.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text-tertiary)' }}>No hay empleados registrados</p>
        )}
      </article>
    </section>
  )
}
