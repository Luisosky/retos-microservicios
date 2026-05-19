import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function EmployeesPage() {
  const [emps, setEmps] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.empleadosClient.get('/empleado')
      .then(r => setEmps(r.data || []))
      .catch(e => setError('Failed to load employees'))
  }, [])

  return (
    <div>
      <h2>Employees</h2>
      {error && <div>{error}</div>}
      <ul>
        {emps.map((e, i) => (<li key={i}>{e.nombre || e.name || JSON.stringify(e)}</li>))}
      </ul>
    </div>
  )
}
