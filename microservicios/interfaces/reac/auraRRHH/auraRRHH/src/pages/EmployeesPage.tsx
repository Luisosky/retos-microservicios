import { employees } from '../data/mockData'

export function EmployeesPage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h3>Gestion de Empleados</h3>
        <p>
          Vista preparada para CRUD de empleados y publicacion de eventos de
          dominio: creado, actualizado y eliminado.
        </p>
      </article>

      <article className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Cargo</th>
              <th>Area</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((employee) => (
              <tr key={employee.id}>
                <td>{employee.id}</td>
                <td>{employee.nombre} {employee.apellido}</td>
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
      </article>
    </section>
  )
}
