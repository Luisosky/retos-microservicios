import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import AuthPage from './pages/AuthPage'
import EmployeesPage from './pages/EmployeesPage'
import ProfilePage from './pages/ProfilePage'

export default function App() {
  return (
    <div>
      <nav>
        <Link to="/auth">Auth</Link> | <Link to="/employees">Employees</Link> | <Link to="/profile">Profile</Link>
      </nav>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/employees" element={<EmployeesPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/" element={<AuthPage />} />
      </Routes>
    </div>
  )
}
