import React, { useState } from 'react'
import api, { setAuthToken } from '../services/api'

export default function AuthPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [info, setInfo] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.authClient.post('/auth/login', { email, password })
      const token = res.data?.token || res.data
      setAuthToken(token)
      localStorage.setItem('token', token)
      const payload = token.split('.')[1]
      const json = JSON.parse(atob(payload))
      setInfo(`Logged as ${json.role || json.roles || 'unknown'}`)
    } catch (err: any) {
      setInfo('Login failed')
    }
  }

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div>
          <input value={email} onChange={e => setEmail(e.target.value)} placeholder="email" />
        </div>
        <div>
          <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="password" />
        </div>
        <button type="submit">Login</button>
      </form>
      <div>{info}</div>
    </div>
  )
}
