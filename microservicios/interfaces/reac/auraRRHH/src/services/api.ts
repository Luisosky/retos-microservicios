import axios from 'axios'

const authClient = axios.create({ baseURL: 'http://localhost:8084' })
const empleadosClient = axios.create({ baseURL: 'http://localhost:8080' })
const perfilesClient = axios.create({ baseURL: 'http://localhost:8083' })

export function setAuthToken(token: string | null) {
  const header = token ? `Bearer ${token}` : null
  [authClient, empleadosClient, perfilesClient].forEach(c => {
    if (header) c.defaults.headers.common['Authorization'] = header
    else delete c.defaults.headers.common['Authorization']
  })
}

export default { authClient, empleadosClient, perfilesClient }
