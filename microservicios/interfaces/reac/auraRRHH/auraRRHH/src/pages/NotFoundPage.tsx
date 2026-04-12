import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h3>Vista no encontrada</h3>
        <p>La ruta solicitada no existe en la interfaz de AuraRRHH.</p>
        <Link className="primary-btn inline-btn" to="/">
          Volver al resumen
        </Link>
      </article>
    </section>
  )
}
