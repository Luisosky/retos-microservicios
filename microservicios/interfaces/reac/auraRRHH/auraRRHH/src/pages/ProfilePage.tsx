export function ProfilePage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>Perfil personal del empleado</h3>
        <p>
          Espacio para que cada usuario autenticado gestione su informacion
          personal, profesional y de contacto.
        </p>
        <ul className="list-clean">
          <li>Nombre, apellido y telefono</li>
          <li>Direccion completa y ciudad</li>
          <li>Cargo, area y numero de empleado</li>
          <li>Biografia, foto y redes sociales</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Formulario mock de perfil</h3>
        <form className="form-grid" onSubmit={(event) => event.preventDefault()}>
          <label>
            Nombre completo
            <input type="text" placeholder="Lucia Mendez" />
          </label>
          <label>
            Telefono
            <input type="tel" placeholder="+57 300 000 0000" />
          </label>
          <label>
            Direccion
            <input type="text" placeholder="Calle 123 #45-67" />
          </label>
          <label>
            Ciudad
            <input type="text" placeholder="Bogota" />
          </label>
          <button type="submit" className="primary-btn">Guardar cambios</button>
        </form>
      </article>
    </section>
  )
}
