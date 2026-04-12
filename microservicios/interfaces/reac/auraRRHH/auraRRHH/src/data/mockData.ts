export type EmployeeState = 'ACTIVO' | 'EN_VACACIONES' | 'RETIRADO'

export type Employee = {
  id: string
  nombre: string
  apellido: string
  email: string
  cargo: string
  area: string
  estado: EmployeeState
}

export type VacationPeriod = {
  id: string
  empleado: string
  inicio: string
  fin: string
  estadoCuenta: 'Programada' | 'Desactivada' | 'Reactivada'
}

export type NotificationEvent = {
  id: string
  evento: string
  canal: 'Email' | 'InApp'
  destino: string
  estado: 'Enviado' | 'Pendiente' | 'Error'
  fecha: string
}

export const kpiCards = [
  { title: 'Empleados Activos', value: '142', delta: '+6 esta semana' },
  { title: 'Cuentas en Vacaciones', value: '11', delta: '3 inician hoy' },
  { title: 'Notificaciones Enviadas', value: '1,284', delta: '98.9% entrega' },
  { title: 'Incidentes Críticos', value: '0', delta: 'Uptime 99.97%' },
]

export const employees: Employee[] = [
  {
    id: 'EMP-1021',
    nombre: 'Lucia',
    apellido: 'Mendez',
    email: 'lucia.mendez@aurarrhh.com',
    cargo: 'Analista Senior',
    area: 'RRHH',
    estado: 'ACTIVO',
  },
  {
    id: 'EMP-1027',
    nombre: 'Daniel',
    apellido: 'Rivera',
    email: 'daniel.rivera@aurarrhh.com',
    cargo: 'Desarrollador Backend',
    area: 'Tecnologia',
    estado: 'EN_VACACIONES',
  },
  {
    id: 'EMP-1039',
    nombre: 'Mariana',
    apellido: 'Cortes',
    email: 'mariana.cortes@aurarrhh.com',
    cargo: 'Coordinadora de Talento',
    area: 'RRHH',
    estado: 'RETIRADO',
  },
]

export const vacationPeriods: VacationPeriod[] = [
  {
    id: 'VAC-3301',
    empleado: 'Daniel Rivera',
    inicio: '2026-04-15',
    fin: '2026-04-22',
    estadoCuenta: 'Programada',
  },
  {
    id: 'VAC-3302',
    empleado: 'Laura Parra',
    inicio: '2026-04-03',
    fin: '2026-04-10',
    estadoCuenta: 'Reactivada',
  },
]

export const notifications: NotificationEvent[] = [
  {
    id: 'NOT-890',
    evento: 'empleado.creado',
    canal: 'Email',
    destino: 'lucia.mendez@aurarrhh.com',
    estado: 'Enviado',
    fecha: '2026-04-11 08:12',
  },
  {
    id: 'NOT-891',
    evento: 'vacaciones.programadas',
    canal: 'Email',
    destino: 'daniel.rivera@aurarrhh.com',
    estado: 'Pendiente',
    fecha: '2026-04-11 09:41',
  },
  {
    id: 'NOT-892',
    evento: 'cuenta.desactivada',
    canal: 'InApp',
    destino: 'mariana.cortes@aurarrhh.com',
    estado: 'Error',
    fecha: '2026-04-11 10:09',
  },
]
