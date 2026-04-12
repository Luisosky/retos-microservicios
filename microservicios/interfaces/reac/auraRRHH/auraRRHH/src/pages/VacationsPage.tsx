import { vacationPeriods } from '../data/mockData'

export function VacationsPage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>Gestion de Vacaciones</h3>
        <p>
          Flujo preparado para programacion de vacaciones y sincronizacion de
          activacion/desactivacion de cuentas por fechas.
        </p>
        <ul className="list-clean">
          <li>Validacion de solapamientos</li>
          <li>Control de dias disponibles</li>
          <li>Eventos para auth y notificaciones</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Periodos programados</h3>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Empleado</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Cuenta</th>
            </tr>
          </thead>
          <tbody>
            {vacationPeriods.map((vacation) => (
              <tr key={vacation.id}>
                <td>{vacation.id}</td>
                <td>{vacation.empleado}</td>
                <td>{vacation.inicio}</td>
                <td>{vacation.fin}</td>
                <td>{vacation.estadoCuenta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  )
}
