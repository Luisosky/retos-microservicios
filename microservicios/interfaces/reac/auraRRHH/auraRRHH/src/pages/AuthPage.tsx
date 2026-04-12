export function AuthPage() {
  return (
    <section className="page-grid two-col">
      <article className="panel">
        <h3>🔐 Autenticación y autorización</h3>
        <p style={{ marginTop: '12px', marginBottom: '16px' }}>
          Sistema seguro de autenticación basado en JWT. Todos los microservicios validan
          tokens para garantizar acceso seguro a los recursos.
        </p>
        <ul className="list-clean">
          <li><strong>POST /auth/login</strong> - Obtener token de acceso</li>
          <li><strong>POST /auth/change-password</strong> - Cambiar contraseña</li>
          <li><strong>POST /auth/recover-password</strong> - Recuperación de acceso</li>
          <li>Validación JWT en gateway y todos los microservicios</li>
          <li>Creación de usuarios solo mediante eventos (event-driven)</li>
          <li>Tokens con expiración configurable</li>
        </ul>
      </article>

      <article className="panel">
        <h3>Acceder a Aura</h3>
        <form className="form-grid" onSubmit={(event) => event.preventDefault()}>
          <label>
            Correo empresarial
            <input type="email" placeholder="nombre@aura.com" required />
          </label>
          <label>
            Contraseña
            <input type="password" placeholder="••••••••" required />
          </label>
          <label style={{ display: 'flex', gap: '8px', fontSize: '0.9rem', cursor: 'pointer' }}>
            <input type="checkbox" />
            Recordar mis datos
          </label>
          <button type="submit" className="primary-btn" style={{ marginTop: '8px' }}>
            Iniciar sesión
          </button>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)', textAlign: 'center' }}>
            ¿Olvidaste tu contraseña? <a href="#" style={{ color: 'var(--aura-primary)', textDecoration: 'none' }}>Recupera tu acceso</a>
          </p>
        </form>
      </article>
    </section>
  )
}
