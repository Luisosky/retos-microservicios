import { vacationPeriods } from '../data/mockData'

export function VacationsPage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>🏖️ Gestión de vacaciones</h3>
        <p style={{ marginTop: '12px', marginBottom: '16px' }}>
          Programa y monitorea períodos de descanso. Las cuentas se desactivan y reactivan
          automáticamente según las fechas configuradas. RRHH recibe notificaciones para
          seguimiento.
        </p>
        <ul className="list-clean">
          <li>Validación contra solapamiento de períodos</li>
          <li>Control automático de días disponibles</li>
          <li>Desactivación y reactivación de cuentas</li>
          <li>Notificaciones automáticas a empleados</li>
          <li>Auditoría completa de cambios</li>
        </ul>
      </article>

      <article className="panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0 }}>Períodos programados</h3>
          <button className="primary-btn">+ Programar vacaciones</button>
        </div>
        {vacationPeriods.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>ID período</th>
                <th>Empleado</th>
                <th>Fecha inicio</th>
                <th>Fecha fin</th>
                <th>Estado de cuenta</th>
              </tr>
            </thead>
            <tbody>
              {vacationPeriods.map((vacation) => (
                <tr key={vacation.id}>
                  <td style={{ fontWeight: '600', color: 'var(--aura-primary)' }}>{vacation.id}</td>
                  <td style={{ fontWeight: '500' }}>{vacation.empleado}</td>
                  <td>{vacation.inicio}</td>
                  <td>{vacation.fin}</td>
                  <td>
                    <span className={`status status--${vacation.estadoCuenta.toLowerCase().replace(' ', '_')}`}>
                      {vacation.estadoCuenta}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text-tertiary)' }}>No hay períodos de vacaciones programados</p>
        )}
      </article>
    </section>
  )
}
