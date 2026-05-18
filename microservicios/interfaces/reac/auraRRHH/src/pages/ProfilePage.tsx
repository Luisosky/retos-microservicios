import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function ProfilePage() {
  const [profiles, setProfiles] = useState<any[]>([])

  useEffect(() => {
    api.perfilesClient.get('/api/perfiles')
      .then(r => setProfiles(r.data || []))
      .catch(() => setProfiles([]))
  }, [])

  return (
    <div>
      <h2>Profiles</h2>
      <ul>
        {profiles.map((p, i) => (<li key={i}>{p.nombre || p.name || JSON.stringify(p)}</li>))}
      </ul>
    </div>
  )
}
