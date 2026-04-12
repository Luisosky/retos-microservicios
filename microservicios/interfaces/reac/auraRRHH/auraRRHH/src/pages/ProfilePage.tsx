export function ProfilePage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>👤 Mi perfil profesional</h3>
        <p style={{ marginTop: '12px', marginBottom: '16px' }}>
          Actualiza tu información personal y profesional. Los cambios se reflejan
          en toda la platform de manera inmediata.
        </p>
        <ul className="list-clean">
          <li>Información personal: nombre, teléfono, documento</li>
          <li>Ubicación: dirección completa y ciudad</li>
          <li>Datos profesionales: cargo, departamento y número de empleado</li>
          <li>Medio social: foto de perfil y biografía</li>
          <li>Contactos de emergencia y referencias</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Editar información</h3>
        <form className="form-grid" onSubmit={(event) => event.preventDefault()}>
          <label>
            Nombre completo *
            <input type="text" placeholder="Lucia Mendez" required />
          </label>
          <label>
            Teléfono personal
            <input type="tel" placeholder="+57 300 000 0000" />
          </label>
          <label>
            Dirección *
            <input type="text" placeholder="Calle 123 #45-67, Apto 501" required />
          </label>
          <label>
            Ciudad *
            <input type="text" placeholder="Bogotá" required />
          </label>
          <label>
            Biografía profesional
            <textarea placeholder="Cuéntanos sobre tu experiencia..." style={{ minHeight: '100px', fontFamily: 'inherit', lineHeight: '1.5' }} />
          </label>
          <button type="submit" className="primary-btn">Guardar cambios</button>
        </form>
      </article>
    </section>
  )
}
