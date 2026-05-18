# Plan de Implementación: Desarrollo e Integración de Aura RRHH

Este plan detalla el diseño técnico y el flujo de trabajo para consolidar, dockerizar, integrar y automatizar el frontend unificado de **Aura RRHH** (`aura.rrhh`) en el ecosistema actual de microservicios.

## User Review Required

> [!IMPORTANT]
> **Plan Actualizado según tus comentarios:**
> 1. **Independencia del Frontend (Sin Reverse Proxy):** Nginx se utilizará **únicamente** para servir los archivos estáticos de React. El frontend realizará las peticiones directamente a los puertos expuestos de cada microservicio en el host (`8084` para autenticación, `8080` para empleados, `8083` para perfiles). Así garantizamos que si el frontend se cae, no afecte en absoluto la operatividad y enrutamiento del backend.
> 2. **Gestión de Roles Visibles:** Dado que el backend ya controla de forma segura qué puede modificar cada rol, el frontend simplemente leerá el rol del JWT decodificado para adaptar la interfaz visualmente (ej. mostrando los botones de editar/agregar global solo a `ADMIN` o Recursos Humanos, y dejando a los empleados regulares solo con acceso de lectura/edición propia).

---

## Proposed Changes

### [Consolidación y Estructura del Frontend]

Consolidación de la aplicación en TypeScript, eliminando la duplicación en JavaScript y moviendo los archivos fuente a una estructura limpia.

#### [NEW] [Dockerfile](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/Dockerfile)
Creación de la configuración de compilación de Docker multi-etapa utilizando Node 20 para el build y Nginx para servir los assets estáticos.

#### [NEW] [nginx.conf](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/nginx.conf)
Configuración básica de Nginx dedicada exclusivamente a servir los archivos estáticos de React y manejar el enrutamiento del cliente (fallback a `index.html`). No interferirá con el tráfico de la API.

#### [NEW] [Jenkinsfile](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/Jenkinsfile)
Creación del pipeline CI/CD declarativo para el frontend en Jenkins, integrando pruebas, análisis en SonarQube y despliegue del contenedor.

---

### [Configuración y Orquestación global]

#### [MODIFY] [docker-compose.yml](file:///d:/univercidad/micro%20servicios/microservicios/docker-compose.yml)
Integración del servicio `frontend-service` (Aura RRHH) con sus puertos expuestos (ej. `3001:80`). Completamente aislado y desacoplado del backend.

#### [MODIFY] [casc.yaml](file:///d:/univercidad/micro%20servicios/microservicios/Jenkins/casc.yaml)
Adición del Job DSL para automatizar la creación del pipeline de CI/CD para el frontend de Aura RRHH en Jenkins.

---

### [Lógica y Conexión de API en React]

#### [MODIFY] [api.ts](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/src/services/api.ts) [NEW]
Creación de clientes HTTP (Axios o Fetch) configurados para apuntar directamente a las URLs absolutas de cada microservicio (`http://localhost:8084`, `http://localhost:8080`, etc.), inyectando automáticamente el token JWT Bearer. Se gestionarán políticas de CORS en los backends si fuera necesario.

#### [MODIFY] [AuthPage.tsx](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/src/pages/AuthPage.tsx)
Conexión con el endpoint `/auth/login` en el puerto 8084, guardando el token y obteniendo el rol del usuario.

#### [MODIFY] [EmployeesPage.tsx](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/src/pages/EmployeesPage.tsx)
Sustitución de los mocks por llamadas directas al puerto 8080 (`/empleado`). Se ocultarán condicionalmente los botones de administración para usuarios con rol `USER`.

#### [MODIFY] [ProfilePage.tsx](file:///d:/univercidad/micro%20servicios/microservicios/interfaces/reac/auraRRHH/src/pages/ProfilePage.tsx)
Carga y actualización de perfiles conectándose directamente al servicio de Perfiles en el puerto 8083.

---

## Verification Plan

### Automated Tests
- **Jenkins CI Build Pipeline:** Ejecutar el pipeline de Jenkins para verificar la correcta compilación y análisis SonarQube del código fuente unificado.

### Manual Verification
1. **Control de Accesos (Roles):**
   - Iniciar sesión como `ADMIN` o `HR`: Verificar que los botones de modificar y agregar empleados globales estén visibles.
   - Iniciar sesión como `USER`: Verificar que dichos botones estén ocultos en la UI y que solo pueda interactuar con sus propios datos.
2. **Independencia del Frontend:**
   - Detener el contenedor del frontend (`docker stop aura-rrhh-frontend`).
   - Verificar usando Postman que las llamadas directas a los microservicios en sus puertos (8084, 8080, etc.) siguen respondiendo al 100%, garantizando el aislamiento total solicitado.
3. **Observabilidad:**
   - Confirmar en Loki/Grafana que los logs estáticos del frontend se están capturando sin acoplar la arquitectura de los microservicios.
