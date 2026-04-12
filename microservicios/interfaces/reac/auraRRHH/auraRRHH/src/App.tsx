import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './layout/AppShell'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { EmployeesPage } from './pages/EmployeesPage'
import { GatewayPage } from './pages/GatewayPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { ObservabilityPage } from './pages/ObservabilityPage'
import { ProfilePage } from './pages/ProfilePage'
import { VacationsPage } from './pages/VacationsPage'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/empleados" element={<EmployeesPage />} />
        <Route path="/perfil" element={<ProfilePage />} />
        <Route path="/vacaciones" element={<VacationsPage />} />
        <Route path="/notificaciones" element={<NotificationsPage />} />
        <Route path="/gateway" element={<GatewayPage />} />
        <Route path="/observabilidad" element={<ObservabilityPage />} />
        <Route path="/home" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App
