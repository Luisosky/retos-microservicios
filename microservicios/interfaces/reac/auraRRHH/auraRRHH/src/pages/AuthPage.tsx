export function AuthPage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>Autenticacion y autorizacion</h3>
        <p>
          Este modulo debe consumir unicamente endpoints de login, cambio de
          contrasena y validacion de token desde el gateway.
        </p>
        <ul className="list-clean">
          <li>POST /auth/login</li>
          <li>POST /auth/change-password</li>
          <li>Validacion JWT en gateway y microservicios</li>
          <li>Registro de usuario solo por eventos internos</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Formulario mock de acceso</h3>
        <form className="form-grid" onSubmit={(event) => event.preventDefault()}>
          <label>
            Usuario
            <input type="text" placeholder="usuario@empresa.com" />
          </label>
          <label>
            Contrasena
            <input type="password" placeholder="********" />
          </label>
          <button type="submit" className="primary-btn">
            Iniciar sesion
          </button>
        </form>
      </article>
    </section>
  )
}
